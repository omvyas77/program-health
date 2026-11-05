# Addendum: the UW–Madison School of Education in public data

The same pipeline pointed at a second school. It adds no new sources: the IPEDS completions files
already in data/extracts cover every field for all 18 Big Ten schools, Wisconsin among them. It is
not affiliated with or endorsed by UW–Madison.

- The one-page note: [brief/soe_note.pdf](../brief/soe_note.pdf), built by `make soe-note`
- The tables behind it, each with its SQL: F1 to F4 in [docs/findings.md](findings.md)
- The marts: `mart_education_completions` (18 schools, CIP 13 by four-digit series, plus each
  school's all-fields total) and `mart_soe_portfolio` (UW–Madison, the fields the School houses)

## What it found

- **Education degrees grew at UW–Madison while they fell across the Big Ten.** Three-year averages,
  2014-15 to 2016-17 against 2022-23 to 2024-25: bachelor's rose 47% (122 to 180 a year) and
  master's 52% (114 to 174). The other 16 schools combined fell 5% and 20%. UW–Madison's master's
  growth is the largest of the 18. Doctoral degrees held level (58 to 56).
- **New programs drove the bachelor's growth.** 85 of the 173-degree rise in three-year totals is in
  CIP 13.09, which first passes 10 bachelor's degrees in 2018-19 and matches the Educational Policy
  Studies BS. Curriculum and instruction drove the master's growth (120 to 262 in three-year
  totals), with special education (19 to 79). Master's degrees peaked at 222 in 2021-22 and were 164
  in 2024-25.
- **Education is about half of the degrees in the School's fields**: 43% of mapped degrees in
  2024-25, or 52% counting only high-confidence codes.

## Method

- **Degrees, first majors.** Bachelor's (AWLEVEL 5), master's (7), and doctoral (17, 18, 19);
  certificates are left out. MAJORNUM 1 only, so each degree counts once, as in the business marts.
- **Three-year windows.** Single years swing (Wisconsin's master's went from 87 to 147 between
  2015-16 and 2016-17), so the headline compares three-year averages and the chart shows every year.
- **The combined peer line leaves out Penn State**, whose 2019-20 and 2020-21 files are excluded
  (data_notes.md), so it is the same 16 schools every year. The per-school table in F1 keeps all 18.
- **Series are four-digit CIP codes** with labels from the 2020 CIP (config/cip_education_series.csv).
  Rolling up to four digits keeps recodes inside a series together: 13.1099 first appears in
  2024-25 as 13.1001 falls, and both stay in Special Education.

## The School of Education map

IPEDS reports by field, not by school or college, so `config/cip_soe_map.csv` maps the codes the
School's ten departments appear to confer, from the departments and majors in the Guide. Each code
has a confidence:

- **high**: the code matches a School department's programs and no other school or college appears
  to confer it (all of CIP 13, kinesiology, athletic training, occupational therapy, dance, art,
  counseling and educational psychology, rehabilitation psychology). Music teacher education
  (13.1312) sits in CIP 13 and is worth checking, since music is taught outside the School.
- **medium**: likely but unconfirmed. 31.0599 starts in 2020-21 and matches the Health Promotion and
  Health Equity BS; 42.2805 (school psychology) is placed in Educational Psychology; 50.0501
  (theatre) follows the Theatre and Drama department, which the Guide lists in the School today.

Left out on purpose, because other schools and colleges confer them: psychology (42.0101), art
history (50.0703), music (50.09), interior design (50.0408), arts administration (50.1002), public
health (51.22), and physical therapy (51.2308). Left out because I couldn't place them: 31.0504 and
42.2799. `assert_soe_portfolio_matches_education` checks that the map's Education group equals the
peer mart's UW–Madison education rows in every year.

## Limitations

- **Not School totals.** The map is a first pass. The first thing to do with internal access is to
  reconcile it against RADAR's Trends in Degrees, department by department.
- **IPEDS can't show attribution changes.** If a department's degrees moved between schools, the
  map counts them in every year anyway.
- **2024-25 is a provisional release**, and the 2024-25 numbers can move when it becomes final.
- **Degrees only.** Enrollment by program, retention, time to degree, licensure, post-graduation
  outcomes, scholarships, and course seat fill are not in the public files; the note lists them as
  the questions to answer next.
