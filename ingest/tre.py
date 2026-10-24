# Teachers Ranked as Excellent, from wadefagen/datasets. The file lists instructors by name, so
# it is counted here by term, unit, and role, and names never leave data/raw.

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

log = logging.getLogger("tre")

PATH = "teachers-ranked-as-excellent/uiuc-tre-dataset.csv"
COLUMNS = ["term", "unit", "lname", "fname", "role", "ranking", "course"]
OUT = EXTRACTS / "tre" / "tre_counts.parquet"


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    commit = github_head(WADEFAGEN_REPO)
    dest = RAW / PATH
    manifest_row = download(new_session(), wadefagen_url(commit, PATH), dest, PATH)
    data = read_text_csv(dest.read_bytes())
    assert list(data.columns) == COLUMNS, f"TRE columns changed: {list(data.columns)}"
    counts = data.groupby(["term", "unit", "role"]).size().reset_index(name="listings")
    assert counts["listings"].sum() == len(data), "counts do not add back to the row total"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    counts.to_parquet(OUT, index=False)
    update_manifest([manifest_row | {"file_used": dest.name}])
    log.info("tre: %d listings in %d term-unit-role groups", len(data), len(counts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
