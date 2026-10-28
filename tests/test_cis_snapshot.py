# Fixtures are live Spring 2027 responses for BDI and MBA fetched Oct 23, 2026, with instructor
# names, the department contact, and the department head removed.

import csv
from datetime import date, datetime
from pathlib import Path

import pytest

from ingest.cis_snapshot import COLUMNS, parse_cascade, snapshot_day, validate, write_snapshot

FIXTURES = Path(__file__).parent / "fixtures" / "cis"


def bdi_rows():
    return parse_cascade((FIXTURES / "2027-sp_BDI_cascade.xml").read_bytes(), "BDI")


def test_cascade_returns_every_bdi_section():
    rows = bdi_rows()
    assert len(rows) == 11
    assert len({row["crn"] for row in rows}) == 11
    assert {row["number"] for row in rows} == {"199", "367", "475", "513", "587", "593"}
    assert all(row["section"] and row["type_code"] and row["section_status"] for row in rows)


def test_write_keeps_sections_without_a_section_number(tmp_path):
    # MBA 530 and MBA 531 are independent study sections the API lists with no section number.
    rows = parse_cascade((FIXTURES / "2027-sp_MBA_cascade.xml").read_bytes(), "MBA")
    out = tmp_path / "2026-10-23.csv"
    write_snapshot(rows, out, "2026-10-23T14:00:00Z")
    with out.open(newline="") as f:
        reader = csv.DictReader(f)
        written = list(reader)
    assert reader.fieldnames == COLUMNS
    assert len(written) == len(rows) == 24
    assert {r["number"] for r in written if r["section"] == ""} == {"530", "531"}
    assert list(tmp_path.iterdir()) == [out]


def test_validate_passes_when_count_matches_previous():
    rows = bdi_rows()
    validate(rows, ["BDI"], previous_count=len(rows))


def test_validate_fails_on_large_row_change():
    rows = bdi_rows()
    with pytest.raises(AssertionError, match="previous snapshot"):
        validate(rows, ["BDI"], previous_count=len(rows) * 2)


def test_validate_fails_on_duplicate_crn():
    rows = bdi_rows()
    with pytest.raises(AssertionError, match="more than once"):
        validate(rows + rows[:1], ["BDI"], previous_count=None)


def test_validate_fails_when_a_subject_returns_nothing():
    rows = bdi_rows()
    with pytest.raises(AssertionError, match="ACCY"):
        validate(rows, ["BDI", "ACCY"], previous_count=None)


def test_a_late_evening_snapshot_keeps_its_central_date():
    def day(utc):
        return snapshot_day(datetime.fromisoformat(utc))

    # The run started by hand at 7:49 pm CDT on Oct 26, 2026, already Oct 27 in UTC.
    assert day("2026-10-27T00:49:22+00:00") == date(2026, 10, 26)
    assert day("2026-10-28T18:39:00+00:00") == date(2026, 10, 28)
    # After the change to standard time, 11:30 pm CST on Nov 2 and 12:30 am on Nov 3.
    assert day("2026-11-03T05:30:00+00:00") == date(2026, 11, 2)
    assert day("2026-11-03T06:30:00+00:00") == date(2026, 11, 3)
