# Gies enrollment from DMI's published fall reports. DMI's site now redirects to DAIR's Tableau
# dashboard, so Fall 2012 to Fall 2025 come from the Internet Archive's copies of the original
# pages, pinned to the captures listed in config/dmi_pages.csv.

import csv
import logging
import sys

import pandas as pd
from lxml import html

from ingest.http import new_session
from ingest.paths import CONFIG, EXTRACTS, RAW
from ingest.sources import download, update_manifest

log = logging.getLogger("dmi")

COLLEGE_CODE = "KM"
COLLEGE_NAMES = {"Business", "Gies Business"}
CLASS_KEYS = ["College Code", "Dept", "Degr", "Major Code", "Major Name", "Conc Code"]
STUDENT_TYPES = [
    "First time Freshman",
    "New Transfer",
    "Readmit & Returning",
    "Continuing & Nondegree",
    "Total",
]
CLASS_LEVELS = ["Fresh", "Soph", "Junior", "Senior", "ND", "Total"]
OUT = EXTRACTS / "dmi"


def read_pages():
    with (CONFIG / "dmi_pages.csv").open(newline="") as f:
        return list(csv.DictReader(f))


def archive_url(page):
    # The id_ form returns the page as originally served, without the archive's banner.
    return f"https://web.archive.org/web/{page['capture']}id_/{page['original_url']}"


def table_rows(table):
    return [[" ".join(c.text_content().split()) for c in tr.xpath("./td|./th")] for tr in table]


def parse_class_report(content):
    tables = [
        t
        for t in html.fromstring(content).xpath("//table")
        if t.xpath(f".//td[normalize-space()='{COLLEGE_CODE}']")
    ]
    assert len(tables) == 1, f"expected one table for college {COLLEGE_CODE}, found {len(tables)}"
    rows = table_rows(tables[0].xpath(".//tr"))
    header = next(r for r in rows if "Dept" in r)
    # The first header cell is blank in the source; it holds the college code.
    header = ["College Code"] + header[1:]
    assert header[: len(CLASS_KEYS)] == CLASS_KEYS, f"unexpected header {header[:7]}"
    curricula = [
        dict(zip(header, r, strict=True))
        for r in rows
        if len(r) == len(header) and r[0] == COLLEGE_CODE and r[3]
    ]
    totals = [r for r in rows if any("College total" in cell for cell in r)]
    assert len(totals) == 1, f"expected one college total row, found {len(totals)}"
    college_total = int(totals[0][header.index("TOTAL STUDENTS")])
    summed = sum(int(r["TOTAL STUDENTS"]) for r in curricula)
    assert summed == college_total, f"curricula sum to {summed}, college total is {college_total}"
    return curricula


def parse_abstract(content):
    rows = [
        r for t in html.fromstring(content).xpath("//table") for r in table_rows(t.xpath(".//tr"))
    ]
    starts = [
        (i, j) for i, r in enumerate(rows) for j, cell in enumerate(r) if cell in COLLEGE_NAMES
    ]
    assert len(starts) == 1, f"expected one Business block, found {starts}"
    i, j = starts[0]
    block = rows[i + 1 : i + 1 + len(STUDENT_TYPES)]
    labels = [r[j] for r in block]
    assert labels == STUDENT_TYPES, f"unexpected student types {labels}"
    return [
        {"Student Type": r[j]}
        | dict(zip(CLASS_LEVELS, r[j + 1 : j + 1 + len(CLASS_LEVELS)], strict=True))
        for r in block
    ]


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    session = new_session()
    manifest_rows, curricula, student_types = [], [], []
    for page in read_pages():
        name = page["original_url"].rsplit("/", 1)[-1]
        dest = RAW / "dmi" / name
        manifest_rows.append(
            download(session, archive_url(page), dest, f"dmi/{name}") | {"file_used": name}
        )
        tags = {"fall": page["fall"], "capture": page["capture"]}
        if page["report"] == "class":
            rows = parse_class_report(dest.read_bytes())
            curricula += [tags | r for r in rows]
            log.info("%s class report: %d curriculum rows", page["fall"], len(rows))
        else:
            rows = parse_abstract(dest.read_bytes())
            student_types += [tags | r for r in rows]
            log.info("%s abstract: %d student type rows", page["fall"], len(rows))
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(curricula).to_parquet(OUT / "enrollment_by_curriculum.parquet", index=False)
    pd.DataFrame(student_types).to_parquet(OUT / "student_type.parquet", index=False)
    update_manifest(manifest_rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
