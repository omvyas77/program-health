# Data notes

Quirks in the sources and what I did about each. Dated by when I found them.

## IPEDS

**Penn State's reporting unit changes for three collection years (Oct 23, 2026).** In the 2019-20 winter and spring collections, Penn State reported all of its campuses under the main campus UNITID, 214777. In 2020-21 and 2021-22 it reported them under a new UNITID, 495767, "The Pennsylvania State University", which no longer appears in the directory. From 2022-23 on, 214777 covers University Park only. The all-campus figures are about twice the size: 15,989 first-year students enrolled in fall 2019 against 8,075 in fall 2018 and 9,216 in fall 2022, and full-time retention of 87 to 88% against 91 to 93% in the years around them. I left Penn State out of every file from those collections rather than map 495767 to 214777, because the numbers describe a different institution. That covers ADM, EF D, GR, EF A_DIST, and GR_PELL_SSL for 2019 to 2021, C for 2020 and 2021, and EF CP for 2020 (it is reported in even years only). C2019_A comes from the fall 2019 collection, before the change, and stays. In those years the peer median is the median of the other 16 schools, and charts show Penn State as missing with a note.

**Online campuses are reported in different ways (Oct 23, 2026).** Illinois reports its online programs, the iMBA among them, under its own UNITID, so 40.1% of its graduate students were exclusively online in fall 2024. Penn State reports World Campus as a separate institution (479956), and Purdue Global reports as its own institution (489779). I compare each school as reported and say on the online-share charts that Penn State's and Purdue's online students sit outside the main campus figures. The University of Maryland Global Campus (163204) is a separate university in the Maryland system, not part of College Park, so it doesn't apply.

**Five dictionaries contradict themselves about the year (Oct 23, 2026).** GR2020, GR2024, GR2024_PELL_SSL, GR2021_PELL_SSL, and C2022_A each carry one title, label, or description that disagrees with the rest of the file. docs/ipeds_variables.md lists them and the label I used. The data settles the graduation files: every GR file's cohort matches the full-time cohort EF D reports six falls earlier, with median ratios of 0.999 to 1.000, so GR2020 is the 2014 cohort and GR2024 is the 2018 cohort.

**Older files pad their codes (Oct 23, 2026).** Files up to 2019 write AWLEVEL as "05" and GRTYPE and EFDELEV with a leading space (" 2"). The extracts keep the source text unchanged; staging trims and casts every code to an integer.

**Completions files carry a grand-total row (Oct 23, 2026).** CIPCODE "99" holds the total across all fields and equals the sum of the other codes. Sums leave it out, and it stays as a cross-check.

**Two definition changes break trends (Oct 23, 2026).** The retention cohort adds inclusions from fall 2017 on, so rates before and after aren't strictly comparable. Completions switch from the 2010 to the 2020 CIP classification in C2020_A, and 30.7102, Business Analytics, exists only from 2019-20 awards on.

## DMI and DAIR

**DMI's reports moved to DAIR (Oct 23, 2026).** Every dmi.illinois.edu/stuenr/ page now redirects to the DAIR homepage. Fall 2012 to Fall 2025 come from the Internet Archive's copies of the original DMI pages, pinned in config/dmi_pages.csv; Fall 2026 and the missing Fall 2024 student types come from DAIR's Statistical Abstract dashboard. The archived Fall 2025 pages reproduce every anchor checked before the build exactly: 9,640 Gies students, 3,329 undergraduate and 6,311 graduate, 3,572 in the MBA, 1,030 in Business Undeclared, 787 first-time freshmen, and 84 new transfers.

**The curriculum report changed shape in Fall 2020 (Oct 23, 2026).** From Fall 2012 to Fall 2019 it has 20 columns. Fall 2020 adds full-time and part-time counts for undergraduate, graduate, professional, and total, for 28. Columns are matched by their header text, so both layouts load into one table with the new columns empty before Fall 2020.

**Every fall's curricula add up to DMI's college total (Oct 23, 2026).** The ingest checks it and stops if any fall disagrees. None does.

**Undergraduate majors appear twice (Oct 23, 2026).** Most BS majors are listed once under their own academic program code and again under 10KM8037BS. In Fall 2025 Finance has 351 students under 10KM0075BS and 298 under 10KM8037BS. Both rows count toward the college total, so they are different students. DMI does not say what 10KM8037BS means, and config/program_map.csv leaves it marked.

**A program code ending in U marks an online program (Oct 23, 2026).** DAIR's Student Enrollment dashboard flags every program as online or not (data/manual/dair/online_programs_*.csv). In Fall 2025 and Fall 2026 all 23 online codes end in U (the 3,572-student MBA, 10KS9875MBAU, among them) and none of the 23 other codes does. config/program_map.csv uses that rule, and for the 36 older curricula DAIR doesn't list, modality is inferred from it and the row says so.

**The Fall 2024 ten-day abstract is missing from the archive (Oct 23, 2026).** It was never captured. DAIR's College, Class, Type sheet fills it: 661 first-year students and 79 new transfers. DAIR labels first-time freshmen "First Year Student"; the numbers are the same students, as Fall 2025 shows (787 in both).

**DAIR and the archived DMI pages agree for Fall 2025 (Oct 23, 2026).** All 61 Gies curricula match on total headcount and on juniors plus seniors, and the college totals match: 9,640 students, 3,329 undergraduate and 6,311 graduate. Student types match too.

**DAIR's exports have their own quirks (Oct 23, 2026).** Files are UTF-16 and tab-separated. The curriculum sheet exports either one row per curriculum and level or one column per level, depending on how it is downloaded; the ingest reads both. The doctoral column is labeled "Grad 2 (Master)" but holds the PhD students (64 in Fall 2025). In the graduation file the label "Size of Adjusted Cohort" appears twice: the copy followed by two spaces holds the cohort size, and the other repeats the graduate count. Its year groups are not cumulative, so a six-year rate adds the 3-, 4-, 5-, and 6-year groups. The retention file's "Avg. Retention Rate" row reads 1 throughout and is ignored in favor of the counts.

**Every online program on campus follows the U convention (Oct 23, 2026).** DAIR's Online Program filter, downloaded for all colleges, lists 100 online program codes in Fall 2025 and 108 in Fall 2026, and every one ends in U.

**How config/program_map.csv groups programs (Oct 23, 2026).** A family is the degree plus the major; the "+ Data Science" majors are their own families, concentrations roll up to their major, and renamed majors stay separate with a note where one appears to succeed another. Rows under 10KM8037BS count toward their major. Certificates, nondegree students, the MBA, and the PhD are one family each.

**Gies has no online program code before Fall 2017 (Oct 24, 2026).** The archived curriculum reports for Fall 2012 to Fall 2016 list no Gies code ending in U. The online codes campus-wide in Fall 2016 belong to other colleges, among them Crop Sciences, Computer Science, and Education. The online MBA, 10KS9875MBAU, first appears in Fall 2017 with 787 students, so the online share of Gies graduate headcount goes from zero in Fall 2016 to 47.9% in Fall 2017.

## Other sources

**The catalog has gaps before Fall 2017 (Oct 23, 2026).** There is no 2016-sp, 2016-su, 2016-wi, or 2017-wi file, so the 40 terms start with 2016-fa.

**WICHE's file carries two Midwests (Oct 23, 2026).** WICHE's own Midwest (code _M) and the Census Bureau's (code CM) both fall 16% from the class of 2023 to the class of 2041: 760,548 to 638,923 and 777,916 to 657,001. I use WICHE's, since the findings quoted are WICHE's.

**One more subject might belong to Gies (Oct 23, 2026).** The Course Explorer API lists exactly six subjects under Gies's college code, KM: ACCY, BADM, BDI, BUS, FIN, and MBA, which match config/gies_subjects.csv. DTX, Human-Centered Design and Design Thinking, lists Business Administration as its unit but college code KP. It is not added, because it belongs to another college.

## GPA dataset

**13% of Gies sections have no schedule type (Oct 24, 2026).** 1,248 of the 9,675 Gies sections leave Sched Type blank, so they can't be called online or in person. Nearly all of them come from four whole terms, 2016-fa, 2017-sp, 2017-fa, and 2018-sp, where the field is blank on every row campus-wide; Fall 2018 is complete. The online and in-person comparison starts there. One more, in 2010-sp, has the code Q, which no catalog term defines. All 1,249 (60,119 graded students) are counted under mode "unknown" and left out of the online and in-person comparison rather than guessed. ST and RES, which appear elsewhere in the file, never appear in Gies rows.

**Where grades are recorded changed over time (Oct 25, 2026).** The GPA data lists each section that recorded grades, and that was sometimes the discussion rather than the lecture. In Fall 2019, 40 of the 346 Gies sections in the data were discussion-type; by Fall 2025 none were. ACCY 201 ran 3 primary sections in both falls, but its grades sat under 20 sections in Fall 2019 and 2 in Fall 2025. Counts of graded sections, and anything divided by them, move with this bookkeeping as well as with class size.

**The source has no Spring 2012 (Oct 28, 2026).** The dataset's changelog for Mar 25, 2026 says the rows labeled Spring 2012 were a copy of Summer 2012 and were removed. The extract has 2012-su and 2012-fa and nothing for 2012-sp; Summer 2011 is missing too. On a chart with one bar per term name, 2011-fa sits next to 2012-fa with no visible gap, so the Grades dashboard's definitions say so. Trends by fall are unaffected.

## Course catalog and TRE

**Some sections carry two primary meeting types (Oct 24, 2026).** 60 of the 10,795 primary sections in the catalog files list two primary types in the same term; 49 of them pair a lecture-discussion with an online meeting. Sections offered are counted as distinct CRNs, so each counts once.

**TRE switches its unit names to mixed case in Spring 2024 (Oct 24, 2026).** ACCOUNTANCY becomes Accountancy, and so on. The two spellings never appear in the same term, so units are matched without case. Business and Technical Writing is an English unit and is left out of Gies counts.

**BUS has more TA listings than sections (Oct 24, 2026).** In Falls 2017 to 2019 TRE lists 54 to 60 BUS teaching assistants against 37 to 42 primary BUS sections, and 40 to 45 sections of every type. BUS TA listings drop to nearly none from Fall 2020 on.

## Common Data Set

**Fall 2024 CDS totals match IPEDS ADM2024 almost everywhere (Oct 23, 2026).** Of 51 comparisons (17 schools, three counts each), 44 match exactly and 50 are within 1%. The small differences are Maryland (14 fewer applicants, 5 fewer admits), Wisconsin (39 more applicants, 2 more admits), Washington (1 fewer enrolled), and UCLA (4 more applicants). These are from the draft and are rechecked once each value is verified.

**Purdue's 2024-25 file states the wrong admits total (Oct 23, 2026).** Its C1 total for admits reads 30,272, the same number as its women applicants. Its in-state, out-of-state, and international admits add up to 39,272, which matches IPEDS. The draft keeps the file's number and flags it. Purdue's CDS covers West Lafayette, Purdue in Indianapolis, and Polytechnic Statewide from 2024-25 on, yet its Fall 2024 applicants and enrolled match IPEDS 243780 exactly, so the two report the same scope for that year.

**Not every school reports the residency split (Oct 23, 2026).** Michigan, Northwestern, UCLA, Oregon's 2024-25 file, USC's 2024-25 file, and Wisconsin's 2024-25 file leave it blank. Maryland reports in-state and out-of-state only; the two add up to its total, so international students sit inside one of them. Minnesota's 2024-25 file reports 5,769 applicants and 4,419 admits of unknown residency.

**Some PDFs can't be read as text (Oct 23, 2026).** Ohio State's two files and UCLA's 2024-25 file draw their numbers as shapes. Their values were read from rendered page images (data/manual/cds_c1_image_reads.csv) and, for Ohio State, agree three ways: the residency parts, the residency total, and the gender rows. UCLA's 2024-25 gender rows sum to 146,276 applicants, 4 more than IPEDS.

**Illinois's and Wisconsin's 2025-26 workbooks carry a broken answer list (Oct 23, 2026).** Beside the form on the CDS-C sheet, and on the Answer Sheet tab, a list of field codes and values runs one row out of step from the full-time and part-time rows on, with #REF! errors in places. Only the form itself is read.

**Penn State's CDS page links a dead folder (Oct 23, 2026).** Its link goes to a SharePoint folder that returns 404. The University Park files used are on the same office's site, found by search.

## Course Explorer

**The public API has no enrollment status (Oct 23, 2026).** No response from the Course Explorer API carries enrollmentStatus, for Spring 2027 or Fall 2026, in cascade, detail, or section mode. The availability shown on the public course pages (Open, Closed, Open (Restricted)) is the field the registration watch was built on, but those pages sit behind bot protection that began returning empty responses to a script after several hundred requests. The daily snapshot records the section list from the API only, so it shows sections added and removed during registration but not which sections are closed.

**Tech Services approved a daily pass over the course pages (Oct 26, 2026).** I asked the Registrar whether a supported route to section status existed, or whether one automated pass a day would be acceptable. Tech Services confirmed the API has no status field and approved the pass on two conditions: two seconds between requests, and a start at 8:14 am Central, which falls between their status updates. GitHub starts scheduled jobs hours late, so the job starts the evening before and waits, making no request, until 8:14 (runbook.md); it runs only between 8:14 and 8:44 Central and skips a day rather than start later. If bot protection ever challenges it, the pass stops with nothing written for that day. Closed share counts sections marked Closed; Open (Restricted) means seats held for certain students and counts as open. A closed section isn't necessarily full.

**Some sections have no section number (Oct 23, 2026).** The API lists 13 independent study sections in Spring 2027 with no section number, for example ACCY 199, CRN 10033. The snapshot writes them with a blank section.

**A few sections mix meeting types (Oct 23, 2026).** ACCY CRNs 71766 and 77038 each have a Lecture-Discussion meeting and an Online Lab meeting. The snapshot keeps both codes, as "LCD;OLB".

**No snapshot for Oct 27, 2026.** Both of Oct 26's scheduled snapshot runs failed after reading the API, so neither committed its file. The rebuild selects only the registration watch's models, and dbt's default test selection also picked a test that reads mart_course_sections, which that job never builds; it surfaced once the status columns made the watch depend on int_type_codes. Both workflows now pass --indirect-selection cautious, which runs a test only when everything it reads was built. The fixed job, started by hand at 7:49 pm Central on Oct 26, took that day's snapshot, but snapshots were then named by UTC date, already Oct 27, so both of Oct 27's runs found the file and exited. Since Oct 28 snapshots are named by Central date, as the status pass is, and that file is Oct 26's. The API shows only the current state, so Oct 27 can't be recovered. The report's "since the previous snapshot" section names the date it compares against.

**No status for Oct 27, 2026.** The first pass never ran: GitHub started none of the five morning runs, scheduled from 9:20 UTC, before the window closed at 8:44 Central, and reported no outage. This repo's scheduled jobs had been starting two to six hours late. Since Oct 27 the workflow starts the evening before and relays to fresh runs, which GitHub starts within seconds, until one can wait for 8:14. The first status in the data is Oct 28, the first morning the relay ran.
