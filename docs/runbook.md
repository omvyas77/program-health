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
