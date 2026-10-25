-- One row per Gies course and term: primary sections offered, from the catalog, next to graded
-- sections and students, from the GPA dataset. Primary sections are counted as distinct CRNs, so
-- a section listed with two primary meeting types counts once. The catalog starts in Fall 2016
-- and the GPA data holds only sections with 21 or more graded students, so either side can be
-- empty for a course-term.
with primary_sections as (
    select c.yearterm, c.year, c.term, c.subject, c.number, count(distinct c.crn) as sections
    from {{ ref('stg_catalog') }} as c
    inner join {{ ref('int_type_codes') }} as t on t.type_code = c.type_code
    where t.is_primary
    group by c.yearterm, c.year, c.term, c.subject, c.number
),

graded as (
    select
        yearterm,
        year,
        term,
        subject,
        number,
        sum(graded_sections) as graded_sections,
        sum(students_graded) as students_graded
    from {{ ref('int_course_terms') }}
    where is_gies
    group by yearterm, year, term, subject, number
),

joined as (
    select
        coalesce(p.yearterm, g.yearterm) as yearterm,
        coalesce(p.year, g.year) as year,
        coalesce(p.term, g.term) as term,
        coalesce(p.subject, g.subject) as subject,
        coalesce(p.number, g.number) as number,
        p.sections as primary_sections,
        g.graded_sections,
        g.students_graded
    from primary_sections as p
    full outer join graded as g
        on g.yearterm = p.yearterm and g.subject = p.subject and g.number = p.number
)

select
    yearterm,
    cast(year as integer) as year,
    term,
    subject,
    number,
    subject || ' ' || number as course,
    cast(least(floor(try_cast(number as integer) / 100) * 100, 500) as integer) as course_level,
    try_cast(number as integer) < 500 as is_undergraduate,
    cast(primary_sections as bigint) as primary_sections,
    cast(graded_sections as bigint) as graded_sections,
    cast(students_graded as bigint) as students_graded,
    cast(students_graded / graded_sections as double) as students_per_graded_section
from joined
