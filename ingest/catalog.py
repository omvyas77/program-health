# Sections offered, from the course catalog files in wadefagen/datasets: one file per term from
# 2016-fa to 2026-fa. Only Gies subjects are kept, and the instructor column is dropped.

import csv
import logging
import sys

from ingest.http import new_session
from ingest.paths import CONFIG, EXTRACTS, RAW
from ingest.sources import (
    WADEFAGEN_REPO,
    download,
    github_head,
    read_text_csv,
    update_manifest,
    wadefagen_url,
)

log = logging.getLogger("catalog")

# There is no 2016-sp, 2016-su, 2016-wi, or 2017-wi file.
TERMS = ["2016-fa", "2017-sp", "2017-su", "2017-fa"] + [
    f"{year}-{term}" for year in range(2018, 2027) for term in ("wi", "sp", "su", "fa")
]
KEEP = [
    "Year",
    "Term",
    "YearTerm",
    "Subject",
    "Number",
    "Name",
    "Credit Hours",
    "CRN",
    "Section",
    "Type",
    "Type Code",
    "Part of Term",
    "Section Status",
    "Enrollment Status",
]
OUT = EXTRACTS / "catalog"


def read_subjects():
    with (CONFIG / "gies_subjects.csv").open(newline="") as f:
        return {row["subject"] for row in csv.DictReader(f)}


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    assert len(TERMS) == 40, f"expected 40 catalog terms, have {len(TERMS)}"
    commit = github_head(WADEFAGEN_REPO)
    session = new_session()
    subjects = read_subjects()
    manifest_rows = []
    OUT.mkdir(parents=True, exist_ok=True)
    for term in TERMS:
        path = f"course-catalog/data/{term}.csv"
        dest = RAW / "catalog" / f"{term}.csv"
        manifest_rows.append(
            download(session, wadefagen_url(commit, path), dest, path) | {"file_used": dest.name}
        )
        data = read_text_csv(dest.read_bytes())
        missing = [c for c in KEEP if c not in data.columns]
        assert not missing, f"{term}: catalog columns missing {missing}"
        gies = data.loc[data["Subject"].isin(subjects), KEEP]
        gies.to_parquet(OUT / f"{term}.parquet", index=False)
        log.info("%s: %d Gies rows of %d", term, len(gies), len(data))
    update_manifest(manifest_rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
