# The UIUC GPA dataset from wadefagen/datasets. Each row is one section with 21 or more graded
# students. The instructor column is dropped here, so names never reach data/extracts.

import logging
import sys

from ingest.http import new_session
from ingest.paths import EXTRACTS, RAW
from ingest.sources import (
    WADEFAGEN_REPO,
    download,
    github_head,
    read_text_csv,
    update_manifest,
    wadefagen_url,
)

log = logging.getLogger("gpa")

PATH = "gpa/uiuc-gpa-dataset.csv"
GRADES = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "D-", "F", "W"]
COLUMNS = ["Year", "Term", "YearTerm", "Subject", "Number", "Course Title", "Sched Type"]
COLUMNS += GRADES + ["Students", "Primary Instructor"]
OUT = EXTRACTS / "gpa" / "uiuc-gpa-dataset.parquet"


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    commit = github_head(WADEFAGEN_REPO)
    dest = RAW / PATH
    manifest_row = download(new_session(), wadefagen_url(commit, PATH), dest, PATH)
    data = read_text_csv(dest.read_bytes())
    assert list(data.columns) == COLUMNS, f"GPA columns changed: {list(data.columns)}"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    data.drop(columns=["Primary Instructor"]).to_parquet(OUT, index=False)
    update_manifest([manifest_row | {"file_used": dest.name}])
    log.info("gpa: %d rows from commit %s", len(data), commit[:7])
    return 0


if __name__ == "__main__":
    sys.exit(main())
