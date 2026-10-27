# Decisions

The choices that shape what this project says, newest last, each with the reason. Where a decision is explained at length elsewhere, the entry points there.

## The stack (Oct 22, 2026)

**DuckDB and dbt, not a hosted warehouse.** The data is small: the largest mart has about 6,500 rows and the whole warehouse is one file. DuckDB runs inside the pipeline, costs nothing, and lets anyone rebuild everything from a clone with make all. dbt keeps every transformation in SQL with tests and enforced column contracts, which is how I'd work in a campus warehouse too, so the models would move to Snowflake or BigQuery with little change. What I give up, concurrent users and scheduled queries inside the warehouse, this project doesn't need.

**A Google Sheet between the pipeline and Tableau Public.** Tableau Public can't connect to a database. It saves an extract with each workbook and refreshes it on its own only from Google Sheets. So the weekly refresh writes each mart to a tab of one Sheet, and the dashboards read the Sheet. The dbt contracts on the exported marts exist because the workbook depends on those column names.

**No AWS and nothing paid.** GitHub Actions runs the schedules, Streamlit Community Cloud hosts the app, Tableau Public hosts the dashboards, and Google Sheets carries the data between them, all free for a public project. Anyone can see and rerun every piece, and nothing depends on an account I'd have to keep paying for.

**Streamlit only for the scenarios and the registration watch.** Tableau carries the standing views. Two things it handles poorly: inputs that rerun a model, like the enrollment scenarios, and data that changes every day, like registration. Tableau Public refreshes once a day at best and can't run Python. The app reads the committed marts and redeploys on every push, so it picks up each day's snapshot.

**Graduation rates from GR, not DRVGR.** DRVGR exists only from 2021, while the GR files go back to the 2008 cohort and carry the counts: the adjusted cohort and the completers by year. With counts, every rate is computed the same way across all years, and the GR cohorts check out against the fall cohorts EF D reports six years earlier.

## Data (Oct 23, 2026)

**Penn State's 2019 to 2021 IPEDS collections are left out,** because they describe all its campuses together, about twice the size of the main campus. Peer medians use the other schools for those years. See data_notes.md.

**Online campuses are compared as reported.** Illinois reports its online programs under its own IPEDS ID; Penn State World Campus and Purdue Global report separately. The online-share charts say so.

**Program families and modality.** A family is the degree and major; a program code ending in U is online, which matches DAIR's online flag for every Gies code in Fall 2025 and Fall 2026. See config/program_map.csv and data_notes.md.

**Purdue's 2024-25 CDS admits total is kept as filed,** with a note that its parts add up to the IPEDS figure instead.

**The registration watch started on the API only,** and I asked the Registrar for access to section status rather than work around the course pages' bot protection. Tech Services approved a daily pass on Oct 26 (below).

## Marts and findings (Oct 24, 2026)

**Business completions count CIP 52 codes and, as a separate version, 30.7102 Business Analytics,** which exists only in the 2020 CIP classification. Both versions are reported.

**A C-or-below-or-W rate sits beside the DFW rate,** because D, F, and W grades are too rare in Gies undergraduate courses (1.4% in Fall 2025) to separate courses.

**The course watch list** is courses averaging 150 or more graded students per term offered, with 15% or more at C or below or withdrawing in at least two of the last four long terms. The thresholds live in transform/dbt_project.yml.

**Online and in-person sections are compared from Fall 2018 on,** the first fall after four terms with no schedule type at all.

## Projection (Oct 24, 2026)

**Covid transitions are left out of the continuing share:** into Fall 2020 and into Fall 2021. **Intake is the three-year mean,** which matched the naive forecast in the backtest while holding the latest fall lost to it at every horizon. **The online series uses exponential smoothing without a trend,** because the damped trend carried the programs' launch forward and lost to the naive forecast at every horizon. See projection_method.md.

## Publishing and dashboards (Oct 25, 2026)

**New IPEDS files and new catalog terms open an issue instead of being ingested,** because a new year's dictionary has to be read first: no IPEDS variable name is guessed.

**Illinois's rank in business degrees uses the business share of bachelor's degrees,** 14th of 18, not the count, which mostly reflects each university's size.

**Students per section divides by primary sections from the catalog,** not by the GPA data's sections, because grades moved from discussion sections to lectures over these years. See data_notes.md.

## Registration status (Oct 26, 2026)

**Tech Services approved one pass a day over the Gies course pages:** two seconds between requests, starting at 8:14 am Central, through Feb 1, 2027. GitHub starts scheduled jobs hours late, so the job starts early and waits until 8:14, and it skips a day rather than start after 8:44. Closed share counts sections marked Closed; Open (Restricted) counts as open. See data_notes.md and runbook.md.

**The registration watch reaches the Sheet every day,** written by the snapshot and status jobs after they commit, while every other tab still waits for the Monday refresh. Tableau Public reads the Sheet once a day, and registration is the one dataset that changes daily.

**The daily jobs run a test only when they built everything it reads** (dbt's cautious selection). They build the registration watch alone, and a test that also reads the course marts broke both Oct 26 snapshot runs.
