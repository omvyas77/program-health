# Data sources

Every source this project reads, where it comes from, and what version is in use. Exact URLs, retrieval times, ETags, and SHA-256 hashes for every downloaded file are in data/extracts/manifest.csv.

## IPEDS Complete Data Files

The National Center for Education Statistics publishes one zip per survey file and year, with a dictionary zip beside it. Since late 2025 the IPEDS Data Center links years up to 2022 to nces.ed.gov/ipeds/datacenter/data/ and 2023 onward to nces.ed.gov/ipeds/complete-data-files/; the old folder still holds stale copies of the 2023 files. config/ipeds_files.csv lists the 72 files used, each with the URL the Data Center gives for it. config/ipeds_releases.csv copies NCES's release schedule (nces.ed.gov/ipeds/survey-components/data-release-schedule) and drives the provisional flag. Variables and data years are documented in docs/ipeds_variables.md.

IPEDS is institution-level. It gives Illinois's campus-wide retention and graduation rates, not Gies's.

## UIUC GPA dataset

wadefagen/datasets on GitHub, gpa/uiuc-gpa-dataset.csv, read at commit c6618ca (Oct 15, 2026); the file itself last changed on Mar 25, 2026. One row per section with 21 or more graded students, from Spring 2010 to Winter 2026. Data through Fall 2024 came from FOIA requests; from Spring 2025 it comes through Senate item EP.25.072. The Primary Instructor column is dropped at ingest.

## Course catalog

wadefagen/datasets, course-catalog/data/{term}.csv, at the same commit: 40 terms from 2016-fa to 2026-fa, with no 2016-sp, 2016-su, 2016-wi, or 2017-wi file. Each file was scraped at a different time, so its Enrollment Status reflects that moment and is not trended. Only Gies subjects are kept, and instructors are dropped.

## Course Explorer API

courses.illinois.edu/cisapp/explorer, documented as public with no authentication (answers.illinois.edu/88215). The daily snapshot reads the Spring 2027 section list for the six Gies subjects. The API carries no enrollment status; see docs/data_notes.md.

## Course Explorer course pages

courses.illinois.edu/schedule/2027/spring/{subject}/{number}. The pages show each section's availability (Open, Closed, Open (Restricted)), which the API doesn't. On Oct 26, 2026, the university's Tech Services approved one automated pass a day over the Gies course pages, with two seconds between requests and a start at 8:14 am Central, between their status updates. ingest/cis_status.py makes that pass from Oct 28, 2026 (the Oct 27 pass never ran) through Feb 1, 2027, the last day to add, and keeps only each CRN and its status in data/snapshots/cis_status/.

## DMI enrollment reports, through the Internet Archive

The Division of Management Information published two fall reports this project uses: Enrollment by Curriculum and Class Level (stuenr/class/enrfaYY.htm) and the Statistical Abstract of Ten-Day Enrollment (stuenr/abstracts/faYY_ten2.htm). DMI's site now redirects to DAIR, so Fall 2012 to Fall 2025 come from the Internet Archive's copies of the original pages. config/dmi_pages.csv pins the capture used for each page. The ten-day abstract for Fall 2024 was never captured.

## DAIR dashboards

Data, Analytics, and Institutional Research (dair.illinois.edu) took over DMI's reports as public Tableau dashboards. Three are used, with crosstabs downloaded by hand into data/manual/dair/ on Oct 23, 2026 (steps in docs/runbook.md) and read by ingest/dair.py:

- Statistical Abstract (dair.illinois.edu/access-data/statistical-abstract/), Fall 2004 to Fall 2026. Its Data Table - Curriculum and Level sheet replaces DMI's curriculum report, and its College, Class, Type sheet replaces the ten-day abstract. Used for Fall 2026, for Fall 2024 student types, and to reconcile Fall 2025 against the archived DMI pages.
- Student Enrollment (dair.illinois.edu/access-data/student-enrollment/), Fall 2013 to Fall 2026. Its Online Program filter identifies which Gies programs are online.
- Retention and Graduation Rates (dair.illinois.edu/access-data/retention-and-graduation-rates/). First-fall to second-fall retention and four-, five-, and six-year graduation rates for first-time, full-time, degree-seeking undergraduates, by entering college. This answers whether Gies-level rates are public: they are, by college of entry.

## Common Data Set

Each school publishes its own Common Data Set; config/cds_files.csv lists the file used for 2024-25 (Fall 2024) and 2025-26 (Fall 2025), the official page it was found on, and any note about scope. Formats differ: PDF for most, Excel for Illinois, Maryland, Purdue, and Wisconsin's 2025-26, and web pages for Indiana and Nebraska. Rutgers-New Brunswick has not published a CDS since 2023-24. Section C1 (first-time, first-year applicants, admits, and enrolled, with the residency split where reported) is drafted by ingest/cds.py into data/manual/cds_c1_draft.csv and verified by hand against each file into data/manual/cds_c1.csv; data/manual/cds_c1_checklist.md lists every file and where to look.

## WICHE Knocking at the College Door

The 11th edition projections dataset (December 2024), from wiche.edu/knocking/data/. The workbook was relabeled on Jan 31, 2025 with no values changed. High school graduates, actual and projected, for Illinois, the nation, and both Midwest definitions the file carries.

## Teachers Ranked as Excellent

wadefagen/datasets, teachers-ranked-as-excellent/uiuc-tre-dataset.csv, at the same commit, through Summer 2025. The file lists instructors by name, so it is counted by term, unit, and role at ingest and names never leave data/raw.
