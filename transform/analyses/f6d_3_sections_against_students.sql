-- 6d.3 Gies courses where primary sections and graded students moved in opposite directions, Fall 2019 to Fall 2025
-- Sections are distinct CRNs in the catalog; graded students come from the GPA dataset, which
-- leaves out sections with 20 or fewer graded students. Courses must appear in both terms in
-- both sources.
with sections as (
    select c.yearterm, c.subject, c.number, count(distinct c.crn) as sections
    from {{ ref('stg_catalog') }} as c
    inner join {{ ref('int_type_codes') }} as t on t.type_code = c.type_code
    where t.is_primary and c.yearterm in ('2019-fa', '2025-fa')
    group by c.yearterm, c.subject, c.number
),

students as (
    select yearterm, subject, number, sum(students_graded) as graded
    from {{ ref('int_course_terms') }}
    where is_gies and yearterm in ('2019-fa', '2025-fa')
    group by yearterm, subject, number
),

courses as (
    select
        s.subject,
        s.number,
        max(s.sections) filter (where s.yearterm = '2019-fa') as sections_2019,
        max(s.sections) filter (where s.yearterm = '2025-fa') as sections_2025,
        max(g.graded) filter (where g.yearterm = '2019-fa') as graded_2019,
        max(g.graded) filter (where g.yearterm = '2025-fa') as graded_2025
    from sections as s
    inner join students as g
        on g.yearterm = s.yearterm and g.subject = s.subject and g.number = s.number
    group by s.subject, s.number
)

select
    case
        when sections_2025 < sections_2019 then 'Fewer sections, more students'
        else 'More sections, fewer students'
    end as "Direction",
    subject || ' ' || number as "Course",
    sections_2019 as "Sections, Fall 2019",
    sections_2025 as "Sections, Fall 2025",
    {{ fmt_int('graded_2019') }} as "Graded, Fall 2019",
    {{ fmt_int('graded_2025') }} as "Graded, Fall 2025"
from courses
where (sections_2025 < sections_2019 and graded_2025 > graded_2019)
    or (sections_2025 > sections_2019 and graded_2025 < graded_2019)
order by 1, subject, number
