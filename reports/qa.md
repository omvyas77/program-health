# QA, Oct 26 to 29, 2026

The checks I ran before sharing the project: that it rebuilds from a clone, that every number in the brief is computed, that no person is named, that every link resolves, and that the published dashboards and app show what the marts say.

| Check | Result |
|---|---|
| A fresh clone runs make all | Pass. Exit 0 in 11 minutes, dbt PASS=153, and the rebuilt marts match the committed ones. |
| Number audit | Pass. Every analytic number in the brief is computed by brief/numbers.py; none is typed by hand in the brief, the guide, or the README. |
| Privacy | Pass. No instructor names in any committed file. |
| Links | Pass. 17 of 17 resolve, among them the Tableau workbook and the Streamlit app. |
| PDFs render | Pass. brief/brief.pdf is 4 pages and brief/guide.pdf is 1 page; both link to the dashboards, the app, and the repository. |
| Scheduled jobs | Fixed. Both Oct 26 snapshot runs failed; the cause is fixed and a run by hand passed. Oct 27 has no snapshot and no status (data_notes.md). |
| Published dashboards and app | Pass: every title number matches the marts. Display fixes still open are listed below. |

## A fresh clone runs make all

| Step | Result |
|---|---|
| Clone | Into an empty folder |
| pip install -r requirements.txt | Exit 0, 54 s |
| make all | Exit 0, 647 s |
| dbt build | PASS=153 WARN=0 ERROR=0 |
| Rebuilt marts against the committed ones | 15 files, same rows and columns, every non-float value identical. The largest float difference is 5.7e-9, in the online projection's interval bounds. |
| Downloads against the manifest | 257 files, 255 identical by SHA-256. HD2024.zip and its dictionary hashed differently because NCES serves more than one copy of the same file (data_notes.md); the marts built from them are identical. |

## Number audit

Every number in the brief's text comes from an inline expression in brief/brief.qmd that reads brief/numbers.py. The numbers typed as text are counts, codes, and dates that don't come from the data:

| File | Number | What it is | Checked against |
|---|---|---|---|
| brief, guide, README | 18, 17, 16 | Big Ten universities, the peers other than Illinois, the public ones | config/peers.csv |
| brief | 52 | The CIP code family for business | NCES CIP 2020 |
| brief | July 1, 2026, 2026-27, 2027-28 | When AACSB's 2026 standards took effect, the transition year, and the first year they are required | aacsb.edu/accreditation/standards |
| brief | Standards 5, 6, 7 | Assurance of learning, learner progression, teaching effectiveness and impact | AACSB's 2026 standards |
| brief | 80% | Width of the projection's interval | forecast/projection.py |
| brief | 2019 to 2021 | Penn State's IPEDS years reported for all campuses | docs/data_notes.md |
| guide, README | 20, 21 | The GPA dataset leaves out sections of 20 or fewer students | The dataset's README |
| guide | 25th, 75th | The peer band is the interquartile range | docs/tableau_spec.md |
| guide, README | 8:14, Oct 28, 2026 | The approved start time and the first day the status pass ran | Tech Services' reply; .github/workflows/status.yml |

The outlook sensitivities in projection_method.md were also recomputed by hand from the stock-and-flow recursion.

## Privacy

| Where | What was checked | Result |
|---|---|---|
| Every committed CSV and parquet under data/ and config/ | Column names that could hold a person | none |
| data/extracts/gpa | Columns | Year, Term, YearTerm, Subject, Number, Course Title, Sched Type, grade counts, Students |
| data/extracts/tre | Columns | term, unit, role, listings |

The Primary Instructor column is dropped at ingest (ingest/gpa.py). The Course Explorer fixtures in tests/fixtures/cis have empty instructor elements, and the registration snapshots carry no instructor column. The Google service account key lives outside the repository, in GitHub Secrets.

## Links

Every URL in the README, docs/, and brief/ was requested once, 1 s apart. All returned 200 or a redirect to the expected page, except two NCES download folders that have no index page; the files under them load. courses.illinois.edu wasn't requested: its pages are read only by the approved daily pass.

## Scheduled jobs

| Workflow | Runs | Result |
|---|---|---|
| ci | Every push | Pass |
| snapshot | Oct 26 | Failed. The job builds only the registration watch's models, and dbt's default test selection also picked a test that reads mart_course_sections. Fixed with --indirect-selection cautious in snapshot.yml and status.yml. |
| status | Oct 27 | Never started before the 8:44 window closed, because scheduled jobs here start hours late. The workflow now starts the evening before and relays (runbook.md). |

## Published dashboards, Oct 28 and 29, 2026

Title numbers were read off the published workbook and compared with the check values in docs/tableau_spec.md.

| Dashboard | Values checked | Result |
|---|---|---|
| Overview | 10,095, +2.7% since Fall 2021; 89.4%, 5,763 of 6,443; 94.8% against 93.0%; 14th of 18, 9.5% against 16.7% | Pass |
| Peers | 7 of 18 on retention, Illinois 94.8%; admitted 42.4% against a peer median of 58.1%, yield 28.8% | Pass |
| Grades | ACCY 201 57.8% in Fall 2025; 80.0% in Fall 2025, up from 54.4% in Fall 2010 | Pass |
| Course Watch | 5 courses; FIN 300 23.3% over four terms; widest section spread 1.04 points | Pass |
| Sections | ACCY 201: 3 primary sections in Fall 2025 and Fall 2019; 162.7 graded students per section against 201.3 | Pass |
| Registration | Follows the daily snapshot: 507 primary sections and 2.4% closed as of Oct 29, 2026 | Pass |

Display fixes still open, none of which changes a number:

- The footer's date reads "Oct 26,2026", with no space after the comma.
- Overview's legend names and the headcount table's row names are cut off.
- The watch list totals carry no course names and don't line up with the list's rows.
- The Grades info button reads "Defintions", and its text doesn't mention the missing Spring 2012 (data_notes.md).
- The two closed-share sheets label their axis "Days Since Registration Open" while the curves above them say "Days from the start of registration".

## Streamlit app, Oct 28 and 29, 2026

https://gies-program-health.streamlit.app/, compared with data/marts.

| Page | Values checked | Result |
|---|---|---|
| Enrollment scenarios | Base 3,841 undergraduates in Fall 2030, up from 3,652 in Fall 2026, low 3,632 and high 4,171; online graduate headcount holds at 5,763, 80% range 3,682 to 7,844 | Pass |
| Enrollment scenarios, changed input | 900 freshmen a year gives 4,176 in Fall 2030, 335 above base | Pass |
| Registration watch | Follows the daily snapshot: 507 primary sections across 223 courses on Oct 29; every section closed in ACCY 321, BADM 303, and BADM 366 | Pass |

The marts are cached by file modification time, so the app picks up each day's snapshot without a restart.
