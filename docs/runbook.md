# Runbook

## Downloading DAIR crosstabs

DAIR publishes enrollment, student type, and retention as Tableau dashboards, so there is no file to fetch and these downloads are done by hand: once now, then once each fall after DAIR posts the new term. Save every file to data/manual/dair/ under the name given. On each dashboard the download control is below the dashboard on the right: Download, then Crosstab, then the sheet named below, then CSV. If a filter named here isn't offered, leave it at its default and note that in the file name; the ingest filters to Gies itself.

### 1. Enrollment by curriculum and level

Statistical Abstract: https://dair.illinois.edu/access-data/statistical-abstract/

1. Open the Data Table - Curriculum and Level tab.
2. Set Semester to Fall 2026 and College to Gies College of Business.
3. Download the sheet Table Curriculum and Student Level as curriculum_level_fa2026.csv.
4. Repeat for Fall 2025 as curriculum_level_fa2025.csv. Fall 2025 is also in the archived DMI report, so the two can be reconciled.

### 2. Undergraduate student types by class

Same dashboard.

1. Open the College, Class, Type tab.
2. Set Semester to Fall 2024, College to Gies College of Business, and Compare to Undergraduates by Class.
3. Download the sheet Class,Level,Year as college_class_type_fa2024.csv.
4. Repeat for Fall 2025 and Fall 2026. Fall 2024 fills the ten-day abstract the archive never captured.

### 3. Online programs

Student Enrollment: https://dair.illinois.edu/access-data/student-enrollment/

1. Open the Data Table tab.
2. Set Term to Fall 2026, College to Gies College of Business, Online Program to Yes, and Compare Data Table to Student Level.
3. Download the sheet Enrollment Data Table as online_programs_fa2026.csv. The crosstab dialog lists Data Table Title first; pick Enrollment Data Table, or the file holds only the title.
4. Repeat for Fall 2025. The academic program codes in these files settle the modality column in config/program_map.csv.

### 4. Retention and graduation by college of entry

Retention and Graduation Rates: https://dair.illinois.edu/access-data/retention-and-graduation-rates/

1. Open the Retention Data Table tab. Select every Fall Cohort and every College At Entry, so Gies can be compared with campus.
2. Download the sheet Retention Rates by College Data Table as retention_by_entry_college.csv.
3. Open the Graduation Rate Data Table tab with the same selections.
4. Download the sheet Graduation Rates by College Non-Cumulative Data Table as graduation_by_entry_college.csv. It carries graduate counts by year group, so four- and six-year rates can be computed from counts.

## The daily snapshot

.github/workflows/snapshot.yml reads the Spring 2027 Gies sections from the Course Explorer API at 13:07 UTC, with a backup run at 19:37 UTC that exits if the day's file exists. It writes data/snapshots/cis/2027-sp/ under the Central date, the day the snapshot describes, since the job often starts hours late and an evening run is already the next day in UTC. It fails without writing if a Gies subject returns no sections, a CRN appears twice, or the section count moves more than 20% from the previous day's. It then rebuilds the registration watch and its report, commits, and writes the mart_registration_watch tab of the Google Sheet, which Tableau Public reads once a day. The Sheet step runs after the commit, so a Sheets error leaves the snapshot in place; the next run or the Monday refresh republishes the tab. The API shows only the current state, so a day with no successful run can't be filled in later.

## The daily status pass

.github/workflows/status.yml reads enrollment status from the Gies course pages once a day, on the terms Tech Services approved on Oct 26, 2026: two seconds between requests and a start at 8:14 am Central. GitHub starts this repo's scheduled jobs two to six hours late and ends any job after six hours, so the workflow starts the evening before, at 0:20 and 2:20 UTC, and relays. A run more than five hours from 8:14 sleeps up to 5 hours 15 minutes, making no request, then starts a fresh run, which begins within seconds; the run within five hours of 8:14 waits for it and does the pass. Morning runs at 9:20, 11:20, and 13:20 UTC are backups. The script runs only between 8:14 and 8:44 Central, so a run that starts later exits without a request, and a run that finds the day's file exits. A normal night shows two or three status runs in the Actions tab, each lasting about five hours, plus some marked cancelled: GitHub keeps one run pending behind the running one and cancels any older pending run, which is expected. If a morning has no status file, look for a red run in that night's chain. To check the hand-off itself at any hour, run the workflow by hand with check relay ticked: that run reads nothing and only starts a fresh run, which finds 8:14 too far off and exits. The pass takes its course list from the latest API snapshot in its checkout, makes about 250 requests over roughly ten minutes, and commits data/snapshots/cis_status/2027-sp/ with each CRN and its status; a second job then rebuilds the registration watch and writes it to the Sheet. It stops by itself after the last day to add in config/registration.csv.

Never run it outside that window, by hand or otherwise. If a run fails with an HTTP 202 and an empty body, the site's bot protection has challenged it: do not retry or change the request pattern; write to Tech Services, who approved the pass, and ask them to allow it.

## Starting a new registration term

The registration watch is built for Spring 2027. For another term:

1. Ask Tech Services again before reading the course pages for the new term. Their Oct 26, 2026 approval covers the Spring 2027 Gies pages through Feb 1, 2027.
2. Add a row to config/registration.csv with the term, the first day of registration, and the last day to add.
3. In ingest/cis_snapshot.py, set TERM and the year and semester in API_BASE; in ingest/cis_status.py, the year and semester in WEB_BASE. Snapshots for the new term land in their own folders under data/snapshots/.
4. Rename the report in publish/registration_report.py and the files the workflows commit.
5. Run make snapshot once by hand to check the API, then let the scheduled jobs take over. The status pass needs no test run: never run it outside 8:14 to 8:44 Central.

## The weekly refresh

.github/workflows/refresh.yml runs Mondays at 11:17 UTC and can be started by hand from the Actions tab (refresh, then Run workflow). It sends a HEAD request for every source in data/extracts/manifest.csv and treats a source as changed when its Last-Modified or ETag differs from the manifest. It reruns the ingest for changed sources only, then runs dbt build, the forecast, the export, and pytest. It publishes to the Google Sheet only if all of them pass, appends a row per mart to mart_refresh_log, and commits.

When a check fails, the run commits only its log row (published is false), leaves the Sheet and the rest of main untouched, and fails, so GitHub sends an email. The run page shows which step failed.

## When the refresh opens an issue

The refresh lists new upstream files but never ingests them by itself. An issue titled "New upstream files: ..." means one of two things.

- A new IPEDS file, such as ADM2025. Read its dictionary first: check that every variable the staging model for its family uses is still there with the same meaning, and record it in docs/ipeds_variables.md. Copy the file's URL and its dictionary's from the IPEDS Data Center year page into config/ipeds_files.csv, add the collection's release to config/ipeds_releases.csv as provisional, then run make ingest and make build.
- A new course catalog term, such as 2027-sp. Add it to TERMS in ingest/catalog.py and update the count the module asserts, then run python -m ingest.catalog and make build.

Close the issue once the file is in.

## When NCES finalizes a collection

NCES releases provisional data first and revised, final data about a year later. The refresh notices the revised files, because their ETags change, and re-ingests them. The provisional flag comes from config/ipeds_releases.csv, so change that collection's release_type to final by hand when NCES's release schedule (nces.ed.gov/ipeds/survey-components/data-release-schedule) says the final files are out.

## Sources the refresh can't check

The DMI pages are frozen Internet Archive captures. The DAIR crosstabs (above) and the Common Data Set files (data/manual/cds_c1_checklist.md) are downloaded by hand once a year, after each fall's data is posted.

## Keeping the scheduled workflows running

GitHub disables scheduled workflows in a public repository after 60 days without activity. The daily snapshot commits and the weekly refresh commits keep this one active. If a workflow ever shows as disabled, open the Actions tab, pick the workflow, and choose Enable workflow.

## The Streamlit app

Community Cloud redeploys the app on every push to main, so the registration page updates with each daily snapshot. The app sleeps after 12 hours without traffic, and anyone can wake it with one click. Open it yourself before sending the link or walking into an interview.

## Publishing by hand

make publish writes every mart in data/marts to the Google Sheet. It needs SHEET_ID set to the Sheet's ID and the service account key at ~/.config/gies-program-health/sa.json, or its contents in GCP_SA_KEY.
