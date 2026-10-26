# Daily enrollment status for Gies's Spring 2027 sections, read from the public course pages.
# The Course Explorer API has no status field, and on Oct 26, 2026 Tech Services approved one
# automated pass a day over the Gies course pages on two conditions: two seconds between
# requests, and a start at 8:14 am Central, which falls between their status updates. The pass
# runs only from 8:14 to 8:44 Central and stops after the last day to add. Its course list comes
# from the latest API snapshot, so it makes no API calls. Only each CRN and its status are kept:
# the instructor cell is never read and no page is saved. A bot-protection challenge stops the
# pass with nothing written; it is never worked around.

import csv
import logging
import sys
from datetime import UTC, datetime
from datetime import time as clock
from zoneinfo import ZoneInfo

from lxml import html

from ingest.cis_snapshot import TERM, read_last_day_to_add
from ingest.http import fetch, new_session, require_ok
from ingest.paths import ROOT, SNAPSHOTS, STATUS_SNAPSHOTS

log = logging.getLogger("cis_status")

WEB_BASE = "https://courses.illinois.edu/schedule/2027/spring"
CENTRAL = ZoneInfo("America/Chicago")
WINDOW = (clock(8, 14), clock(8, 44))
REQUEST_GAP_S = 2.0
COLUMNS = ["snapshot_utc", "crn", "status"]
KNOWN_STATUSES = {
    "Open",
    "Open (Restricted)",
    "Closed",
    "CrossListOpen",
    "CrossListOpen (Restricted)",
    # seen Oct 23, 2026 on the two sections whose API section status is P
    "Pending",
}


def in_window(now_central):
    return WINDOW[0] <= now_central.time() <= WINDOW[1]


def course_list(term_dir):
    # The latest API snapshot, usually written at 13:07 UTC the same morning.
    snapshots = sorted(term_dir.glob("*.csv"))
    assert snapshots, f"no API snapshot in {term_dir.relative_to(ROOT)}"
    with snapshots[-1].open(newline="") as f:
        rows = list(csv.DictReader(f))
    courses = sorted({(row["subject"], row["number"]) for row in rows})
    return snapshots[-1].stem, courses, {row["crn"] for row in rows}


def parse_course_page(page_html):
    # Reads only the CRN cell and the Availability value; the instructor cell is never touched.
    tables = html.fromstring(page_html).xpath('//table[@id="schedule-course-table"]')
    assert len(tables) == 1, f"expected one schedule table on the course page, found {len(tables)}"
    headers = [th.text_content().strip() for th in tables[0].xpath("./thead/tr/th")]
    assert "CRN" in headers, f"schedule table has no CRN column: {headers}"
    crn_col = headers.index("CRN")
    availability = {}
    for row in tables[0].xpath("./tbody/tr"):
        crn = row.xpath("./td")[crn_col].text_content().strip()
        values = row.xpath('.//dt[normalize-space()="Availability:"]/following-sibling::dd[1]')
        assert len(values) == 1, f"CRN {crn}: expected one Availability, found {len(values)}"
        assert crn not in availability, f"CRN {crn} appears twice on one course page"
        availability[crn] = values[0].text_content().strip()
    return availability


def collect(session, courses):
    statuses = {}
    for subject, number in courses:
        # require_ok fails on anything but a 200 with a body, including the 202 with an empty
        # body that bot protection sends, so a challenge ends the pass.
        page = require_ok(fetch(session, f"{WEB_BASE}/{subject}/{number}", gap=REQUEST_GAP_S))
        for crn, status in parse_course_page(page).items():
            assert statuses.get(crn, status) == status, f"CRN {crn} has two statuses"
            statuses[crn] = status
    return statuses


def write_statuses(statuses, path, snapshot_utc):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    with temp.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNS)
        writer.writerows((snapshot_utc, crn, statuses[crn]) for crn in sorted(statuses))
    temp.replace(path)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    now = datetime.now(UTC)
    central = now.astimezone(CENTRAL)
    if central.date() > read_last_day_to_add():
        log.info("past the last day to add; nothing to do")
        return 0
    if not in_window(central):
        log.info("%s Central is outside 8:14 to 8:44; no pass today from this run", central)
        return 0
    path = STATUS_SNAPSHOTS / TERM / f"{central.date()}.csv"
    if path.exists():
        log.info("%s already exists", path.relative_to(ROOT))
        return 0
    snapshot_day, courses, api_crns = course_list(SNAPSHOTS / TERM)
    log.info("%d course pages, from the %s API snapshot", len(courses), snapshot_day)
    statuses = collect(new_session(), courses)
    unknown = sorted({s for s in statuses.values() if s not in KNOWN_STATUSES})
    if unknown:
        log.warning("statuses not seen before: %s", unknown)
    # Sections can change between the API snapshot and the pass; dbt reports the CRNs that differ.
    log.info(
        "%d statuses; %d CRNs not in the API snapshot; %d API CRNs without a status",
        len(statuses),
        len(set(statuses) - api_crns),
        len(api_crns - set(statuses)),
    )
    write_statuses(statuses, path, now.strftime("%Y-%m-%dT%H:%M:%SZ"))
    log.info("wrote %s", path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
