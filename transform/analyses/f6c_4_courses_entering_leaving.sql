-- 6c.4 Gies undergraduate courses graded in only one of Fall 2015 and Fall 2025
with courses as (
    select
        yearterm,
        subject,
        number,
        max(course_title) as course_title,
        sum(students_graded) as graded,
        sum(a_range) as a_range
    from {{ ref('int_course_terms') }}
    where is_gies and is_undergraduate and yearterm in ('2015-fa', '2025-fa')
    group by yearterm, subject, number
),

single_term as (
    select subject, number
    from courses
    group by subject, number
    having count(*) = 1
)

select
    case c.yearterm when '2015-fa' then 'Fall 2015 only' else 'Fall 2025 only' end as "Taught in",
    c.subject || ' ' || c.number as "Course",
    c.course_title as "Title",
    {{ fmt_int('c.graded') }} as "Graded",
    {{ fmt_pct('c.a_range / c.graded') }} as "A-range share"
from courses as c
inner join single_term as s on s.subject = c.subject and s.number = c.number
order by c.yearterm, c.subject, c.number
