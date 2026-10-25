# Tableau spec

Four dashboards in one Tableau Public workbook, built from the Google Sheet the pipeline writes. Each dashboard answers one question. Every title states a finding and takes its numbers from fields, so it stays true when the weekly refresh changes the data. The check values are the numbers each sheet showed on Oct 25, 2026, from docs/findings.md and the marts; tick each one off when the sheet is built.

## Connecting

1. In Tableau Public, Connect, To a Server, Google Sheets. Sign in with the Google account that owns the Sheet and pick **gph-marts**.
2. The Sheet has one tab per mart. Make one data source per tab used below, each holding that one table and named after it: mart_gies_enrollment, mart_peer_metrics, mart_funnel, mart_course_terms, mart_course_watch_list, mart_section_spread, mart_course_sections, mart_registration_watch, mart_refresh_log. No joins or relationships are needed; a parameter carries the course selection across data sources.
3. Tableau renames fields for display: underscores become spaces and each word is capitalized, so data_year shows as Data Year and is_illinois as Is Illinois. This spec uses those names. If your Tableau shows the raw names, the mapping is mechanical.
4. Check types once, in each data source's Data pane:
   - Every field starting Is (Is Illinois, Is Provisional, Is Undergraduate, Is On Watch List, Is Term At Threshold) and Published: Boolean. If one comes in as a string, change its type to Boolean.
   - Snapshot Date: Date.
   - Unitid, Data Year, Fall Year, Year, Course Level: whole numbers. Drag Unitid to Dimensions. Leave the year fields as measures; the sheets below say where to use them as continuous dimensions.
5. When you save to Tableau Public, tick "Keep my data in sync with Google Sheets". Tableau Public then refreshes from the Sheet once a day, after the pipeline's Monday refresh and daily snapshot.

## Look

| Item | Setting |
|---|---|
| Size | Desktop: fixed, 1200 × 1100. Phone: device layout, described per dashboard |
| Font | Tableau Book throughout (Format, Workbook). Titles Tableau Semibold 15, text 11, footer 9 |
| Text color | #333333; secondary text #6B6A66 |
| Illinois | #2A78D6 |
| Other Big Ten schools | #8C8C8C |
| Gridlines and zero lines | #E4E3DF, thin and solid; no column or row dividers |
| Shaded ranges (peer IQR, covid terms) | #F0EFEC |
| Program groups, bottom of stack to top | Online MBA #2A78D6, Other online graduate #EB6834, Residential graduate #1BAF7A, Undergraduate majors #EDA100, Business Undeclared #E87BA4, Undergraduate nondegree #008300 |
| Grade bands, A to D or F, and W | Grade A #104281, Grade B #256ABF, Grade C #5598E7, Grade D F #86B6EF, W #8C8C8C |
| Single-series bars and lines | #2A78D6 |
| Ramps for highlight tables | Tableau's Blue sequential palette |

These colors passed a colorblind check: adjacent program groups stay apart under protanopia, deuteranopia, and tritanopia, and the grade bands step evenly from dark to light. Three program-group colors fall below 3:1 contrast on white, so that chart carries a table under it. No gauges, donuts, 3D, or dual axes with two scales. No university logos or brand colors.

Every dashboard has, top to bottom: the title (the first sheet's title, dashboard title hidden), an info button at the top right, the sheets, and the footer sheet.

### Info button

On each dashboard: drag a Vertical container, float it at the top right (360 wide), put a Text object in it with the definitions given for that dashboard, then from the container's menu choose Add Show/Hide Button. Set the button to an image or the text "Definitions", and have the container start hidden.

### Footer sheet (used on every dashboard)

Data source mart_refresh_log.

- Calculated field **Last Refresh**: `{ MAX(IF [Published] THEN DATEPARSE("yyyy-MM-dd'T'HH:mm:ss'Z'", [Run Utc]) END) }`
- Marks: Text. Put Last Refresh on Text, formatted as a date, "mmm d, yyyy".
- Text, 9 point, #6B6A66: "Sources: IPEDS (National Center for Education Statistics); University of Illinois enrollment reports from the Division of Management Information and DAIR; the UIUC GPA and course catalog datasets (wadefagen/datasets); daily Course Explorer snapshots. Data refreshed <Last Refresh>. An independent project, not affiliated with or endorsed by the University of Illinois. github.com/omvyas77/program-health"
- No title, no tooltip.

### Course parameter (shared by Courses and Scheduling)

- **Course Choice**: String, List. Under "When workbook opens", fill from field mart_course_sections, Course. Current value ACCY 201. Show the parameter control as a single-value dropdown on both dashboards; it keeps the two in step.

### Peer set parameter (used on Peers)

- **Peer Set**: String, List with two values, "All 18 Big Ten schools" and "The 16 public schools". Current value "All 18 Big Ten schools". Northwestern and USC are private; the public view leaves them out of the peers, the medians, and the shaded range.

## Dashboard 1: Overview

Question: how are Gies programs doing?

Layout: a row of four number tiles across the top (four sheets, equal width), then Headcount by Program Group (full width), then Headcount Table (full width), then the footer. Dashboard title: the title of Headcount by Program Group.

### Calculated fields, data source mart_gies_enrollment

- **Latest Fall**: `{ MAX([Fall Year]) }`
- **Headcount Latest**: `SUM(IF [Fall Year] = [Latest Fall] THEN [Headcount] END)`
- **Headcount Five Falls Earlier**: `SUM(IF [Fall Year] = [Latest Fall] - 5 THEN [Headcount] END)`
- **Headcount Change Five Falls**: `[Headcount Latest] / [Headcount Five Falls Earlier] - 1`
- **Online Graduate Latest**: `SUM(IF [Fall Year] = [Latest Fall] AND [Level] = 'graduate' AND [Modality] = 'online' THEN [Headcount] END)`
- **Graduate Latest**: `SUM(IF [Fall Year] = [Latest Fall] AND [Level] = 'graduate' THEN [Headcount] END)`
- **Online Share Of Graduate**: `[Online Graduate Latest] / [Graduate Latest]`
- **Program Group**:

```
IF [Level] = 'undergraduate' THEN
    IF [Program Family] = 'Business Undeclared' THEN 'Business Undeclared'
    ELSEIF [Program Family] = 'Nondegree' THEN 'Undergraduate nondegree'
    ELSE 'Undergraduate majors'
    END
ELSEIF [Modality] = 'online' THEN
    IF [Program Family] = 'MBA' THEN 'Online MBA' ELSE 'Other online graduate' END
ELSE 'Residential graduate'
END
```

- **Is Online**: `[Modality] = 'online'`
- **First Chart Fall**: `[Latest Fall] - 9`
- **Headcount First Chart Fall**: `SUM(IF [Fall Year] = [First Chart Fall] THEN [Headcount] END)`
- **Online Added Since First Chart Fall**: `SUM(IF [Fall Year] = [Latest Fall] AND [Is Online] AND [Level] = 'graduate' THEN [Headcount] END) - SUM(IF [Fall Year] = [First Chart Fall] AND [Is Online] AND [Level] = 'graduate' THEN [Headcount] END)`

### Sheet: Tile Headcount

- Data source mart_gies_enrollment. Marks: Text.
- Text: Headcount Latest (number, thousands separator, no decimals), 28 point Semibold; a second line with Headcount Change Five Falls (percentage, one decimal, "+" for positive: custom format `+0.0%;-0.0%`) and the words "since Fall", then the field Latest Fall minus 5 (make a calc **Five Falls Earlier** = `[Latest Fall] - 5`, format number, no separator).
- Title: "Gies students, Fall <MAX(Latest Fall)>"
- Tooltip: off.
- Check: 10,095, +2.7% since Fall 2021.

### Sheet: Tile Online Share

- Data source mart_gies_enrollment. Marks: Text.
- Text: Online Share Of Graduate (percentage, one decimal), 28 point; second line "<Online Graduate Latest> of <Graduate Latest> graduate students".
- Title: "In online programs, Fall <MAX(Latest Fall)>"
- Check: 89.4%, 5,763 of 6,443.

### Sheet: Tile Retention

- Data source mart_peer_metrics. Marks: Text.
- Calculated fields (also used on Peers): **Latest Data Year For Metric** = `{ FIXED [Metric] : MAX([Data Year]) }`; **Is Latest Year** = `[Data Year] = [Latest Data Year For Metric]`.
- Filters: Metric equals ft_retention_rate; Is Illinois True; Is Latest Year True.
- Text: AVG([Value]) as a percentage, one decimal, 28 point; second line "against a peer median of <AVG(Peer Median Excl Il)>"; third line <ATTR(Data Year Label)>, 9 point.
- Title: "Illinois first-year retention"
- Check: 94.8% against 93.0%, Fall 2023 cohort returning in fall 2024.

### Sheet: Tile Business Share Rank

- Data source mart_peer_metrics. Marks: Text.
- Filters: Metric equals business_share_of_bachelors; Is Illinois True; Is Latest Year True.
- Calc **Rank Text**: `STR(MIN([Rank Of 18])) + IF MIN([Rank Of 18]) % 10 = 1 AND MIN([Rank Of 18]) <> 11 THEN 'st' ELSEIF MIN([Rank Of 18]) % 10 = 2 AND MIN([Rank Of 18]) <> 12 THEN 'nd' ELSEIF MIN([Rank Of 18]) % 10 = 3 AND MIN([Rank Of 18]) <> 13 THEN 'rd' ELSE 'th' END + ' of ' + STR(MIN([N Ranked]))`
- Text: Rank Text, 28 point; second line "<AVG(Value)> of bachelor's degrees, against a peer median of <AVG(Peer Median Excl Il)>" (both percentages, one decimal); third line <ATTR(Data Year Label)>, 9 point.
- Title: "Business share of Illinois bachelor's degrees, rank in the Big Ten"
- Check: 14th of 18; 9.5% against 16.7%; July 2024 to June 2025.

### Sheet: Headcount by Program Group

- Data source mart_gies_enrollment. Marks: Bar.
- Filter: Fall Year at least First Chart Fall (calc **In Chart Window** = `[Fall Year] >= [First Chart Fall]`, True).
- Columns: Fall Year as a discrete dimension. Rows: SUM(Headcount).
- Color: Program Group, with the colors and stack order under Look (Online MBA at the bottom). Size: about 70% of the band.
- Labels: segment labels off. Show each bar's total above it with a reference line: Analytics pane, Reference Line, Scope Per Cell, Value SUM(Headcount) with aggregation Total, Label Value, Line None.
- Tooltip: "Fall <Fall Year>: <SUM(Headcount)> students in <Program Group>"
- Title: "Gies enrollment grew from <Headcount First Chart Fall> in Fall <First Chart Fall> to <Headcount Latest> in Fall <Latest Fall>; online graduate programs account for <Online Added Since First Chart Fall> of the added students"
- Check, Fall 2017 to Fall 2026: Online MBA 787 to 3,847; Other online graduate 195 to 1,916; Residential graduate 1,068 to 680; Undergraduate majors 2,055 to 2,405; Business Undeclared 934 to 1,171; Undergraduate nondegree 116 to 76. Totals 5,155 and 10,095. Online added 4,781 of 4,940.

### Sheet: Headcount Table

- Same data source and filter. Marks: Text.
- Rows: Program Group (same order as the stack, top to bottom reversed so it reads like the chart). Columns: Fall Year (discrete). Text: SUM(Headcount), thousands separator.
- No title (the chart above carries it); the table is the readable form of the chart's colors.

### Info text

"Headcount counts students enrolled in Gies curricula at the tenth day of each fall, from DMI's reports through Fall 2025 and DAIR's Statistical Abstract for Fall 2026. Online programs are those whose academic program code ends in U; DMI lists none for Gies before Fall 2017. Program groups: Online MBA; other online graduate (MS Accountancy, MS Management, and MS Business Analytics online, the graduate certificate, online nondegree); residential graduate (residential master's, the residential MBA through 2020, and the PhD); undergraduate majors; Business Undeclared; undergraduate nondegree. Retention and the business share of bachelor's degrees are institution-level IPEDS figures for Illinois, not Gies figures. Business share counts first majors in CIP 52 codes. Peer medians leave Illinois out."

### Phone layout

Single column: Tile Headcount and Tile Online Share side by side, then Tile Retention and Tile Business Share Rank side by side, then Headcount by Program Group (height 360), the footer. Hide Headcount Table.

## Dashboard 2: Peers

Question: where does Illinois stand?

Layout: the Metric Choice and Peer Set controls in a row under the title; Dot Plot (left, 60% width) beside Illinois Over Time (right); Admit And Yield (full width) below; footer.

### Parameter

- **Metric Choice**: String, List. Values and display names:

| Value | Display as |
|---|---|
| ft_retention_rate | First-year retention rate |
| grad_rate_4yr | Four-year graduation rate |
| grad_rate_6yr | Six-year graduation rate |
| pell_gap_6yr | Pell gap in six-year graduation |
| admit_rate | Admit rate |
| yield_rate | Yield |
| applicants | Applicants |
| business_bachelors | Business bachelor's degrees |
| business_bachelors_incl_307102 | Business bachelor's degrees, with Business Analytics |
| business_share_of_bachelors | Business share of bachelor's degrees |
| business_share_of_bachelors_incl_307102 | Business share of bachelor's degrees, with Business Analytics |
| business_masters | Business master's degrees |
| business_masters_incl_307102 | Business master's degrees, with Business Analytics |
| business_major_share_of_ug | Business majors' share of undergraduates |
| pct_ug_exclusively_online | Undergraduates exclusively online |
| pct_grad_exclusively_online | Graduate students exclusively online |

Current value ft_retention_rate.

### Calculated fields, data source mart_peer_metrics

- **Is Selected Metric**: `[Metric] = [Metric Choice]`
- **Latest Data Year For Metric**: `{ FIXED [Metric] : MAX([Data Year]) }`
- **Is Latest Year**: `[Data Year] = [Latest Data Year For Metric]`
- **Is In Peer Set**: `[Peer Set] = 'All 18 Big Ten schools' OR [Control] = 'public'`
- **Metric Kind**: `IF [Metric] = 'pell_gap_6yr' THEN 'points' ELSEIF CONTAINS([Metric], 'rate') OR CONTAINS([Metric], 'share') OR STARTSWITH([Metric], 'pct_') THEN 'percent' ELSE 'count' END`
- **Scale**: `IF [Metric Kind] = 'count' THEN 1 ELSE 100 END`
- **Shown Value**: `[Value] * [Scale]`
- **Shown Peer Median**: `IIF([Peer Set] = 'All 18 Big Ten schools', [Peer Median Excl Il], [Public Peer Median Excl Il]) * [Scale]`
- **Shown Peer P25**: `IIF([Peer Set] = 'All 18 Big Ten schools', [Peer P25], [Public Peer P25]) * [Scale]`
- **Shown Peer P75**: `IIF([Peer Set] = 'All 18 Big Ten schools', [Peer P75], [Public Peer P75]) * [Scale]`
- **School Role**: `IIF([Is Illinois], 'Illinois', 'Other Big Ten schools')`
- **Label Percent**: `IF [Metric Kind] = 'percent' THEN [Shown Value] END`, number format custom `0.0"%"`
- **Label Points**: `IF [Metric Kind] = 'points' THEN [Shown Value] END`, custom `+0.0" pts";-0.0" pts"`
- **Label Count**: `IF [Metric Kind] = 'count' THEN [Shown Value] END`, number with thousands separator, no decimals
- **Rank In Set**: table calculation `RANK(SUM([Value]), 'desc')`, computed along School (rank 1 is the highest value, as in the mart)
- **Schools In Set**: table calculation `SIZE()`, computed along School
- **Metric Name**: a CASE over [Metric Choice] returning the display names above, for titles:

```
CASE [Metric Choice]
WHEN 'ft_retention_rate' THEN 'first-year retention'
WHEN 'grad_rate_4yr' THEN 'the four-year graduation rate'
WHEN 'grad_rate_6yr' THEN 'the six-year graduation rate'
WHEN 'pell_gap_6yr' THEN 'the Pell gap in six-year graduation'
WHEN 'admit_rate' THEN 'admit rate'
WHEN 'yield_rate' THEN 'yield'
WHEN 'applicants' THEN 'applicants'
WHEN 'business_bachelors' THEN 'business bachelor''s degrees'
WHEN 'business_bachelors_incl_307102' THEN 'business bachelor''s degrees with Business Analytics'
WHEN 'business_share_of_bachelors' THEN 'the business share of bachelor''s degrees'
WHEN 'business_share_of_bachelors_incl_307102' THEN 'the business share of bachelor''s degrees with Business Analytics'
WHEN 'business_masters' THEN 'business master''s degrees'
WHEN 'business_masters_incl_307102' THEN 'business master''s degrees with Business Analytics'
WHEN 'business_major_share_of_ug' THEN 'the business majors'' share of undergraduates'
WHEN 'pct_ug_exclusively_online' THEN 'the share of undergraduates exclusively online'
WHEN 'pct_grad_exclusively_online' THEN 'the share of graduate students exclusively online'
END
```

### Sheet: Dot Plot

- Data source mart_peer_metrics. Marks: Shape.
- Filters: Is Selected Metric True; Is Latest Year True; Is In Peer Set True. Add Is Selected Metric and Is In Peer Set to context, so the rank and the reference lines use only the schools shown.
- Rows: School, sorted by SUM(Shown Value) descending. Columns: SUM(Shown Value); axis title from Metric Choice's display name is not dynamic, so hide the axis title and let the title carry the unit.
- Shape: Is Provisional (False: filled circle; True: open circle). Size: 10 on the size slider's second notch. Color: School Role (Illinois #2A78D6, other schools #8C8C8C).
- Label: only the Illinois mark is labeled. Make **Illinois Label Percent** = `IF [Is Illinois] THEN [Label Percent] END`, **Illinois Label Points** and **Illinois Label Count** likewise, with the same number formats, and put all three on Label; for any metric only one is non-null.
- Reference band on the column axis, Per Table: from AVG(Shown Peer P25) to AVG(Shown Peer P75), fill #F0EFEC, no label. Reference line, Per Table: AVG(Shown Peer Median), solid #8C8C8C, label "Peer median".
- Tooltip: "<School>: <Label Percent><Label Points><Label Count> in <Data Year Label>. Rank <Rank In Set> of <Schools In Set>.<IF provisional: ' Provisional IPEDS data.'>" (use a calc **Provisional Note** = `IIF([Is Provisional], ' Provisional IPEDS data.', '')`).
- Title: "Illinois ranks <Rank In Set for Illinois> of <Schools In Set> on <Metric Name>, <Data Year Label>". For the Illinois rank in a title, make **Illinois Rank** = `WINDOW_MAX(IF ATTR([Is Illinois]) THEN [Rank In Set] END)` computed along School.
- Check (retention, all 18): Illinois 94.8%, 7th of 18, peer median 93.0%, shaded range 91.1% to 96.2%, Fall 2023 cohort returning in fall 2024, open circles (provisional). With the 16 publics: 5th of 16, peer median 92.7%, range 90.7% to 95.4%.

### Sheet: Illinois Over Time

- Data source mart_peer_metrics. Filters: Is Selected Metric True; Is Illinois True.
- Columns: Data Year as a continuous dimension (whole numbers, no separator). Rows: Measure Values with SUM(Shown Value) and SUM(Shown Peer Median), one axis. Color: Measure Names (Shown Value #2A78D6, renamed "Illinois"; Shown Peer Median #8C8C8C, renamed "Peer median").
- Marks: Line, 2 pt. To show provisional years as hollow points on the same scale, duplicate Measure Values on Rows, make it a dual axis, then Synchronize Axis and hide the right-hand axis: both axes are one scale. On the second pane set marks to Shape, Shape on Is Provisional (filled or open circle), Color on Measure Names.
- Tooltip: "<Measure Names>, <Data Year Label>: <Measure Values>".
- Title: "Illinois against the peer median on <Metric Name>, by data year"; subtitle "Open circles are provisional IPEDS data."
- Check (retention): Illinois 93.5% in 2014 and 94.8% in 2024; peer median 93.1% and 93.0%; 2024 is provisional.

### Sheet: Admit And Yield

- Data source mart_funnel.
- Calculated fields: **Latest IPEDS Fall** = `{ FIXED [Source] : MAX([Fall Year]) }`; **Is Latest IPEDS Fall** = `[Source] = 'ipeds' AND [Fall Year] = [Latest IPEDS Fall]`; **School Role** and **Is In Peer Set** as on mart_peer_metrics.
- Filters: Is Latest IPEDS Fall True; Residency equals all; Is In Peer Set True.
- Columns: AVG(Admit Rate), percent, one decimal. Rows: AVG(Yield Rate), percent, one decimal. Detail: School. Marks: Shape, Shape on Is Provisional, Color on School Role.
- Label: School, for Illinois only (calc **Illinois Name** = `IIF([Is Illinois], [School], NULL)`).
- Reference lines, Per Table: median of AVG(Admit Rate) and median of AVG(Yield Rate) over the peers. Tableau's reference line median includes Illinois, so use the calc **Peer Admit Rate** = `IIF([Is Illinois], NULL, [Admit Rate])` and **Peer Yield Rate** likewise, on Detail, and reference lines on their medians, solid #8C8C8C, labeled "Peer median".
- Tooltip: "<School>, <Fall Term> entering class: admitted <Admit Rate> of applicants; <Yield Rate> of admits enrolled."
- Title: "Illinois admitted <Illinois admit rate> of Fall <Latest IPEDS Fall> applicants, against a peer median of <median>; <Illinois yield> of admits enrolled" (make **Illinois Admit Rate** = `{ FIXED : AVG(IF [Is Illinois] AND [Is Latest IPEDS Fall] AND [Residency] = 'all' THEN [Admit Rate] END) }` and **Illinois Yield Rate** likewise).
- Check: Illinois 42.4% admitted, 28.8% yield; peer medians 58.1% and 22.4%; Fall 2024.

### Info text

"Peers are the 18 Big Ten universities in 2026. Peer medians and the shaded interquartile range leave Illinois out; with The 16 public schools selected they also leave out Northwestern and USC. Rank 1 is the highest value, so for admit rate it is the least selective school. Data years follow IPEDS: retention is labeled by the fall students returned, graduation rates by the entering cohort, completions by the July to June award year. Open circles are provisional IPEDS releases. Penn State is missing for its 2019 to 2021 collections, when it reported all campuses together. IPEDS figures describe the whole university, not Gies. With Business Analytics adds CIP 30.7102, which exists from 2019-20 awards on."

### Phone layout

Single column: the two controls, Dot Plot (height 520), Illinois Over Time (300), Admit And Yield (360), footer.

## Dashboard 3: Courses

Question: where should an assessment committee look?

Layout: the Course Choice control under the title; Grade Bands By Term (left half) beside Gies A-Range Trend (right half); Watch List (full width); Section Spread (full width); footer.

### Calculated fields, data source mart_course_terms

- **Course**: `[Subject] + ' ' + [Number]`
- **Is Chosen Course**: `[Course] = [Course Choice]`
- **Is Long Term**: `[Term] = 'Fall' OR [Term] = 'Spring'`
- **Term Order**: `[Year] * 10 + CASE [Term] WHEN 'Spring' THEN 1 WHEN 'Summer' THEN 2 WHEN 'Fall' THEN 3 ELSE 0 END`
- **Term Date**: `MAKEDATE([Year], IIF([Term] = 'Spring', 2, 9), 1)`
- **A Range Share**: `SUM([Grade A]) / SUM([Students Graded])`
- **Is Covid Term**: `[Term Flag] = 'covid_grading'`

### Sheet: Grade Bands By Term

- Data source mart_course_terms. Filters: Is Chosen Course True (add to context); Is Long Term True.
- Columns: Yearterm, sorted by MIN(Term Order) ascending. Rows: Measure Values with SUM(Grade A), SUM(Grade B), SUM(Grade C), SUM(Grade D F), SUM(W), in that order. Marks: Bar, stacked. Quick table calculation on Measure Values: Percent of Total, computed using Measure Names, so each bar adds to 100% of graded students plus W.
- Color: Measure Names with the grade band colors under Look; rename them "A range", "B range", "C range", "D or F", "W".
- Tooltip: "<Course>, <Yearterm>: <Measure Values> <Measure Names>". Add SUM(Students Graded) to Tooltip as "<SUM(Students Graded)> graded students".
- Title: "<Course Choice>: <A share in the latest long term> of grades were in the A range in <latest long term>" with **Latest Chosen Term** = `{ FIXED [Course] : MAX(IF [Is Long Term] THEN [Term Order] END) }` and **A Share Latest Chosen Term** = `SUM(IF [Term Order] = [Latest Chosen Term] THEN [Grade A] END) / SUM(IF [Term Order] = [Latest Chosen Term] THEN [Students Graded] END)`. Use ATTR of a calc **Latest Chosen Yearterm** = `IF [Term Order] = [Latest Chosen Term] THEN [Yearterm] END` (MAX) for the term name.
- Check (ACCY 201, 2025-fa): A range 282, B 129, C 53, D or F 24, W 4, of 488 graded; A range 57.8% of graded students. 2025-sp: 70.1%; 2010-fa: 62.4%.

### Sheet: Gies A-Range Trend

- Data source mart_course_terms. Filters: Is Undergraduate True; Is Long Term True.
- Columns: Term Date, continuous exact date, axis by year. Rows: A Range Share, percent, one decimal. Marks: Line, 2 pt, #2A78D6, with markers.
- Reference band on the date axis, Per Table, constant values from #2020-01-01# to #2021-03-01#, fill #F0EFEC, label "Covid grading terms (credit/no credit allowed)".
- Tooltip: "<Yearterm>: <A Range Share> of grades in Gies undergraduate courses were in the A range, from <SUM(Students Graded)> graded students." (Yearterm on Detail.)
- Title: "<Latest fall A share> of grades in Gies undergraduate courses were in the A range in Fall <latest fall>, up from <first fall A share> in Fall <first fall>" with **Latest Fall Year** = `{ FIXED : MAX(IF [Term] = 'Fall' THEN [Year] END) }`, **First Fall Year** = `{ FIXED : MIN(IF [Term] = 'Fall' THEN [Year] END) }`, and the two shares as `{ FIXED : SUM(IF [Term] = 'Fall' AND [Year] = [Latest Fall Year] AND [Is Undergraduate] THEN [Grade A] END) / SUM(IF [Term] = 'Fall' AND [Year] = [Latest Fall Year] AND [Is Undergraduate] THEN [Students Graded] END) }` and the same for First Fall Year.
- Subtitle: "Grades describe grading, not learning. Within-course change accounts for 17.5 of the 21.7-point rise from Fall 2015 to Fall 2025 (docs/findings.md, 6c.3)."
- Check: 54.4% in Fall 2010, 80.0% in Fall 2025; 2020-sp to 2021-sp inside the shaded band.

### Sheet: Watch List

- Data source mart_course_watch_list. Filter: Is On Watch List True.
- Calculated field **Term Order**: as on mart_course_terms.
- Rows: Course, Course Title. Columns: Yearterm, sorted by MIN(Term Order). Marks: Square. Color: AVG(C Or Below W Rate), Blue sequential, range from 0 to 0.3 fixed. Text: AVG(C Or Below W Rate), percent, one decimal. Border: none.
- A second text table to its right (same rows): AVG(Graded Per Term Offered) as "Graded per term", AVG(Course C Or Below W Rate) as "Four terms", AVG(Course Dfw Rate) as "DFW, four terms". Build it as a separate sheet, Watch List Totals, and place it beside Watch List.
- Tooltip: "<Course> <Course Title>, <Yearterm>: <C Or Below W Rate> of <SUM(Students Graded) + SUM(W)> students got C or below or withdrew; DFW <Dfw Rate>."
- Title: "<COUNTD(Course)> Gies undergraduate courses had 15% or more of students at C or below or withdrawing in at least two of the last four long terms"
- Subtitle: "Courses averaging 150 or more graded students per term offered. A course here is a question about preparation, placement, and support, not a verdict on its teaching."
- Check: 5 courses (ACCY 201, ACCY 202, ACCY 301, ACCY 303, FIN 300); FIN 300 23.3% over four terms, 25.8% in 2024-sp.

### Sheet: Section Spread

- Data source mart_section_spread.
- Calculated fields: **Year** = `INT(LEFT([Yearterm], 4))`; **Term Code** = `RIGHT([Yearterm], 2)`; **Long Term Index** = `[Year] * 2 + IIF([Term Code] = 'fa', 1, 0)`; **Is Last Four Long Terms** = `([Term Code] = 'fa' OR [Term Code] = 'sp') AND [Long Term Index] >= { FIXED : MAX(IF [Term Code] = 'fa' OR [Term Code] = 'sp' THEN [Long Term Index] END) } - 3`; **Course** = `[Subject] + ' ' + [Number]`; **Is Undergraduate** = `INT([Number]) < 500`; **GPA Range** = `[Gpa Max] - [Gpa Min]`.
- Filters: Is Last Four Long Terms True; Is Undergraduate True.
- Rows: Course, then Yearterm (sorted by MIN(Long Term Index)). Columns: AVG(Gpa Min), axis fixed from 2.0 to 4.0. Marks: Gantt Bar, Size AVG(GPA Range), color #2A78D6.
- Sort: Course alphabetically. Never sort by GPA; the sheet shows how much sections of one course differ, not which course or section grades easiest.
- Tooltip: "<Course>, <Yearterm>: <N Sections> sections, <Students Graded> graded students. Section GPAs from <Gpa Min> to <Gpa Max>; standard deviation <Gpa Sd>." (two decimals)
- Title: "In the last four long terms, section GPAs within one Gies undergraduate course differed by up to <WINDOW_MAX(MAX(GPA Range))> points"
- Subtitle: "Courses with three or more sections in the GPA data. No section or instructor is identified."
- Check: 91 course-terms; widest 1.04 (FIN 300, 2024-sp, 2.30 to 3.34).

### Info text

"From the UIUC GPA dataset: sections with 21 or more graded students, Spring 2010 to Winter 2026. Graded students leave out W. A range is A+, A, and A-. C or below or W counts C+ through F plus W over graded students plus W; DFW counts D+ through F plus W. Covid grading terms (Spring 2020 to Spring 2021) allowed credit/no credit and nearly eliminated W. Grades describe grading, not learning, and a course on the watch list is a question for its department, not a verdict on its teaching. Undergraduate courses are numbered below 500."

### Phone layout

Single column: Course Choice, Grade Bands By Term (360), Gies A-Range Trend (300), Watch List (fit width; hide Watch List Totals), Section Spread (fit width), footer.

## Dashboard 4: Scheduling

Question: where is capacity tight?

Layout: Course Choice control under the title; Sections By Term above Students By Term (both full width, aligned on the same term axis); Students Per Section (left half) beside Registration Curve (right half); footer.

### Calculated fields, data source mart_course_sections

- **Is Chosen Course**: `[Course] = [Course Choice]`
- **Is Long Term**, **Term Order**: as on mart_course_terms.
- **Term Date**: `MAKEDATE([Year], IIF([Term] = 'Spring', 2, 9), 1)`

### Sheet: Sections By Term

- Filters: Is Chosen Course True; Is Long Term True; Year at least 2016 (the catalog starts in Fall 2016).
- Columns: Term Date, continuous, axis from #2016-08-01# to the latest term (leave automatic end). Rows: SUM(Primary Sections). Marks: Bar, #2A78D6.
- Tooltip: "<Course>, <Yearterm>: <Primary Sections> primary sections (lectures, lecture-discussions, online lectures, seminars)."
- Calculated fields: **Latest Graded Fall** = `{ MAX(IF [Term] = 'Fall' AND NOT ISNULL([Students Graded]) THEN [Year] END) }`, the latest fall the GPA data covers, so the sections and students titles compare the same terms; **Sections Latest Fall** = `SUM(IF [Term] = 'Fall' AND [Year] = [Latest Graded Fall] THEN [Primary Sections] END)`; **Sections Fall 2019** = `SUM(IF [Yearterm] = '2019-fa' THEN [Primary Sections] END)`. Put Is Chosen Course in context so these sum one course.
- Title: "<Course Choice>: <Sections Latest Fall> primary sections in Fall <Latest Graded Fall>, against <Sections Fall 2019> in Fall 2019"
- Check (ACCY 201): 3 in Fall 2019, 3 in Fall 2025; 3 listed for Spring and Fall 2026.

### Sheet: Students By Term

- Same filters and the same Columns, with the axis range copied from Sections By Term so the bars line up.
- Rows: SUM(Students Graded). Marks: Bar, #2A78D6.
- Tooltip: "<Course>, <Yearterm>: <Students Graded> graded students in sections of 21 or more."
- Calculated fields: **Students Latest Fall** = `SUM(IF [Term] = 'Fall' AND [Year] = [Latest Graded Fall] THEN [Students Graded] END)`; **Students Fall 2019** = `SUM(IF [Yearterm] = '2019-fa' THEN [Students Graded] END)`.
- Title: "Graded students: <Students Fall 2019> in Fall 2019, <Students Latest Fall> in Fall <Latest Graded Fall>"
- Check (ACCY 201): 604 in Fall 2019, 488 in Fall 2025.

### Sheet: Students Per Section

- Calculated field **Students Per Primary Section**: `SUM([Students Graded]) / SUM(IF NOT ISNULL([Students Graded]) THEN [Primary Sections] END)`. Graded students come from the GPA data, which leaves out sections of 20 or fewer, so the figure runs a little low; the sections are the catalog's lectures and seminars. The GPA data's own section count isn't used, because where grades were recorded moved from discussions to lectures over these years (docs/data_notes.md). Chosen Oct 25, 2026.
- Filters: Is Chosen Course True; Is Long Term True; Year at least 2016.
- Columns: Term Date, continuous. Rows: Students Per Primary Section, one decimal. Marks: Line, 2 pt, #2A78D6, markers on.
- Tooltip: "<Course>, <Yearterm>: <Students Per Primary Section> graded students per primary section."
- Title: "<Course Choice>: <latest value> graded students per primary section in Fall <Latest Graded Fall>, against <Fall 2019 value> in Fall 2019", with **Per Section Latest Fall** = `[Students Latest Fall] / [Sections Latest Fall]` and **Per Section Fall 2019** = `[Students Fall 2019] / [Sections Fall 2019]`.
- Check: ACCY 201 201.3 in Fall 2019 and 162.7 in Fall 2025. Gies-wide, across courses with both counts: 55.9 and 69.8 (docs/findings.md, 6d.2).

### Sheet: Registration Curve

- Data source mart_registration_watch.
- Calculated fields: **Course** = `[Subject] + ' ' + [Number]`; **Is Chosen Course** = `[Course] = [Course Choice]`; **Latest Snapshot** = `{ MAX([Snapshot Date]) }`; **Latest Days** = `{ MAX([Days Since Registration Open]) }`; **Registration Status** = `IF [Latest Days] < 0 THEN 'opens in ' + STR(-[Latest Days]) + ' days' ELSEIF [Latest Days] = 0 THEN 'opens today' ELSE 'opened ' + STR([Latest Days]) + ' days ago' END`; **Sections At Latest Snapshot** = `SUM(IF [Snapshot Date] = [Latest Snapshot] THEN [Primary Sections] END)`.
- Two panes in one sheet would need two scales, so build it as two small sheets stacked:
  - **Registration Gies Total**: Columns Days Since Registration Open (continuous); Rows SUM(Primary Sections); Line, 2 pt, #2A78D6, markers on. Reference line at constant 0 on the column axis, solid #8C8C8C, label "Registration opens Nov 2". Title: "Gies lists <Sections At Latest Snapshot> primary sections for Spring 2027 as of <Latest Snapshot>; registration <ATTR(Registration Status)>".
  - **Registration Chosen Course**: same, filtered to Is Chosen Course True (in context). Title: "<Course Choice>: <Sections At Latest Snapshot> primary sections for Spring 2027". A course with no Spring 2027 sections leaves this sheet blank; its caption says so: "Blank when the course has no Spring 2027 primary sections."
- Tooltip: "<Snapshot Date>, <Days Since Registration Open> days from opening: <Primary Sections> primary sections; <Sections Added Since Previous> added and <Sections Removed Since Previous> removed since the previous snapshot."
- Caption under both: "The Course Explorer API doesn't report whether a section is open or closed, so this tracks the section list. A section added after registration opens can mean demand ran ahead of the schedule; it can also be a room or staffing change."
- Check (Oct 25, 2026): 509 primary sections, registration opens in 8 days; ACCY 201 3 sections. These change daily.

### Info text

"Primary sections are lectures, lecture-discussions, online lectures, online lecture-discussions, and seminars in the course catalog, counted once per CRN; discussions and labs are left out. The catalog covers Fall 2016 on. Graded students come from the GPA dataset, which leaves out sections of 20 or fewer graded students and leaves out W. The registration watch reads the Course Explorer API once a day; it has no seat counts or open/closed status. Registration for Spring 2027 opens Nov 2, 2026, and the last day to add is Feb 1, 2027."

### Phone layout

Single column: Course Choice, Sections By Term (220), Students By Term (220), Students Per Section (240), Registration Gies Total (220), Registration Chosen Course (220), footer.

## After building

1. Check every value listed under Check against the dashboards, and against docs/findings.md where it says so.
2. Switch Metric Choice through all 16 metrics and Peer Set both ways; every title should read as a sentence and every dot plot should have 16 to 18 schools (17 for Penn State's missing years).
3. Pick three courses in Course Choice, one on the watch list, one graduate course, and one with no Spring 2027 sections, and confirm nothing breaks.
4. Save to Tableau Public with "Keep my data in sync with Google Sheets" ticked, open the published workbook in a private window, and check the phone layout from a phone.
