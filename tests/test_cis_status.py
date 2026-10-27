from datetime import datetime, timedelta
from pathlib import Path

from ingest.cis_snapshot import parse_cascade
from ingest.cis_status import (
    CENTRAL,
    KNOWN_STATUSES,
    MAX_WAIT,
    RELAY_SLEEP,
    in_window,
    parse_course_page,
    plan,
    write_statuses,
)

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


def test_a_close_start_waits_an_early_one_relays_and_a_late_one_skips():
    def at(utc):
        return datetime.fromisoformat(utc).astimezone(CENTRAL)

    # 9:20 UTC on Nov 3 is 3:20 CST: wait 4 h 54 min, until 8:14.
    assert plan(at("2026-11-03T09:20:00+00:00")) == ("run", (4 * 60 + 54) * 60)
    # Inside the window, start now.
    assert plan(at("2026-11-03T14:20:00+00:00")) == ("run", 0)
    # 8:00 UTC is 2:00 CST, 6 h 14 min early: sleep 4 h 14 min, leaving the next run two hours.
    assert plan(at("2026-11-03T08:00:00+00:00")) == ("relay", (4 * 60 + 14) * 60)
    # The evening cron: 0:20 UTC on Oct 28 is 19:20 CDT, 12 h 54 min early: sleep the full 5 h 15.
    assert plan(at("2026-10-28T00:20:00+00:00")) == ("relay", (5 * 60 + 15) * 60)
    # A scheduled run that starts after 8:44 skips; the evening relay covers tomorrow.
    assert plan(at("2026-11-03T14:45:00+00:00")) == ("skip", None)


def test_the_gap_to_8_14_is_real_time_on_the_night_the_clocks_change():
    # 6:30 UTC on Nov 1 is 1:30 CDT; 8:14 CST that morning is 7 h 44 min away, not the 6 h 44 min
    # the wall clocks show. The relay sleeps the full 5 h 15 min, not 4 h 44 min.
    now = datetime.fromisoformat("2026-11-01T06:30:00+00:00").astimezone(CENTRAL)
    assert plan(now) == ("relay", (5 * 60 + 15) * 60)


def test_any_start_within_16_hours_relays_into_the_window():
    # A chain started at any minute in the 16 hours before 8:14, on an ordinary night and on the
    # night the clocks change, reaches the window: no relay sleeps past the job's limit, and the
    # last run waits at most five hours. Each fresh run is allowed two minutes to start.
    for target_utc in ("2026-10-28T13:14:00+00:00", "2026-11-01T14:14:00+00:00"):
        target = datetime.fromisoformat(target_utc)
        for minutes in range(0, 16 * 60 + 30, 7):
            now = target - timedelta(hours=16) + timedelta(minutes=minutes)
            action, wait = plan(now.astimezone(CENTRAL))
            while action == "relay":
                assert wait <= RELAY_SLEEP.total_seconds()
                now += timedelta(seconds=wait, minutes=2)
                action, wait = plan(now.astimezone(CENTRAL))
            assert action == "run"
            assert wait <= MAX_WAIT.total_seconds()
            assert in_window((now + timedelta(seconds=wait)).astimezone(CENTRAL))
