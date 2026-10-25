import datetime

import pandas as pd

from ingest.paths import MARTS
from publish import refresh_log, registration_report, sheets

WATCH = pd.read_parquet(MARTS / "mart_registration_watch.parquet")


def test_sheet_values_keep_numbers_and_blank_missing_values():
    first = WATCH[WATCH.snapshot_date == WATCH.snapshot_date.min()].head(2)
    rows = sheets.values(first)
    assert rows[0] == list(first.columns)
    snapshot, days, subject, number, sections, added, removed, since_open = rows[1]
    assert snapshot == "2026-10-23"
    assert isinstance(days, int) and isinstance(sections, int)
    # The first snapshot has no previous one and comes before registration opens.
    assert (added, removed, since_open) == ("", "", "")


def test_sheet_cells_for_dates():
    assert sheets.cell(pd.Timestamp("2026-10-23")) == "2026-10-23"
    assert sheets.cell(datetime.date(2026, 10, 23)) == "2026-10-23"


def test_refresh_log_schema():
    log = pd.read_parquet(MARTS / "mart_refresh_log.parquet")
    assert dict(log.dtypes.astype(str)) == refresh_log.COLUMNS
    assert not log.duplicated(["run_utc", "mart"]).any()
    assert "mart_refresh_log" not in set(log.mart)


def test_registration_report_states_where_registration_stands():
    text = registration_report.report(WATCH)
    as_of = pd.to_datetime(WATCH.snapshot_date).max()
    assert text.startswith("# Spring 2027 registration watch\n")
    assert f"As of the {registration_report.day(as_of)} snapshot" in text
    assert registration_report.NOTE in text
