# High school graduates, actual and projected, from WICHE's Knocking at the College Door, 11th
# edition (December 2024; the workbook was relabeled on Jan 31, 2025 with no values changed).

import logging
import sys

import pandas as pd

from ingest.http import new_session
from ingest.paths import EXTRACTS, RAW
from ingest.sources import download, update_manifest

log = logging.getLogger("wiche")

URL = (
    "https://www.wiche.edu/wp-content/uploads/2024/12/"
    "Knocking-at-the-College-Door-11th-Edition-Projections-Dataset-12-11-2024.xlsx"
)
COLUMNS = [
    "Stabbr",
    "StateRegionUS",
    "ClassOf",
    "SchoolYear",
    "SchoolSector",
    "Grade",
    "RaceEthnicity",
    "Students",
    "ActualProjected",
    "REGION_Census",
    "REGION_Census_Division",
    "RegionWICHE",
]
# Illinois, WICHE's Midwest, the Census Bureau's Midwest, and the nation. Both Midwest
# definitions are kept; the analysis says which one it uses.
GEOGRAPHIES = {"IL", "_M", "CM", "_U"}
OUT = EXTRACTS / "wiche" / "hs_graduates.parquet"


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    dest = RAW / "wiche" / "knocking-11th-edition.xlsx"
    manifest_row = download(new_session(), URL, dest, "wiche/knocking-11th-edition.xlsx")
    data = pd.read_excel(dest, sheet_name="Data", dtype=str, na_filter=False, engine="openpyxl")
    assert list(data.columns) == COLUMNS, f"WICHE columns changed: {list(data.columns)}"
    keep = data[data["Stabbr"].isin(GEOGRAPHIES) & (data["Grade"] == "High school graduates")]
    found = set(keep["Stabbr"])
    assert found == GEOGRAPHIES, f"WICHE geographies missing: {GEOGRAPHIES - found}"
    OUT.parent.mkdir(parents=True, exist_ok=True)
    keep.to_parquet(OUT, index=False)
    update_manifest([manifest_row | {"file_used": "Data sheet"}])
    log.info("wiche: kept %d of %d rows", len(keep), len(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
