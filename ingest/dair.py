# DAIR dashboard crosstabs, downloaded by hand into data/manual/dair/ (steps in
# docs/runbook.md). Tableau exports them as UTF-16, tab-separated, with headers spread over
# one or two rows; each is read into a long table that keeps the dashboard's own labels.

import csv
import hashlib
import io
import logging
import sys
from datetime import UTC, datetime

import pandas as pd

from ingest.paths import EXTRACTS, ROOT
from ingest.sources import update_manifest

log = logging.getLogger("dair")

MANUAL = ROOT / "data" / "manual" / "dair"
OUT = EXTRACTS / "dair"
STATISTICAL_ABSTRACT = "https://dair.illinois.edu/access-data/statistical-abstract/"
STUDENT_ENROLLMENT = "https://dair.illinois.edu/access-data/student-enrollment/"
RETENTION = "https://dair.illinois.edu/access-data/retention-and-graduation-rates/"
CURRICULUM_KEYS = [
    "Term Code",
    "College Code",
    "College",
    "Dept Code",
    "Department",
    "Major Code",
    "Major Name",
    "Conc Code",
    "Concentration Name",
    "Academic Program Code",
]


def read_crosstab(path):
    text = path.read_bytes().decode("utf-16")
    return list(csv.reader(io.StringIO(text), delimiter="\t"))


def parse_curriculum(rows):
    # The Data Table - Curriculum and Level sheet exports either long (Measure Names and
    # Measure Values columns) or wide (one column per level), depending on the sheet chosen.
    header = rows[0]
    assert header[: len(CURRICULUM_KEYS)] == CURRICULUM_KEYS, f"unexpected header {header[:10]}"
    records = [dict(zip(header, r, strict=True)) for r in rows[1:]]
    if "Measure Names" in header:
        return records
    measures = [h for h in header if h not in CURRICULUM_KEYS + ["Term Display"]]
    # The wide export ends with a college total and a campus total; filtered to one college,
    # both should equal the sum of its curricula.
    totals = [r for r in records if r["College"] == "College Total"]
    curricula = [r for r in records if r["College"] != "College Total"]
    assert totals, "no College Total row in the wide export"
    for measure in measures:
        summed = sum(int(r[measure].replace(",", "") or 0) for r in curricula)
        for total in totals:
            stated = int(total[measure].replace(",", "") or 0)
            assert summed == stated, f"{measure!r}: curricula sum to {summed}, total is {stated}"
    return [
        {k: r[k] for k in CURRICULUM_KEYS}
        | {"Measure Names": m, "Term Display": r["Term Display"], "Measure Values": r[m]}
        for r in curricula
        for m in measures
    ]


def parse_class_type(rows):
    # Two header rows: the semester, then the class. Rows named Total are dropped.
    semesters, classes = rows[0], rows[1]
    records = []
    for r in rows[2:]:
        if r[1] == "Total" or r[0] == "Grand Total":
            continue
        for i in range(3, len(r)):
            records.append(
                {
                    "College": r[1],
                    "Student Type": r[2],
                    "Semester": semesters[i],
                    "Class": classes[i],
                    "Count": r[i],
                }
            )
    return records


def parse_online(rows):
    # Two header rows: the term over the level columns, then the column names. The export
    # repeats Major as a seventh column; rows whose program code is Total are subtotals.
    terms, header = rows[0], rows[1]
    keys = ["College", "Department", "Degree", "Major", "Concentration", "Academic Program Code"]
    assert header[: len(keys)] == keys, f"unexpected header {header}"
    return [
        dict(zip(keys, r[: len(keys)], strict=True))
        | {"Term": terms[i], "Level": header[i], "Count": r[i]}
        for r in rows[2:]
        if r[5] != "Total"
        for i in range(7, len(r))
    ]


def parse_retention(rows):
    # Two header rows: the college at entry, then the cohort; one row per measure.
    colleges, cohorts = rows[0], rows[1]
    return [
        {"Entry College": colleges[i], "Fall Cohort": cohorts[i], "Measure": r[0], "Value": r[i]}
        for r in rows[2:]
        for i in range(1, len(r))
    ]


def parse_graduation(rows):
    # The measure label "Size of Adjusted Cohort" appears twice in this export. Labels are kept
    # exactly as exported; docs/data_notes.md says which one carries the cohort size.
    header = rows[0]
    return [
        {
            "College At Entry": r[0],
            "Graduation Year Group": r[1],
            "Measure": r[2],
            "Fall Cohort": header[i],
            "Value": r[i],
        }
        for r in rows[1:]
        for i in range(3, len(r))
    ]


FILES = {
    "curriculum_level": (parse_curriculum, STATISTICAL_ABSTRACT),
    "college_class_type": (parse_class_type, STATISTICAL_ABSTRACT),
    "online_programs": (parse_online, STUDENT_ENROLLMENT),
    "retention_by_entry_college": (parse_retention, RETENTION),
    "graduation_by_entry_college": (parse_graduation, RETENTION),
}


def manifest_row(path, url):
    content = path.read_bytes()
    downloaded = datetime.fromtimestamp(path.stat().st_mtime, UTC)
    return {
        "source": f"dair/{path.name}",
        "url": url,
        "retrieved_utc": downloaded.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_modified": "",
        "etag": "",
        "bytes": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
        "file_used": path.name,
    }


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    OUT.mkdir(parents=True, exist_ok=True)
    manifest_rows = []
    for stem, (parse, url) in FILES.items():
        paths = sorted(MANUAL.glob(f"{stem}*.csv"))
        assert paths, f"no {stem} files in {MANUAL.relative_to(ROOT)}"
        records = []
        for path in paths:
            parsed = parse(read_crosstab(path))
            records += [{"file": path.name} | r for r in parsed]
            manifest_rows.append(manifest_row(path, url))
            log.info("%s: %d rows", path.name, len(parsed))
        pd.DataFrame(records).to_parquet(OUT / f"{stem}.parquet", index=False)
    update_manifest(manifest_rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
