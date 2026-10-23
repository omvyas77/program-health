# Section status during registration can't be collected after the fact, so this runs daily.
# The Course Explorer API is the university's documented route for automated access. It lists
# every section but carries no enrollment status, so the snapshot records which sections exist
# and their section status; sections added or removed during registration show up day to day.
# The public course pages do show availability, but they sit behind bot protection.

import csv
import logging
import sys
from collections import Counter
from datetime import UTC, date, datetime

from lxml import etree

from ingest.http import fetch, new_session, require_ok
from ingest.paths import CONFIG, ROOT, SNAPSHOTS

log = logging.getLogger("cis_snapshot")

TERM = "2027-sp"
API_BASE = "https://courses.illinois.edu/cisapp/explorer/schedule/2027/spring"
MAX_ROW_CHANGE = 0.20
COLUMNS = [
    "snapshot_utc",
    "term",
    "subject",
    "number",
    "crn",
    "section",
    "type_code",
    "part_of_term",
    "section_status",
]


def read_subjects():
    with (CONFIG / "gies_subjects.csv").open(newline="") as f:
        subjects = [row["subject"] for row in csv.DictReader(f)]
    assert subjects, "config/gies_subjects.csv lists no subjects"
    return subjects


def read_last_day_to_add():
    with (CONFIG / "registration.csv").open(newline="") as f:
        rows = [row for row in csv.DictReader(f) if row["term"] == TERM]
    assert len(rows) == 1, f"config/registration.csv needs exactly one row for {TERM}"
    return date.fromisoformat(rows[0]["last_day_to_add"])


def listed_subjects(term_xml):
    return {s.get("id") for s in etree.fromstring(term_xml).iterfind("subjects/subject")}


def parse_cascade(subject_xml, subject):
    # Only the root element is namespaced (ns2:subject); its children are not.
    root = etree.fromstring(subject_xml)
    rows = []
    for course in root.iterfind("cascadingCourses/cascadingCourse"):
        course_subject, number = course.get("id").split(" ")
        assert course_subject == subject, f"{course.get('id')} listed under {subject}"
        for section in course.iterfind("detailedSections/detailedSection"):
            codes = [t.get("code") for t in section.iterfind("meetings/meeting/type")]
            rows.append(
                {
                    "subject": subject,
                    "number": number,
                    "crn": section.get("id"),
                    "section": section.findtext("sectionNumber"),
                    # a few sections mix meeting types (LCD and OLB in ACCY); keep each one
                    "type_code": ";".join(dict.fromkeys(codes)),
                    "part_of_term": section.findtext("partOfTerm"),
                    "section_status": section.findtext("sectionStatusCode"),
                }
            )
    return rows


def snapshot_subject(session, subject):
    response = fetch(session, f"{API_BASE}/{subject}.xml?mode=cascade")
    rows = parse_cascade(require_ok(response), subject)
    courses = {row["number"] for row in rows}
    log.info("%s: %d courses, %d sections", subject, len(courses), len(rows))
    return rows


def previous_row_count(term_dir, today):
    earlier = sorted(p for p in term_dir.glob("*.csv") if p.stem < today.isoformat())
    if not earlier:
        return None
    with earlier[-1].open(newline="") as f:
        return sum(1 for _ in csv.DictReader(f))


def validate(rows, subjects, previous_count):
    missing = set(subjects) - {row["subject"] for row in rows}
    assert not missing, f"no sections returned for {sorted(missing)}"
    crns = Counter(row["crn"] for row in rows)
    duplicates = sorted(crn for crn, n in crns.items() if n > 1)
    assert not duplicates, f"CRNs appear more than once: {duplicates}"
    if previous_count is not None:
        change = abs(len(rows) - previous_count) / previous_count
        assert change <= MAX_ROW_CHANGE, (
            f"{len(rows)} sections against {previous_count} in the previous snapshot, "
            f"a {change:.1%} change (limit {MAX_ROW_CHANGE:.0%})"
        )


def write_snapshot(rows, path, snapshot_utc):
    # Independent study sections have no section number in the API, so they sort and write
    # as blank.
    ordered = sorted(rows, key=lambda r: (r["subject"], r["number"], r["section"] or "", r["crn"]))
    # Write to a temporary name first so a failed write never leaves a partial snapshot.
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for row in ordered:
            writer.writerow({"snapshot_utc": snapshot_utc, "term": TERM, **row})
    tmp.replace(path)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    started = datetime.now(UTC)
    today = started.date()
    if today > read_last_day_to_add():
        log.info("past the last day to add for %s, nothing to collect", TERM)
        return 0
    out = SNAPSHOTS / TERM / f"{today.isoformat()}.csv"
    if out.exists():
        log.info("%s already exists", out.relative_to(ROOT))
        return 0

    subjects = read_subjects()
    session = new_session()
    response = fetch(session, f"{API_BASE}.xml")
    if response.status_code == 404:
        log.info("%s is not published yet", TERM)
        return 0
    unlisted = set(subjects) - listed_subjects(require_ok(response))
    assert not unlisted, f"{TERM} does not list {sorted(unlisted)}"

    rows = [row for subject in subjects for row in snapshot_subject(session, subject)]
    validate(rows, subjects, previous_row_count(out.parent, today))
    write_snapshot(rows, out, started.strftime("%Y-%m-%dT%H:%M:%SZ"))
    log.info("wrote %d sections to %s", len(rows), out.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
