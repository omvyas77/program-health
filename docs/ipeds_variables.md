# IPEDS variables

Every IPEDS variable this project reads, with the dictionary's own words. Titles come from each file's Varlist sheet, code labels from its Frequencies sheet, and descriptions from its Description sheet. Text is copied from the dictionaries downloaded on Oct 23, 2026, with Excel's line-break code (\_x000D\_) and repeated spaces removed and nothing else changed. When a title, label, or description changes across years in more than its year numbers, each version is listed with the files that use it. File URLs are in config/ipeds_files.csv, taken from the IPEDS Data Center's Complete Data Files pages.

## Data years

The rule here is to take each file's data year from its dictionary title. In 67 of the 72 files the title agrees with the year given everywhere else in the dictionary. In five files one piece of text contradicts the rest and the pattern every other year follows. I label each by what the majority of its own dictionary text says:

| File | What disagrees | What the rest of the dictionary text says | Label used |
| --- | --- | --- | --- |
| GR2020 | COHORT code 2 reads "Bachelor's or equiv 2017 subcohort" | The GR2020 title, and the GR2020_PELL_SSL title, code, and description, all say 2014 | Cohort that entered in 2014 |
| GR2024 | Title reads "cohort year 2017 (4-year)" | COHORT code 2, and the GR2024_PELL_SSL code 2 label and description, say 2018 | Cohort that entered in 2018 |
| GR2024_PELL_SSL | Title reads "cohort year 2017 (4-year)" | PSGRTYPE code 2 and the PSGRTYPE description say 2018, as does GR2024's COHORT code 2 | Cohort that entered in 2018 |
| GR2021_PELL_SSL | PSGRTYPE description reads "entered in 2014" | Title and PSGRTYPE code 2 say 2015 | Cohort that entered in 2015 |
| C2022_A | CTOTALT description reads "between July 1, 2022 and June 30, 2023" | Title says 2021-22 | Awards from July 1, 2021 to June 30, 2022 |

The two graduation-rate files get a second check once the data is downloaded. A GR file's bachelor's cohort should be close to the full-time fall cohort that EF D reports for the same fall: EF2015D's fall 2014 cohort for GR2020, and EF2019D's fall 2018 cohort for GR2024.

| Family | Files | Title of the latest dictionary | What each file describes |
| --- | --- | --- | --- |
| Directory | HD2024 to HD2025 | File Documentation for the IPEDS Directory, 2025-26 | The institution in the file's collection year. HD2025 is 2025-26. |
| Admissions | ADM2014 to ADM2024 | File Documentation for the Admissions Data File, 2024-25 | First-time, degree-seeking undergraduates who applied, were admitted, and enrolled for the fall of the file's year. The dictionary says "the most recent fall period available" for a collection that runs from that fall to the next spring. ADM2024 is the fall 2024 entering class. |
| Retention | EF2014D to EF2024D | File documentation for total entering class, retention rates, and student-to-faculty ratio: Fall 2024 | Retention of the previous fall's full-time cohort into the file's fall. EF2024D is the fall 2023 cohort enrolled in fall 2024. |
| Graduation rates | GR2014 to GR2024 | File documentation for graduation rate data, 150% of normal time to complete - cohort year 2017 (4-year) and cohort year 2020 (2-year) institutions: 2024 | The full-time, first-time cohort that entered six years before the file's year, with completions within 4 and 6 years. GR2024 is the cohort that entered in 2018. |
| Completions | C2015_A to C2025_A | File Documentation for the Completions Data File, 2024-25 | Awards conferred from July 1 of the year before the file's year to June 30 of the file's year. C2025_A is July 1, 2024 to June 30, 2025. |
| Business majors | EF2014CP to EF2024CP | File documentation for enrollment in selected major fields of study, by race/ethnicity, gender, attendance status, and level of student: Fall 2024 | Fall enrollment by major field in the file's year. Reported in even years only. |
| Distance education | EF2014A_DIST to EF2024A_DIST | File documentation for enrollment by distance education status and level of student: Fall 2024 | Fall enrollment by distance education status in the file's year. |
| Pell gap | GR2016_PELL_SSL to GR2024_PELL_SSL | File documentation for graduation rate data for Federal Pell Grant recipients and Direct Subsidized Loan recipients, 150% of normal time to complete - cohort year 2017 (4-year) and cohort year 2021 (2-year and less-than-2-year) institutions: 2024 | The same cohort as the GR file of the same year, split by Pell Grant and subsidized loan receipt. GR2024_PELL_SSL is the cohort that entered in 2018. |

## Directory (HD2024, HD2025)

| Variable | Title in the dictionary | How it's used |
| --- | --- | --- |
| UNITID | Unique identification number of the institution | Key for every join, and the filter to the 18 schools in config/peers.csv. |
| INSTNM | Institution (entity) name | Confirms each UNITID is the school intended. |
| CITY | City location of institution | Confirms each UNITID is the main campus, not a branch. |
| STABBR | State abbreviation | Checked against the state in config/peers.csv. |
| CONTROL | Control of institution | Checked against the control column in config/peers.csv. |

| Variable | Code | Label in the dictionary | How it's used |
| --- | --- | --- | --- |
| CONTROL | 1 | Public | Expected for the 16 publics. |
| CONTROL | 2 | Private not-for-profit | Expected for Northwestern and USC. |

Descriptions:

**UNITID**

> HD2025: (The dictionary gives no description.)

**INSTNM**

> HD2025: Institution (entity) name

**CITY**

> HD2025: City location of institution

**STABBR**

> HD2025: US Postal Service state abbreviation. See also FIPS STATE CODE (FIPS).

**CONTROL**

> HD2025: A classification of whether an institution is operated by publicly elected or appointed officials or by privately elected or appointed officials and derives its major source of funds from private sources. Public institution - An educational institution whose programs and activities are operated by publicly elected or appointed school officials and which is supported primarily by public funds. Private not-for-profit institution - A private institution in which the individual(s) or agency in control receives no compensation, other than wages, rent, or other expenses for the assumption of risk. These include both independent not-for-profit schools and those affiliated with a religious organization. Private for-profit institution - A private institution in which the individual(s) or agency in control receives compensation other than wages, rent, or other expenses for the assumption of risk.


## Admissions (ADM2014 to ADM2024)

| Variable | Title in the dictionary | How it's used |
| --- | --- | --- |
| APPLCN | Applicants total | The applicants metric, and the denominator of admit_rate. |
| ADMSSN | Admissions total | Numerator of admit_rate, denominator of yield_rate. |
| ENRLT | Enrolled total | Numerator of yield_rate. |

admit_rate = ADMSSN / APPLCN. yield_rate = ENRLT / ADMSSN. Both cover first-time, degree-seeking undergraduates only.

Descriptions:

**APPLCN**

> ADM2024: Please provide the number of first-time, degree/certificate-seeking undergraduate students who applied, were admitted, and enrolled (full or part time) at your institution for the most recent fall period available. Include early decision, early action, and students who began studies during the summer prior to that fall. This is applicable to institutions that have no open admission policy for entering first-time undergraduate students Total number of applicants APPLICANT - An individual who has fulfilled the institution’s requirements to be considered for admission (including payment or waiving of the application fee, if any) and who has been notified of one of the following actions: admission, nonadmission, placement on waiting list, or application withdrawn (by applicant or institution). FIRST-TIME STUDENT (UNDERGRADUATE) - A student attending any institution for the first time at the undergraduate level. Includes students enrolled in academic or occupational programs. Also includes students enrolled in the fall term who attended college for the first time in the prior summer term, and students who entered with advanced standing (college credits earned before graduation from high school). DEGREE/CERTIFICATE-SEEKING STUDENTS Students enrolled in courses for credit who are recognized by the institution as seeking a degree or formal award. At the undergraduate level, this is intended to include students enrolled in vocational or occupational programs. EARLY DECISION A plan that allows students to apply and be notified of an admission decision (and financial aid offer, if applicable) well in advance of the regular notification date. Applicants agree to accept an offer of admission and, if admitted, to withdraw their applications from other colleges. There are three possible decision applications: admitted, denied, or not admitted but forwarded for consideration with the regular applicant pool, without prejudice. EARLY ACTION An admission plan that allows students to apply and be notified of an admission decision well in advance of the regular notification dates. If admitted, the candidate is not committed to enroll (unlike early decision). Students may reply to the offer under the college's regular reply policy.

**ADMSSN**

> ADM2024: Please provide the number of first-time, degree/certificate-seeking undergraduate students who applied, were admitted, and enrolled (full or part time) at your institution for the most recent fall period available. Include early decision, early action, and students who began studies during the summer prior to that fall. This is applicable to institutions that have no open admission policy for entering first-time undergraduate students Total number of admissions ADMISSIONS - Applicants that have been granted an official offer to enroll in a college or university. FIRST-TIME STUDENT (UNDERGRADUATE) - A student attending any institution for the first time at the undergraduate level. Includes students enrolled in academic or occupational programs. Also includes students enrolled in the fall term who attended college for the first time in the prior summer term, and students who entered with advanced standing (college credits earned before graduation from high school). DEGREE/CERTIFICATE-SEEKING STUDENTS Students enrolled in courses for credit who are recognized by the institution as seeking a degree or formal award. At the undergraduate level, this is intended to include students enrolled in vocational or occupational programs. EARLY DECISION A plan that allows students to apply and be notified of an admission decision (and financial aid offer, if applicable) well in advance of the regular notification date. Applicants agree to accept an offer of admission and, if admitted, to withdraw their applications from other colleges. There are three possible decision applications: admitted, denied, or not admitted but forwarded for consideration with the regular applicant pool, without prejudice. EARLY ACTION An admission plan that allows students to apply and be notified of an admission decision well in advance of the regular notification dates. If admitted, the candidate is not committed to enroll (unlike early decision). Students may reply to the offer under the college's regular reply policy.

**ENRLT**

> ADM2024: Please provide the number of first-time, degree/certificate-seeking undergraduate students who applied, were admitted, and enrolled (full or part time) at your institution for the most recent fall period available. Include early decision, early action, and students who began studies during the summer prior to that fall. This is applicable to institutions that have no open admission policy for entering first-time undergraduate students Total number of enrolled FIRST-TIME STUDENT (UNDERGRADUATE) - A student attending any institution for the first time at the undergraduate level. Includes students enrolled in academic or occupational programs. Also includes students enrolled in the fall term who attended college for the first time in the prior summer term, and students who entered with advanced standing (college credits earned before graduation from high school). DEGREE/CERTIFICATE-SEEKING STUDENTS Students enrolled in courses for credit who are recognized by the institution as seeking a degree or formal award. At the undergraduate level, this is intended to include students enrolled in vocational or occupational programs. EARLY DECISION A plan that allows students to apply and be notified of an admission decision (and financial aid offer, if applicable) well in advance of the regular notification date. Applicants agree to accept an offer of admission and, if admitted, to withdraw their applications from other colleges. There are three possible decision applications: admitted, denied, or not admitted but forwarded for consideration with the regular applicant pool, without prejudice. EARLY ACTION An admission plan that allows students to apply and be notified of an admission decision well in advance of the regular notification dates. If admitted, the candidate is not committed to enroll (unlike early decision). Students may reply to the offer under the college's regular reply policy.


## Retention (EF2014D to EF2024D)

| Variable | Title in the dictionary | How it's used |
| --- | --- | --- |
| RRFTCTA | Full-time adjusted fall 2023 cohort | Denominator of ft_retention_rate. |
| RET_NMF | Students from the full-time adjusted fall 2023 cohort enrolled in fall 2024 | Numerator of ft_retention_rate. |
| RET_PCF | Full-time retention rate, 2024 | Not used in any metric. Read only to check that RET_NMF / RRFTCTA reproduces NCES's own rate. |

ft_retention_rate = RET_NMF / RRFTCTA, computed from counts: a group's rate is the sum of numerators over the sum of denominators.

The adjusted cohort changed definition: from EF2016D on, the description adds inclusions and says they "were added to the retention rate calculation beginning Fall 2017". Rates before and after that change are not strictly comparable, and charts that span it should say so.

Descriptions:

**RRFTCTA**

> EF2014D to EF2015D, as worded in EF2015D: Full-time adjusted cohort from prior year: Full-time cohort from prior year minus number of exclusions

> EF2016D to EF2024D, as worded in EF2024D: Full-time adjusted cohort from prior year: Full-time cohort from prior year minus number of exclusions plus the number of Inclusions. Inclusions were added to the retention rate calculation beginning Fall 2017.

**RET_NMF**

> EF2024D: Number of students from the full-time cohort in the prior year who are still enrolled in the current year (include students that re-enrolled and students with continuous enrollment).

**RET_PCF**

> EF2024D: The full-time retention rate is the percent of the (fall full-time cohort from the prior year minus exclusions from the fall full-time cohort) that re-enrolled at the institution as either full- or part-time in the current year


## Graduation rates (GR2014 to GR2024)

GR is used instead of DRVGR: the Data Center lists DRVGR only from 2021, and GR carries the cohort and completer counts that rule 6 asks for.

| Variable | Title in the dictionary | How it's used |
| --- | --- | --- |
| GRTYPE | Cohort data | Selects the rows below. |
| COHORT | Cohort | Confirms the cohort year (see Data years). |
| GRTOTLT | Grand total | The count on each selected row. |

| Variable | Code | Label in the dictionary | How it's used |
| --- | --- | --- | --- |
| GRTYPE | 8 | GR2014 to GR2022: Bachelor's or equiv subcohort (4-yr institution) adjusted cohort (revised cohort minus exclusions)<br>GR2023 to GR2024: Adjusted cohort (revised cohort minus exclusions) | Denominator of both rates. GR2014 to GR2022 name the bachelor's subcohort in the label. GR2023 and GR2024 drop it but still list code 8 inside the bachelor's subcohort block (codes 6 to 16). |
| GRTYPE | 13 | GR2014 to GR2022: Bachelor's or equiv subcohort (4-yr institution) Completers of bachelor's or equiv degrees in 4 years or less<br>GR2023 to GR2024: Completers of bachelor's or equivalent degrees in 4 years or less | Numerator of grad_rate_4yr. |
| GRTYPE | 12 | GR2014 to GR2022: Bachelor's or equiv subcohort (4-yr institution) Completers of bachelor's or equiv degrees total (150% of normal time)<br>GR2023 to GR2024: Completers of bachelor's or equivalent degrees total (150% of normal time) | Numerator of grad_rate_6yr. |
| COHORT | 2 | Bachelor's or equiv 2018 subcohort (4-yr institution) | Expected on the rows selected above. |

grad_rate_4yr = GRTOTLT where GRTYPE = 13, divided by GRTOTLT where GRTYPE = 8. grad_rate_6yr uses GRTYPE = 12 as the numerator. For a bachelor's degree, 150% of normal time is six years. Once the data is in, I'll check that code 12 equals codes 13, 14, and 15 added together for every school and year.

Descriptions:

**GRTYPE**

> GR2014, GR2016 to GR2024, as worded in GR2024: Cohort status defines the graduation status students of the cohort. NORMAL TIME TO COMPLETION - The amount of time necessary for a student to complete all requirements for a degree or certificate according to the institution's catalog. This is typically 4 years (8 semesters or trimesters, or 12 quarters, excluding summer terms) for a bachelor's degree in a standard term-based institution; 2 years (4 semesters or trimesters, or 6 quarters, excluding summer terms) for an associate's degree in a standard term-based institution; and the various scheduled times for certificate programs. COMPLETERS WITHIN 150% (OF NORMAL TIME) - Students (within a cohort or subcohort) who completed their program within 150% of the normal time to completion. See Normal Time. BACHELOR'S DEGREE - An award (baccalaureate or equivalent degree, as determined by the Secretary, U.S. Department of Education) that normally requires at least 4 but NOT more than 5 years of full-time equivalent college-level work. This includes ALL bachelor's degrees conferred in a 5-year COOPERATIVE (WORK-STUDY PLAN) PROGRAM. A cooperative plan provides for alternate class attendance and employment in business, industry, or government; thus, it allows students to combine actual work experience with their college studies. Also, includes bachelor's degrees in which the normal 4 years of work are completed in 3 years TOTAL TRANSFER-OUT STUDENTS (NON-COMPLETERS) - Total number of students from the cohort or subcohort who transferred out at any time within 150% of normal time to completion. A transfer-out student is a student who has not completed or graduated from the program in which he or she was enrolled, but who has subsequently enrolled at another eligible institution in any program for which the reporting institution provided substantial preparation. EXCLUSIONS - Students from the cohort or subcohort who left the institution for any of the following reasons: died or were totally and permanently disabled; to serve in the armed forces; to serve with a foreign aid service of the Federal Government, such as the Peace Corps; or to serve on official church missions.

> GR2015, as worded in GR2015: Cohort status defines the graduation status students of the cohort. NORMAL TIME TO COMPLETION - The amount of time necessary for a student to complete all requirements for a degree or certificate according to the institution's catalog. This is typically 4 years (8 semesters or trimesters, or 12 quarters, excluding summer terms) for a bachelor's degree in a standard term-based institution; 2 years (4 semesters or trimesters, or 6 quarters, excluding summer terms) for an associate's degree in a standard term-based institution; and the various scheduled times for certificate programs. COMPLETERS WITHIN 150% (OF NORMAL TIME) - Students (within a cohort or subcohort) who completed their program within 150% of the normal time to completion. See Normal Time. BACHELOR'S DEGREE - An award (baccalaureate or equivalent degree, as determined by the Secretary, U.S. Department of Education) that normally requires at least 4 but NOT more than 5 years of full-time equivalent college-level work. This includes ALL bachelor's degrees conferred in a 5-year COOPERATIVE (WORK-STUDY PLAN) PROGRAM. A cooperative plan provides for alternate class attendance and employment in business, industry, or government; thus, it allows students to combine actual work experience with their college studies. Also, includes bachelor's degrees in which the normal 4 years of work are completed in 3 years TOTAL TRANSFER-OUT STUDENTS (NON-COMPLETERS) - Total number of students from the cohort or subcohort who transferred out at any time within 150% of normal time to completion. A transfer-out student is a student who has not completed or graduated from the program in which he or she was enrolled, but who has subsequently enrolled at another eligible institution in any program for which the reporting institution provided substantial preparation. EXCLUSIONS - Students from the cohort or subcohort who left the institution for any of the following reasons: died or were totally and permanently disabled; to serve in the armed forces; to serve with a foreign aid service of the Federal Government, such as the Peace Corps; or to serve on official church missions. Long programs - Non-completers still enrolled in long programs as of August 31, 2011.

**COHORT**

> GR2024: Cohort

**GRTOTLT**

> GR2024: Grand total (men and women) in cohort


## Completions (C2015_A to C2025_A)

| Variable | Title in the dictionary | How it's used |
| --- | --- | --- |
| CIPCODE | CIP Code - 2020 Classification | Read as text in its NN.NNNN form. The business flag comes from config/cip_business.csv in Phase 5. |
| MAJORNUM | First or Second Major | Only first majors are counted. |
| AWLEVEL | Award Level code | Selects bachelor's and master's degrees. |
| CTOTALT | Grand total | The count. |

| Variable | Code | Label in the dictionary | How it's used |
| --- | --- | --- | --- |
| AWLEVEL | 5 | Bachelor's degree | business_bachelors, business_share_of_bachelors. |
| AWLEVEL | 7 | Master's degree | business_masters. |
| MAJORNUM | 1 | First major | All completions metrics. |

business_bachelors = CTOTALT summed over business CIP codes, AWLEVEL 5, MAJORNUM 1. business_masters is the same with AWLEVEL 7. business_share_of_bachelors = business_bachelors divided by first-major bachelor's degrees in all fields. Counting first majors only counts each degree once; a student's second major is reported again under MAJORNUM 2.

CIPCODE switches from the 2010 to the 2020 CIP classification in C2020_A. Code 30.7102, Business Analytics, exists only in the 2020 classification, so the with-and-without-30.7102 comparison starts with 2019-20 awards.

Descriptions:

**CIPCODE**

> C2015_A to C2019_A, as worded in C2019_A: Classification of instrucional Program (CIP) code. A six-digit code in the form xx.xxxx that identifies instructional program specialties within educational institutions.

> C2020_A to C2025_A, as worded in C2025_A: Classification of instrucional Program (CIP) code. A six-digit code in the form xx.xxxx that identifies instructional program specialties within educational institutions. The Classification of Instructional Programs (CIP) provides a taxonomic scheme that supports the accurate tracking and reporting of fields of study and program completions activity. CIP was originally developed by the U.S. Department of Education's National Center for Education Statistics (NCES) in 1980, with revisions occurring in 1985, 1990, 2000, 2010 and 2021. Information on the CIP classification taxonomy, including a crosswalk between CIP 2010 and 2021 is available at https://nces.ed.gov/ipeds/cipcode/resources.aspx?y=56

**MAJORNUM**

> C2025_A: First or Second Major

**AWLEVEL**

> C2015_A to C2019_A, as worded in C2019_A: Award level code

> C2020_A to C2025_A, as worded in C2025_A: Award level code The twelve award levels under which completions can be reported are: Certificates of less than 12 weeks includes programs of less than 300 clock hours, or, Less than 9 SEMESTER or TRIMESTER credit hours, or Less than 13 QUARTER credit hours Certificates of at least 12 weeks but less than 1 year includes programs of 300-899 clock hours, or 9-29 SEMESTER or TRIMESTER credit hours, or 13-44 QUARTER credit hours Certificates of at least 1 year but less the 2 years includes programs of at least 900, but less than 1800 clock hours, or at least 30, but less than 60 SEMESTER OR TRIMESTER HOURS, or at least 45, but less than 90 QUARTER HOURS Associate's degree Certificates of at least 2 years but less the 4 years includes programs of 1800 or more clock hours, or 60 or more SEMESTER OR TRIMESTER credit hours, or 90 or more QUARTER credit hours Bachelor's degree Postbaccalaureate certificate Master's degree Post-master's certificate Doctor's degree - research/scholarship Doctor's degree - professional practice Doctor's degree - other

**CTOTALT**

> C2015_A to C2024_A, as worded in C2024_A: Awards/degrees conferred between July 1, 2023 and June 30, 2024 to all recipients, across all race/ethnicities and both genders

> C2025_A, as worded in C2025_A: Awards/degrees conferred between July 1, 2024 and June 30, 2025 to all recipients, across all race/ethnicities and both sex categories.


## Business majors (EF2014CP to EF2024CP, even years)

| Variable | Title in the dictionary | How it's used |
| --- | --- | --- |
| CIPCODE | CIP Code for major field of study | Only 52.0000 is used. EF CP reports a fixed list of fields, and 52.0000 is the business row. |
| LSTUDY | Level of student | Selects undergraduate and graduate totals. |
| EFTOTLT | Grand total | The count. |

| Variable | Code | Label in the dictionary | How it's used |
| --- | --- | --- | --- |
| LSTUDY | 2 | All students, Undergraduate total | Numerator of business_major_share_of_ug. |
| LSTUDY | 12 | All students, Graduate | Business graduate enrollment, context only. |

business_major_share_of_ug = EFTOTLT where CIPCODE = 52.0000 and LSTUDY = 2, divided by EFDETOT where EFDELEV = 2 in EF A_DIST for the same fall. EF CP has no all-fields total, and EF A_DIST's undergraduate total is the same fall headcount.

Descriptions:

**CIPCODE**

> EF2024CP: CIP Code for major field of study

**LSTUDY**

> EF2024CP: Level of student

**EFTOTLT**

> EF2024CP: Grand total men and women enrolled for credit during the fall. CREDIT - Recognition of attendance or performance in an instructional activity (course or program) that can be applied by a recipient toward the requirements for a degree, diploma, certificate, or other formal award. NOTE: Enrollment reported is of the institution's official fall reporting date or October 15. Applicable to four-year institutions


## Distance education (EF2014A_DIST to EF2024A_DIST)

| Variable | Title in the dictionary | How it's used |
| --- | --- | --- |
| EFDELEV | Level of student | Selects undergraduate and graduate rows. |
| EFDETOT | All students enrolled | Denominator of both online shares, and of business_major_share_of_ug. |
| EFDEEXC | Students enrolled exclusively in distance education courses | Numerator of both online shares. |

| Variable | Code | Label in the dictionary | How it's used |
| --- | --- | --- | --- |
| EFDELEV | 2 | Undergraduate total | pct_ug_exclusively_online, business_major_share_of_ug. |
| EFDELEV | 12 | Graduate | pct_grad_exclusively_online. |

pct_ug_exclusively_online = EFDEEXC / EFDETOT where EFDELEV = 2. pct_grad_exclusively_online uses EFDELEV = 12. Before comparing these across schools I'll check how each reports online campuses; Purdue Global, for example, reports as its own institution.

Descriptions:

**EFDELEV**

> EF2024A_DIST: Level and degree-seeking/non degree-seeking status of student - This variable identifies the level of enrollment data for the institution. Enrollment counts are available by level of student (undergraduate or graduate). Undergraduate enrollments are disaggregated by degree-seeking and non-degree seeking status. Undergraduate A student enrolled in a 4- or 5-year bachelor's degree program, an associate's degree program, or a vocational or technical program below the baccalaureate. Degree/certificate-seeking students Students enrolled in courses for credit and recognized by the institution as seeking a degree, certificate, or other formal award. High school students also enrolled in postsecondary courses for credit are not considered degree/certificate-seeking. Graduate student A student who holds a bachelor's degree or above and is taking courses at the postbaccalaureate level. These students may or may not be enrolled in graduate programs.

**EFDETOT**

> EF2024A_DIST: Grand total enrolled for credit during the fall CREDIT - Recognition of attendance or performance in an instructional activity (course or program) that can be applied by a recipient toward the requirements for a degree, diploma, certificate, or other formal award. NOTE: Enrollment reported is of the institution's official fall reporting date or October 15.

**EFDEEXC**

> EF2024A_DIST: Students who are enrolled only in courses that are considered distance education courses. NOTE: Includes only students enrolled for credit as of the institution's official fall reporting date or October 15. Distance education course - A course in which the instructional content is delivered exclusively via distance education. Requirements for coming to campus for orientation, testing, or academic support services do not exclude a course from being classified as distance education. Distance education - Education that uses one or more technologies to deliver instruction to students who are separated from the instructor and to support regular and substantive interaction between the students and the instructor synchronously or asynchronously. Technologies used for instruction may include the following: Internet; one-way and two-way transmissions through open broadcasts, closed circuit, cable, microwave, broadband lines, fiber optics, satellite or wireless communication devices; audio conferencing; and video cassette, DVDs, and CD-ROMs, if the cassette, DVDs, and CD-ROMs are used in a course in conjunction with the technologies listed above.


## Pell gap (GR2016_PELL_SSL to GR2024_PELL_SSL, optional)

| Variable | Title in the dictionary | How it's used |
| --- | --- | --- |
| PSGRTYPE | Cohort type | Selects the bachelor's-seeking cohort. |
| PGADJCT | Pell Grant recipients - adjusted cohort (revised minus exclusions) | Pell recipients in the cohort. |
| PGCMBAC | Pell Grant recipients - number that completed a bachelor's or equivalent degree within 150% of normal time | Pell recipients who finished a bachelor's within six years. |
| SSADJCT | GR2016_PELL_SSL to GR2021_PELL_SSL: Subsidized Stafford Loan recipients not receiving Pell Grants - adjusted cohort (revised minus exclusions)<br>GR2022_PELL_SSL to GR2024_PELL_SSL: Direct Subsidized Loan recipients not receiving Pell Grants - adjusted cohort (revised minus exclusions) | Part of the non-Pell cohort. |
| SSCMBAC | GR2016_PELL_SSL to GR2021_PELL_SSL: Subsidized Stafford Loan recipients not receiving Pell Grants - number completed a bachelor's or equivalent within 150% of normal time<br>GR2022_PELL_SSL to GR2024_PELL_SSL: Direct Subsidized Loan recipients not receiving Pell Grants - number completed a bachelor's or equivalent within 150% of normal time | Part of the non-Pell completers. |
| NRADJCT | GR2016_PELL_SSL to GR2021_PELL_SSL: Did not receive Pell grant or subsidized Stafford loan - adjusted cohort (revised minus exclusions)<br>GR2022_PELL_SSL to GR2024_PELL_SSL: Did not receive Pell grant or Direct Subsidized loan - adjusted cohort (revised minus exclusions) | Part of the non-Pell cohort. |
| NRCMBAC | GR2016_PELL_SSL to GR2021_PELL_SSL: Did not receive Pell grant or subsidized Stafford loan - number that completed a bachelor's or equivalent degree within 150% of normal time<br>GR2022_PELL_SSL to GR2024_PELL_SSL: Did not receive Pell grant or Direct Subsidized loan - number that completed a bachelor's or equivalent degree within 150% of normal time | Part of the non-Pell completers. |

| Variable | Code | Label in the dictionary | How it's used |
| --- | --- | --- | --- |
| PSGRTYPE | 2 | Bachelor's degree seeking 2018 cohort - four-year institutions | All Pell gap rows. |

pell_gap_6yr = PGCMBAC / PGADJCT minus (SSCMBAC + NRCMBAC) / (SSADJCT + NRADJCT), in percentage points. Non-Pell students are the two groups that did not receive a Pell Grant, combined as a sum of numerators over a sum of denominators. The loan program's name changes from subsidized Stafford to Direct Subsidized in GR2022_PELL_SSL; the group being counted does not change.

Descriptions:

**PSGRTYPE**

> GR2016_PELL_SSL to GR2019_PELL_SSL, as worded in GR2019_PELL_SSL: This variable describes the four cohorts contained in this data table. 1. Full-time, first-time, degree/certificate-seeking cohort that entered in 2013. This is the sum of the bachelor's and other than bachelor's degree seeking cohort. (4-year nstitutions) 2.Full-time first-time bachelor's or equivalent degree-seeking subcohort that entered in 2013. (4-year institutions) 3. Full-time first-time other degree/certificate-seeking subcohort that entered in 2013. (4-year institutions) 4. Full-time, first-time, degree/certificate-seeking cohort that entered in 2016. (2-year and less-than 2-year institutions) Full-time first-time student (undergraduate) A student who has no prior postsecondary experience (except as noted below) attending any institution for the first time at the undergraduate level. This includes students enrolled in academic or occupational programs. It also includes students enrolled in the fall term who attended college for the first time in the prior summer term, and students who entered with advanced standing (college credits earned before graduation from high school). Full-time undergraduate students are enrolled for 12 or more semester credits, or 12 or more quarter credits, or 24 or more contact hours a week each term. Bachelor's or equivalent degree-seeking subcohort - A cohort of students who were seeking a bachelor's or equivalent degree upon entry. Other degree/certificate-seeking subcohort - A subset of students belonging to a GR cohort who were seeking a degree or certificate other than bachelor's degree upon entry.

> GR2020_PELL_SSL to GR2024_PELL_SSL, as worded in GR2024_PELL_SSL: This variable describes the four cohorts contained in this data table. 1. Full-time, first-time, degree/certificate-seeking cohort that entered in 2018. This is the sum of the bachelor's and other than bachelor's degree seeking cohort. (4-year nstitutions) 2.Full-time first-time bachelor's or equivalent degree-seeking subcohort that entered in 2018. (4-year institutions) 3. Full-time first-time other degree/certificate-seeking subcohort that entered in 2018. (4-year institutions) 4. Full-time, first-time, degree/certificate-seeking cohort that entered in 2021. (2-year and less-than 2-year institutions) Full-time first-time student (undergraduate) A student who has no prior postsecondary experience (except as noted below) attending any institution for the first time at the undergraduate level. This includes students enrolled in academic or occupational programs. It also includes students enrolled in the fall term who attended college for the first time in the prior summer term, and students who entered with advanced standing (college credits earned before graduation from high school). Full-time undergraduate students are enrolled for 12 or more semester credits, or 12 or more quarter credits, or 24 or more clock hours a week each term. Bachelor's or equivalent degree-seeking subcohort - A cohort of students who were seeking a bachelor's or equivalent degree upon entry. Other degree/certificate-seeking subcohort - A subset of students belonging to a GR cohort who were seeking a degree or certificate other than bachelor's degree upon entry.

**PGADJCT**

> GR2024_PELL_SSL: This is the number of Pell grant recipients in the revised cohort minus the number of exclusions.

**PGCMBAC**

> GR2024_PELL_SSL: This is the number of Pell grant recipients of the cohorts specified: total cohort (PSGRTYPE=1), bachelor's cohort (PSGRTYPE=2), other than bachelor's cohort (PSGRTYPE=3) that completed a bachelor's degree in 150% percent of normal time 6-years (4-year institutions only) 150 percent of normal time to complete - Students who completed their program within 150% of the normal (or expected) time for completion. Normal time is the amount of time necessary for a student to complete all requirements for a degree or certificate according to the institution's catalog. This is typically 4 years (8 semesters or trimesters, or 12 quarters, excluding summer terms) for a bachelor's degree in a standard term-based institution; 2 years (4 semesters or trimesters, or 6 quarters, excluding summer terms) for an associate's degree in a standard term-based institution; and the various scheduled times for certificate programs.

**SSADJCT**

> GR2024_PELL_SSL: This is the number of subsidized Staff loan recipients who did not receive a Pell Grant in the revised cohort minus the number of exclusions.

**SSCMBAC**

> GR2016_PELL_SSL to GR2021_PELL_SSL, as worded in GR2021_PELL_SSL: This is the number of subsidized Stafford loan recipients who did not receive a pell grant of the cohorts specified: total cohort (PSGRTYPE=1), bachelor's cohort (PSGRTYPE=2), other than bachelor's cohort (PSGRTYPE=3) that completed a bachelor's degree in 150% percent of normal time 6-years (4-year institutions only) 150 percent of normal time to complete - Students who completed their program within 150% of the normal (or expected) time for completion. Normal time is the amount of time necessary for a student to complete all requirements for a degree or certificate according to the institution's catalog. This is typically 4 years (8 semesters or trimesters, or 12 quarters, excluding summer terms) for a bachelor's degree in a standard term-based institution; 2 years (4 semesters or trimesters, or 6 quarters, excluding summer terms) for an associate's degree in a standard term-based institution; and the various scheduled times for certificate programs.

> GR2022_PELL_SSL to GR2024_PELL_SSL, as worded in GR2024_PELL_SSL: This is the number of Direct Subsidized loan recipients who did not receive a pell grant of the cohorts specified: total cohort (PSGRTYPE=1), bachelor's cohort (PSGRTYPE=2), other than bachelor's cohort (PSGRTYPE=3) that completed a bachelor's degree in 150% percent of normal time 6-years (4-year institutions only) 150 percent of normal time to complete - Students who completed their program within 150% of the normal (or expected) time for completion. Normal time is the amount of time necessary for a student to complete all requirements for a degree or certificate according to the institution's catalog. This is typically 4 years (8 semesters or trimesters, or 12 quarters, excluding summer terms) for a bachelor's degree in a standard term-based institution; 2 years (4 semesters or trimesters, or 6 quarters, excluding summer terms) for an associate's degree in a standard term-based institution; and the various scheduled times for certificate programs.

**NRADJCT**

> GR2016_PELL_SSL to GR2021_PELL_SSL, as worded in GR2021_PELL_SSL: This is the number of students not receiving a Pell grant or subsidized Stafford loan in the revised cohort minus the number of exclusions.

> GR2022_PELL_SSL to GR2024_PELL_SSL, as worded in GR2024_PELL_SSL: This is the number of students not receiving a Pell grant or Direct Subsidized loan in the revised cohort minus the number of exclusions.

**NRCMBAC**

> GR2016_PELL_SSL to GR2021_PELL_SSL, as worded in GR2021_PELL_SSL: This is the number of students not receiving a Pell grant or subsidized Stafford loan of the cohorts specified: total cohort (PSGRTYPE=1), bachelor's cohort (PSGRTYPE=2), other than bachelor's cohort (PSGRTYPE=3) that completed a bachelor's degree in 150% percent of normal time 6-years (4-year institutions only) 150 percent of normal time to complete - Students who completed their program within 150% of the normal (or expected) time for completion. Normal time is the amount of time necessary for a student to complete all requirements for a degree or certificate according to the institution's catalog. This is typically 4 years (8 semesters or trimesters, or 12 quarters, excluding summer terms) for a bachelor's degree in a standard term-based institution; 2 years (4 semesters or trimesters, or 6 quarters, excluding summer terms) for an associate's degree in a standard term-based institution; and the various scheduled times for certificate programs.

> GR2022_PELL_SSL to GR2024_PELL_SSL, as worded in GR2024_PELL_SSL: This is the number of students not receiving a Pell grant or Direct Subsidized loan of the cohorts specified: total cohort (PSGRTYPE=1), bachelor's cohort (PSGRTYPE=2), other than bachelor's cohort (PSGRTYPE=3) that completed a bachelor's degree in 150% percent of normal time 6-years (4-year institutions only) 150 percent of normal time to complete - Students who completed their program within 150% of the normal (or expected) time for completion. Normal time is the amount of time necessary for a student to complete all requirements for a degree or certificate according to the institution's catalog. This is typically 4 years (8 semesters or trimesters, or 12 quarters, excluding summer terms) for a bachelor's degree in a standard term-based institution; 2 years (4 semesters or trimesters, or 6 quarters, excluding summer terms) for an associate's degree in a standard term-based institution; and the various scheduled times for certificate programs.

