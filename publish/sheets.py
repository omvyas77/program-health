# Writes the marts in data/marts to same-named tabs of the project's Google Sheet, which Tableau
# Public reads. Each tab is cleared, resized to fit, written in one request with RAW input so
# numbers stay numbers, then read back; a row, column, or header mismatch fails the run.
# Credentials come from GCP_SA_KEY in Actions or the local key file and are never printed.

import argparse
import json
import logging
import math
import os
import sys
from datetime import date
from pathlib import Path

import gspread
import pandas as pd

from ingest.paths import MARTS

log = logging.getLogger("sheets")

KEY_FILE = Path.home() / ".config" / "gies-program-health" / "sa.json"
MAX_CELLS = 1_000_000


def client():
    key = os.environ.get("GCP_SA_KEY")
    if key:
        return gspread.service_account_from_dict(json.loads(key))
    assert KEY_FILE.exists(), "set GCP_SA_KEY or put the key at ~/.config/gies-program-health/"
    return gspread.service_account(filename=KEY_FILE)


def cell(value):
    if value is None or value is pd.NA or (isinstance(value, float) and math.isnan(value)):
        return ""
    if isinstance(value, pd.Timestamp):
        return value.date().isoformat() if value == value.normalize() else value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return value


def values(frame):
    rows = frame.astype(object).itertuples(index=False, name=None)
    return [list(frame.columns)] + [[cell(v) for v in row] for row in rows]


def write(spreadsheet, tabs, name, frame):
    rows, cols = len(frame) + 1, len(frame.columns)
    assert rows * cols <= MAX_CELLS, f"{name}: {rows * cols:,} cells, over {MAX_CELLS:,}"
    tab = tabs.get(name) or spreadsheet.add_worksheet(name, rows=rows, cols=cols)
    tab.clear()
    tab.resize(rows=rows, cols=cols)
    tab.update(values=values(frame), range_name="A1", value_input_option="RAW")
    back = tab.get_all_values()
    assert len(back) == rows, f"{name}: the tab has {len(back)} rows, the mart {rows}"
    assert back[0] == list(frame.columns), f"{name}: the header didn't come back as written"
    assert all(len(row) == cols for row in back), f"{name}: a row came back without {cols} cells"
    log.info("%s: %d rows", name, len(frame))


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "marts", nargs="*", help="marts to publish; every one in data/marts if none"
    )
    names = parser.parse_args().marts or sorted(p.stem for p in MARTS.glob("mart_*.parquet"))
    sheet_id = os.environ.get("SHEET_ID")
    assert sheet_id, "set SHEET_ID to the Google Sheet's ID"
    spreadsheet = client().open_by_key(sheet_id)
    tabs = {tab.title: tab for tab in spreadsheet.worksheets()}
    for name in names:
        write(spreadsheet, tabs, name, pd.read_parquet(MARTS / f"{name}.parquet"))
    log.info("published %d tabs", len(names))
    return 0


if __name__ == "__main__":
    sys.exit(main())
