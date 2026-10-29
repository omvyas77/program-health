# Final QA, Oct 26 to 28, 2026

The final checks, run before the application deadline. The published dashboards were checked on Oct 28 (Published dashboards, below). So was the deployed app (Streamlit app, below). What still waits on time is listed at the end as not run yet.

| Check | Result |
|---|---|
| A fresh clone runs make all | Pass. Exit 0 in 11 minutes, dbt PASS=153, and the rebuilt marts match the committed ones. |
| Number audit | Pass. 159 values in the brief are computed by brief/numbers.py; no analytic number is typed by hand in the brief, the guide, or the README. |
| Prose check | Pass, rerun Oct 28. No banned words, em dashes, or emoji; every exclamation-point hit is Markdown image syntax, the != operator, or a spreadsheet reference. |
| Privacy | Pass. No instructor names in any committed file. |
| Secrets | Pass, rerun Oct 28. Every hit in the history is this report quoting its own search terms or a planning note's instruction to search. |
| Links | Pass, rerun Oct 28. 17 of 17 resolve, among them the Tableau workbook and the Streamlit app; two NCES paths are download folders with no index page, and the files under them load. |
| PDFs render | Pass, rerendered Oct 28 with that day's snapshot and first closed share. brief/brief.pdf is 4 pages, brief/guide.pdf is 1 page, and both link to the dashboards, the app, and the repository. |
| Scheduled jobs | Fixed. Both Oct 26 snapshot runs had failed; the cause is fixed and a run by hand passed. Oct 26 has no snapshot. |
| Published dashboards and app | Pass on Oct 28: every title number matches; the app's numbers match the marts (sections below). |

## A fresh clone runs make all

| Step | Result |
|---|---|
| Clone | omvyas77/program-health at abb0f10, into an empty folder |
| pip install -r requirements.txt | Exit 0, 54 s |
| make all | Exit 0, 647 s |
| dbt build | PASS=153 WARN=0 ERROR=0 |
| Rebuilt marts against the committed ones | 15 files, same rows and columns, every non-float value identical. The largest float difference is 5.7e-9, in the online projection's interval bounds; the peer percentiles differ by 1.1e-16. |
| Downloads against the manifest | 257 files, 255 identical by SHA-256. HD2024.zip and its dictionary hashed differently because NCES serves more than one copy of the same file (data_notes.md); the marts built from them are identical. |

The same run also showed that data/marts/mart_funnel had been exported before Illinois's Common Data Set rows were verified. It now carries them (8 rows: all, in-state, out-of-state, and international for Fall 2024 and Fall 2025).

## Number audit

Every number in the brief's text comes from an inline expression; the brief has no hand-typed analytic numbers. The table at the bottom lists all 159 computed values and their current values.

Numbers typed as text, and why each is safe to type:

| File | Number | What it is | Checked against |
|---|---|---|---|
| brief, guide, README | 18, 17, 16 | Big Ten universities, the peers other than Illinois, the public ones | config/peers.csv |
| brief | 52 | The CIP code family for business | NCES CIP 2020 |
| brief | 2026, 2026-27, 2027-28, about 30 | AACSB's 2026 standards, the pilot year and its number of schools, the year they take effect | aacsb.edu/educators/global-standards, read Oct 26, 2026 |
| brief | Standards 5, 6, 7 | Assurance of learning, learner progression, teaching effectiveness and impact | The same page |
| brief | 80% | Width of the projection's interval | forecast/projection.py |
| brief | 2019 to 2021 | Penn State's IPEDS years reported for all campuses | docs/data_notes.md |
| brief, README | 2012, 2025, 2024-25, 2025-26, 11th, 2024 | Years and editions in the reference list | The sources |
| guide, README | 20, 21 | The GPA dataset leaves out sections of 20 or fewer students | The dataset's README |
| guide | 25th, 75th | The peer band is the interquartile range | docs/tableau_spec.md |
| guide, README | 8:14, Oct 28, 2026 | The approved start time and the first day the status pass ran | Tech Services' reply; .github/workflows/status.yml |
| README | 3.12, 1.5 | Python and Quarto versions | requirements and Makefile |

The drafted docs (docs/my_notes.md, docs/decisions.md, docs/projection_method.md) were checked against the marts and docs/findings.md: 4,940 students added and 4,781 of them online, residential graduate 1,068 to 680, 901 freshmen, Accountancy juniors and seniors 663 to 545, Accountancy + Data Science 194, 17.5 of the 21.7-point rise within courses, 1.4% D, F, or W, 7th of 18 in retention, 14th of 18 in business share, the 6,506-row largest mart, the in-state funnel (29,419 applicants, 14,509 admits, 6,587 enrolled) and the 59.9% what-if. The two outlook figures in projection_method.md were recomputed by hand from the stock-and-flow recursion: holding 901 freshmen adds 118 x (1 + 0.781 + 0.781^2 + 0.781^3) = 338, and one point of continuation adds about 107 by Fall 2030.

Dashboard titles were audited against tableau_spec.md on Oct 28, 2026, under Published dashboards.

## Prose check

Every tracked Markdown and Quarto file and the app's Python strings, searched for a list of banned words, em dashes, emoji, and exclamation points. Untracked planning notes, which quote the list, are skipped.

| Where | Exclamation-point hits | What they are |
|---|---:|---|
| README.md, brief/brief.qmd, brief/guide.qmd | 8 | Markdown image syntax, and != in the brief's Python |
| docs/findings.md | 1 | != in SQL |
| data/manual/cds_c1_checklist.md, docs/data_notes.md | 8 | Spreadsheet references (CDS-C!C49) and Excel's #REF! error |

None is an exclamation. No banned words, em dashes, or emoji. Rerun Oct 28 after the last edits to the brief, the guide, the README, and the docs.

## Privacy

| Where | What was checked | Result |
|---|---|---|
| Every committed CSV and parquet under data/ and config/ | Column names that could hold a person | none |
| data/extracts/gpa | Columns | Year, Term, YearTerm, Subject, Number, Course Title, Sched Type, A+, A, A-, B+, B, B-, C+, C, C-, D+, D, D-, F, W, Students |
| data/extracts/tre | Columns | term, unit, role, listings |
| Docs, code, and specs | 'Primary Instructor', 'Prof.', 'Dr. Name' | docs/data_sources.md:13, ingest/gpa.py:23, ingest/gpa.py:35 |

The three mentions are a sentence saying the Primary Instructor column is dropped, and the code that drops it. The Course Explorer fixtures in tests/fixtures/cis have empty instructor elements and cells, and the registration snapshots carry no instructor column.

## Secrets

| Search over git log -p --all | Lines |
|---|---:|
| private_key | 4: a planning note's instruction to search, and this report naming it |
| BEGIN PRIVATE KEY | 1: this table |
| client_email | 1: this table |
| sk-ant- | 1: this table |
| AIza | 1: this table |

The service account key stays outside the repository, in ~/.config/gies-program-health and in GitHub Secrets.

## Links

Every URL in the README, docs/, and brief/ was requested once, 1 s apart, with a user agent naming this project.

| URL | Status |
|---|---|
| aacsb.edu/educators/global-standards | 200 |
| answers.illinois.edu/88215 | 200 |
| dair.illinois.edu | 200 |
| dair.illinois.edu/access-data/retention-and-graduation-rates/ | 200 |
| dair.illinois.edu/access-data/statistical-abstract/ | 200 |
| dair.illinois.edu/access-data/student-enrollment/ | 200 |
| dmi.illinois.edu/stuenr/ | 200, redirects to DAIR, as data_notes.md says |
| gies-program-health.streamlit.app | 303 to Community Cloud's cookie check for scripts; loads in a browser |
| github.com/omvyas77/program-health | 200 |
| github.com/omvyas77/program-health/issues | 200 |
| github.com/wadefagen/datasets | 200 |
| nces.ed.gov/ipeds/cipcode/resources.aspx?y=56 | 200 |
| nces.ed.gov/ipeds/survey-components/data-release-schedule | 200 |
| nces.ed.gov/ipeds/complete-data-files/ | 404 for the folder; HD2024.zip under it returns 200 |
| nces.ed.gov/ipeds/datacenter/data/ | 403 for the folder; HD2022.zip under it returns 200 |
| public.tableau.com/app/profile/om.vyas/viz/GiesProgramHealth/Overview | 200 |
| wiche.edu/knocking/data/ | 200 |

courses.illinois.edu wasn't requested. Its pages are read only by the approved daily pass, between 8:14 and 8:44 am Central. Every relative link in the README points to a file that exists.

## PDFs

| File | Pages | Rendered with |
|---|---:|---|
| brief/brief.pdf | 4 | make brief (Quarto 1.10.19, Typst 0.15.1), Oct 28, from the Oct 28 snapshot |
| brief/guide.pdf | 1 | make guide; still one page with a 2.0 in screenshot in place |

## Scheduled jobs

| Workflow | Last runs | Result |
|---|---|---|
| ci | Every push today | Pass |
| snapshot | Oct 26, 19:11 and 23:17 UTC | Failed. The job builds only the registration watch's models on an empty warehouse, and dbt's default test selection also picked assert_course_sections_match_sources, which reads mart_course_sections. It began once the status columns made the watch read int_type_codes. |
| snapshot | Oct 27, 00:49 UTC, started by hand | Pass, PASS=13, after adding --indirect-selection cautious to snapshot.yml and status.yml. The same failure and fix were reproduced first on an empty warehouse in the fresh clone. |
| status | Oct 27, scheduled from 9:20 UTC | Never started before the window closed: GitHub ran none of the five morning runs in time. The workflow now starts the evening before and relays to fresh runs (data_notes.md, runbook.md). Its rebuild job has the same test-selection fix. |

The run started by hand at 00:49 UTC on Oct 27 was 7:49 pm on Oct 26 in Central time. Snapshots were then named by UTC date, so it was filed as Oct 27 and both Oct 27 runs found it and exited. Since Oct 28 they are named by Central date and that file is Oct 26's, so the day with no snapshot is Oct 27 (data_notes.md). Both daily jobs now also write the mart_registration_watch tab to the Google Sheet after they commit, so Tableau's registration curves follow the day's data instead of waiting for Monday's refresh.

## Published dashboards, Oct 28, 2026

The workbook at https://public.tableau.com/app/profile/om.vyas/viz/GiesProgramHealth/Overview, opened in a fresh browser at 1400 by 1000: six dashboards, tabs on, opening on Overview. Title numbers were read off the page and compared with the Check lines in docs/tableau_spec.md; chart marks were compared by eye against their axes, and the Grades bars by measuring the rendered bands.

| Dashboard | Values checked | Result |
|---|---|---|
| Overview | 10,095, +2.7% since Fall 2021; 89.4%, 5,763 of 6,443; 94.8% against 93.0%; 14th of 18, 9.5% against 16.7%; 5,155 to 10,095 with 4,781 of the added students online; the table's Fall 2017 and Fall 2026 columns | Pass |
| Peers | 7 of 18 on retention with all 18 schools, Illinois 94.8%; admitted 42.4% against a peer median of 58.1%, yield 28.8%; the over-time lines | Pass |
| Grades | ACCY 201 57.8% in Fall 2025; 80.0% in Fall 2025, up from 54.4% in Fall 2010; the Fall 2025 bar's five bands against 282, 129, 53, 24, and 4 of 492 | Pass |
| Course Watch | 5 courses; FIN 300 25.8% in 2024-sp and 23.3% over four terms; all five rows of four-term averages; widest section spread 1.04 points | Pass |
| Sections | ACCY 201: 3 primary sections in Fall 2025 against 3 in Fall 2019; 604 and 488 graded students; 162.7 per section against 201.3 | Pass |
| Registration | 509 primary sections as of Oct 28, 2026, registration opens in 5 days; 2.4% closed, 12 of 509, as in reports/registration_watch_2027-sp.md; ACCY 201 3 sections, 0 of 3 closed | Pass |
| Footer | "Data refreshed Oct 26,2026", the last weekly refresh in mart_refresh_log | Pass; the date is missing a space after the comma |

Display issues found on Oct 28, none of which changes a number. Om fixed them that evening; the Oct 29 morning check confirms each one (Not run yet, below).

- "ACCY 201 :" has a space before the colon on Sections By Term, Registration Chosen Course, and Closed Share Chosen Course.
- The two closed-share sheets title their axis "Days Since Registration Open" and label the reference line "Registration Opens Nov 2"; the curves above them say "Days from the start of registration" and "Registration opens Nov 2".
- Overview's legend names and the headcount table's row names are cut off.
- The four-term averages beside the watch list carry no course names and don't line up with its rows; the course titles are cut off.
- The Grades info button reads "Defintions", and its text doesn't mention the missing Spring 2012 (data_notes.md).
- The first upload, gies-program-health, is still on the profile beside GiesProgramHealth.

## Streamlit app, Oct 28, 2026

https://gies-program-health.streamlit.app/, opened in a fresh browser and compared with data/marts.

| Page | Values checked | Result |
|---|---|---|
| Enrollment scenarios | Base 3,841 undergraduates in Fall 2030, up from 3,652 in Fall 2026, low 3,632 and high 4,171; online graduate headcount holds at 5,763, 80% range 3,682 to 7,844; footer "latest Oct 28, 2026" | Pass |
| Enrollment scenarios, changed input | 900 freshmen a year gives 4,176 in Fall 2030, 335 above base: 117 more freshmen times (1 + 0.781 + 0.781^2 + 0.781^3) | Pass, run headless with Streamlit's AppTest |
| Registration watch | Oct 28, 2026, opens in 5 days on Nov 2, 509 primary sections across 225 courses; ACCY 410 0 of 14 closed; every section closed in ACCY 321, BADM 303, and BADM 366, as in reports/registration_watch_2027-sp.md | Pass |

Two fixes came out of it. The closed-share chart scaled its day axis to the one status pass and ticked in half days; both registration charts now share one axis of whole days from the first snapshot to opening day. And the marts were cached by name only, which on Community Cloud would have kept serving the first snapshot after later pushes; the cache now keys on the file's modification time.

A second pass that evening, reading it as a first-time visitor would, changed the rest: every page now opens with what the project is and links to the brief, the dashboards, and the code; the registration page opens on all Gies courses, with the Gies-wide closed share, instead of one course; chart titles moved out of the charts, where a phone cut them short and one was clipped under its heading; the scenario tables moved into a Show the numbers section; transfers show as whole students; and the fully closed table gives dates instead of days from opening.

## Not run yet

| Check | Waiting on |
|---|---|
| The app wakes from sleep | 12 hours without traffic |
| The Oct 28 display fixes in Tableau | The Oct 29 morning check |
| The app picks up a new snapshot without a restart | Oct 29: the footer should read Oct 29 once that day's snapshot is pushed |
| Tableau follows the Sheet each day | Oct 29: once Tableau Public syncs, the Registration titles should move from Oct 28 to Oct 29. The public page doesn't show whether sync is on |
| Reading the brief, the guide, and the README aloud | Om |

## Every computed value in the brief

<details>
<summary>159 computed values, their section, and their value on Oct 28, 2026</summary>

| Section | Expression | Value |
|---|---|---|
| Summary | `n.gies_total_first` | 5,155 |
| Summary | `n.FIRST_CHART_FALL` | 2017 |
| Summary | `n.gies_total` | 10,095 |
| Summary | `n.LATEST_FALL` | 2026 |
| Summary | `n.online_added` | 4,781 |
| Summary | `n.gies_added` | 4,940 |
| Summary | `n.undergrad_change_five` | 15.4% |
| Summary | `n.retention_rank` | 7th |
| Summary | `n.biz_share_rank` | 14th |
| Summary | `n.a_range_2025` | 80.0% |
| Summary | `n.GRADES_LAST_FALL` | 2025 |
| Summary | `n.SHIFT_FROM_FALL` | 2015 |
| Summary | `n.word(n.watch_count)` | five |
| Summary | `n.base_2030` | 3,841 |
| Summary | `n.LAST_PROJECTED_FALL` | 2030 |
| Online programs carried Gies's growth | `n.gies_total` | 10,095 |
| Online programs carried Gies's growth | `n.LATEST_FALL` | 2026 |
| Online programs carried Gies's growth | `n.gies_total_first` | 5,155 |
| Online programs carried Gies's growth | `n.FIRST_CHART_FALL` | 2017 |
| Online programs carried Gies's growth | `n.online_added` | 4,781 |
| Online programs carried Gies's growth | `n.gies_added` | 4,940 |
| Online programs carried Gies's growth | `n.online_share` | 89.4% |
| Online programs carried Gies's growth | `n.online_count` | 5,763 |
| Online programs carried Gies's growth | `n.graduate_count` | 6,443 |
| Online programs carried Gies's growth | `n.mba_online` | 3,847 |
| Online programs carried Gies's growth | `n.graduate_peak` | 6,666 |
| Online programs carried Gies's growth | `n.graduate_peak_fall` | 2021 |
| Online programs carried Gies's growth | `n.graduate_decline_five` | 3.3% |
| Online programs carried Gies's growth | `n.undergrad_change_five` | 15.4% |
| Online programs carried Gies's growth | `n.undergrad_total_five_earlier` | 3,165 |
| Online programs carried Gies's growth | `n.undergrad_total` | 3,652 |
| Online programs carried Gies's growth | `n.freshmen_latest` | 901 |
| Online programs carried Gies's growth | `n.first_new_students_fall` | 2012 |
| Online programs carried Gies's growth | `n.freshmen_range_last_fall` | 2023 |
| Online programs carried Gies's growth | `n.freshmen_range_low` | 560 |
| Online programs carried Gies's growth | `n.freshmen_range_high` | 673 |
| Online programs carried Gies's growth | `n.accy_js_then` | 663 |
| Online programs carried Gies's growth | `n.FIVE_FALLS_EARLIER` | 2021 |
| Online programs carried Gies's growth | `n.accy_js_now` | 545 |
| Online programs carried Gies's growth | `n.fin_js_then` | 555 |
| Online programs carried Gies's growth | `n.fin_js_now` | 610 |
| Online programs carried Gies's growth | `n.data_science_first_fall` | 2022 |
| Online programs carried Gies's growth | `n.data_science_js` | 557 |
| Illinois among its Big Ten peers | `n.retention_label` | Fall 2023 cohort returning in fall 2024 |
| Illinois among its Big Ten peers | `n.retention` | 94.8% |
| Illinois among its Big Ten peers | `n.retention_rank` | 7th |
| Illinois among its Big Ten peers | `n.retention_median` | 93.0% |
| Illinois among its Big Ten peers | `n.retention_direction` | rose |
| Illinois among its Big Ten peers | `n.retention_gain` | 1.9 |
| Illinois among its Big Ten peers | `n.retention_then_label` | Fall 2018 cohort returning in fall 2019 |
| Illinois among its Big Ten peers | `n.retention_median_direction` | fell |
| Illinois among its Big Ten peers | `n.retention_median_change` | 0.6 |
| Illinois among its Big Ten peers | `n.grad6_label` | 2018 cohort |
| Illinois among its Big Ten peers | `n.grad6` | 85.1% |
| Illinois among its Big Ten peers | `n.grad6_median` | 85.3% |
| Illinois among its Big Ten peers | `n.gies_grad6` | 92.0% |
| Illinois among its Big Ten peers | `n.grads_matching_cohort` | 2018 |
| Illinois among its Big Ten peers | `n.campus_grad6` | 85.1% |
| Illinois among its Big Ten peers | `n.gies_retention` | 97.3% |
| Illinois among its Big Ten peers | `n.RETENTION_COHORT` | 2025 |
| Illinois among its Big Ten peers | `n.campus_retention` | 94.9% |
| Illinois among its Big Ten peers | `n.applicants` | 73,742 |
| Illinois among its Big Ten peers | `n.admit_label` | Fall 2024 entering class |
| Illinois among its Big Ten peers | `n.applicants_then` | 43,509 |
| Illinois among its Big Ten peers | `n.admit` | 42.4% |
| Illinois among its Big Ten peers | `n.admit_drop` | 16.7 |
| Illinois among its Big Ten peers | `n.admit_then_label` | Fall 2019 entering class |
| Illinois among its Big Ten peers | `n.admit_median` | 58.1% |
| Illinois among its Big Ten peers | `n.yield_rate` | 28.8% |
| Illinois among its Big Ten peers | `n.yield_median` | 22.4% |
| Illinois among its Big Ten peers | `n.biz_share` | 9.5% |
| Illinois among its Big Ten peers | `n.biz_share_label` | July 2024 to June 2025 |
| Illinois among its Big Ten peers | `n.biz_share_rank` | 14th |
| Illinois among its Big Ten peers | `n.biz_share_median` | 16.7% |
| Illinois among its Big Ten peers | `n.biz_masters` | 2,488 |
| Illinois among its Big Ten peers | `n.biz_masters_ratio` | 4.4 |
| Illinois among its Big Ten peers | `n.pell_label` | 2018 cohort |
| Illinois among its Big Ten peers | `n.pell_gap` | 10.9 |
| Illinois among its Big Ten peers | `n.pell_wider_or_narrower` | wider |
| Illinois among its Big Ten peers | `n.pell_gap_median` | 6.3 |
| What course grades can and can't tell an assessment committee | `n.GRADES_FIRST_FALL` | 2010 |
| What course grades can and can't tell an assessment committee | `n.a_range_2010` | 54.4% |
| What course grades can and can't tell an assessment committee | `n.gpa_2010` | 3.38 |
| What course grades can and can't tell an assessment committee | `n.GRADES_LAST_FALL` | 2025 |
| What course grades can and can't tell an assessment committee | `n.a_range_2025` | 80.0% |
| What course grades can and can't tell an assessment committee | `n.gpa_2025` | 3.72 |
| What course grades can and can't tell an assessment committee | `n.graded_2025` | 13,070 |
| What course grades can and can't tell an assessment committee | `n.campus_a_2010` | 48.6% |
| What course grades can and can't tell an assessment committee | `n.campus_a_2025` | 69.8% |
| What course grades can and can't tell an assessment committee | `n.campus_gpa_2010` | 3.21 |
| What course grades can and can't tell an assessment committee | `n.campus_gpa_2025` | 3.52 |
| What course grades can and can't tell an assessment committee | `n.gies_trend` | 1.9 |
| What course grades can and can't tell an assessment committee | `n.campus_trend` | 1.6 |
| What course grades can and can't tell an assessment committee | `n.SHIFT_FROM_FALL` | 2015 |
| What course grades can and can't tell an assessment committee | `n.SHIFT_TO_FALL` | 2025 |
| What course grades can and can't tell an assessment committee | `n.shift_total` | 21.7 |
| What course grades can and can't tell an assessment committee | `n.shift_courses` | 48 |
| What course grades can and can't tell an assessment committee | `n.shift_within` | 17.5 |
| What course grades can and can't tell an assessment committee | `n.shift_mix` | 0.5 |
| What course grades can and can't tell an assessment committee | `n.shift_interaction` | 1.6 |
| What course grades can and can't tell an assessment committee | `n.shift_entering` | 2.2 |
| What course grades can and can't tell an assessment committee | `n.dfw_2025` | 1.4% |
| What course grades can and can't tell an assessment committee | `n.word(n.watch_count)` | five |
| What course grades can and can't tell an assessment committee | `n.watch_min_graded` | 150 |
| What course grades can and can't tell an assessment committee | `n.watch_min_rate` | 15% |
| What course grades can and can't tell an assessment committee | `n.word(n.watch_min_terms)` | two |
| What course grades can and can't tell an assessment committee | `n.watch_courses` | ACCY 201, ACCY 202, ACCY 301, ACCY 303, and FIN 300 |
| What course grades can and can't tell an assessment committee | `n.watch_top_rate` | 23.3% |
| What course grades can and can't tell an assessment committee | `n.watch_top_course` | FIN 300 |
| What course grades can and can't tell an assessment committee | `n.spread_max` | 1.04 |
| Where scheduling is tight | `n.sections_2025` | 518 |
| Where scheduling is tight | `n.SECTIONS_TO_FALL` | 2025 |
| Where scheduling is tight | `n.sections_2019` | 480 |
| Where scheduling is tight | `n.SECTIONS_FROM_FALL` | 2019 |
| Where scheduling is tight | `n.students_2019` | 21,795 |
| Where scheduling is tight | `n.students_2025` | 30,067 |
| Where scheduling is tight | `n.per_section_2019` | 55.9 |
| Where scheduling is tight | `n.per_section_2025` | 69.8 |
| Where scheduling is tight | `n.word(n.fewer_sections_count)` | five |
| Where scheduling is tight | `n.fewer_sections_list` | ACCY 500, ACCY 505, BADM 509, BADM 572, and FIN 321 |
| Where scheduling is tight | `n.snapshot_date` | Oct 28, 2026 |
| Where scheduling is tight | `n.registration_sections` | 509 |
| Where scheduling is tight | `n.registration_courses` | 225 |
| Where scheduling is tight | `n.registration_status` | registration opens in five days, on Nov 2, 2026 |
| Where scheduling is tight | `n.fully_closed` | ACCY 321, BADM 303, BADM 366 |
| Where scheduling is tight | `n.closed_sections` | 12 |
| Where scheduling is tight | `n.sections_with_status` | 509 |
| Where scheduling is tight | `n.closed_share` | 2.4% |
| Outlook | `n.base_freshmen` | 783 |
| Outlook | `n.base_transfers` | 83 |
| Outlook | `n.intake_first_fall` | 2024 |
| Outlook | `n.LATEST_FALL` | 2026 |
| Outlook | `n.base_c_pct` | 78.1% |
| Outlook | `n.base_2030` | 3,841 |
| Outlook | `n.LAST_PROJECTED_FALL` | 2030 |
| Outlook | `n.low_2030` | 3,632 |
| Outlook | `n.high_2030` | 4,171 |
| Outlook | `n.BACKTEST_FIRST_ORIGIN` | 2016 |
| Outlook | `n.model_1yr` | 2.8% |
| Outlook | `n.model_4yr` | 4.2% |
| Outlook | `n.naive_1yr` | 2.9% |
| Outlook | `n.naive_4yr` | 4.7% |
| Outlook | `n.actual_intake_1yr` | 1.5% |
| Outlook | `n.FRESHMEN_LEVER` | 50 |
| Outlook | `n.plus_50_freshmen` | 143 |
| Outlook | `n.plus_point_c` | 109 |
| Outlook | `n.freshmen_latest` | 901 |
| Outlook | `n.freshmen_hold` | 4,180 |
| Outlook | `n.online_count` | 5,763 |
| Outlook | `n.online_low_2030` | 3,682 |
| Outlook | `n.online_high_2030` | 7,844 |
| Outlook | `n.il_grads_2025` | 144,561 |
| Outlook | `n.WICHE_FROM` | 2025 |
| Outlook | `n.il_grads_2035` | 119,005 |
| Outlook | `n.WICHE_TO` | 2035 |
| Outlook | `n.il_grads_decline` | 17.7% |
| Outlook | `n.in_state_yield_2025` | 45.4% |
| Outlook | `n.in_state_admit_2035` | 59.9% |
| Outlook | `n.in_state_admit_2025` | 49.3% |

</details>
