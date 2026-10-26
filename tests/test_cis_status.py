from datetime import datetime
from pathlib import Path

from ingest.cis_snapshot import parse_cascade
from ingest.cis_status import CENTRAL, KNOWN_STATUSES, in_window, parse_course_page, write_statuses

FIXTURES = Path(__file__).parent / "fixtures" / "cis"


def test_course_page_gives_one_known_status_per_api_crn():
    rows = parse_cascade((FIXTURES / "2027-sp_BDI_cascade.xml").read_bytes(), "BDI")
    api_crns = {row["crn"] for row in rows if row["number"] == "199"}
    availability = parse_course_page((FIXTURES / "2027-sp_BDI_199.html").read_bytes())
    assert set(availability) == api_crns
    assert set(availability.values()) <= KNOWN_STATUSES


def test_window_is_8_14_to_8_44_central_across_the_change_from_daylight_time():
    # 13:14 UTC is 8:14 on Oct 30 (CDT) and 7:14 on Nov 2 (CST); 14:14 UTC the reverse.
    def central(utc):
        return datetime.fromisoformat(utc).astimezone(CENTRAL)

    assert in_window(central("2026-10-30T13:14:00+00:00"))
    assert not in_window(central("2026-10-30T14:14:00+00:00"))
    assert in_window(central("2026-11-02T14:14:00+00:00"))
    assert not in_window(central("2026-11-02T13:14:00+00:00"))
    assert in_window(central("2026-11-02T14:44:00+00:00"))
    assert not in_window(central("2026-11-02T14:45:00+00:00"))


def test_written_file_holds_only_crn_and_status(tmp_path):
    availability = parse_course_page((FIXTURES / "2027-sp_BDI_199.html").read_bytes())
    path = tmp_path / "2026-10-27.csv"
    write_statuses(availability, path, "2026-10-27T13:20:00Z")
    lines = path.read_text().splitlines()
    assert lines[0] == "snapshot_utc,crn,status"
    assert len(lines) == len(availability) + 1
