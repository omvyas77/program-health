-- 6c.6 Spread of section GPAs within Gies undergraduate courses with three or more sections, last four long terms
-- Sorted by course. No section or instructor is identified.
with last_four as (
    select yearterm, year, term
    from (select distinct yearterm, year, term from {{ ref('int_course_terms') }})
    where term in ('Fall', 'Spring')
    order by {{ term_order('year', 'term') }} desc
    limit 4
)

select
    s.subject || ' ' || s.number as "Course",
    s.yearterm as "Term",
    s.n_sections as "Sections",
    {{ fmt_int('s.students_graded') }} as "Graded",
    {{ fmt_gpa('s.gpa_min') }} as "Lowest section GPA",
    {{ fmt_gpa('s.gpa_max') }} as "Highest section GPA",
    {{ fmt_gpa('s.gpa_max - s.gpa_min') }} as "Range",
    {{ fmt_gpa('s.gpa_sd') }} as "Standard deviation"
from {{ ref('mart_section_spread') }} as s
inner join last_four as l on l.yearterm = s.yearterm
where try_cast(s.number as integer) < 500
order by s.subject, s.number, {{ term_order('l.year', 'l.term') }}
