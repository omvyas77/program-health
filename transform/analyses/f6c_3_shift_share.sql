-- 6c.3 Change in A-range share in Gies undergraduate courses, Fall 2015 to Fall 2025, split into within-course change, course mix, and their interaction
-- The split uses courses taught in both terms, weighted by their share of graded students.
-- Within-course: sum of w0 * (s1 - s0). Mix: sum of s0 * (w1 - w0). Interaction: sum of
-- (w1 - w0) * (s1 - s0). The three add up to the change among courses taught in both terms.
with courses as (
    select yearterm, subject, number, sum(students_graded) as graded, sum(a_range) as a_range
    from {{ ref('int_course_terms') }}
    where is_gies and is_undergraduate and yearterm in ('2015-fa', '2025-fa')
    group by yearterm, subject, number
),

in_both as (
    select subject, number
    from courses
    group by subject, number
    having count(*) = 2
),

weighted as (
    select
        c.yearterm,
        c.subject,
        c.number,
        c.graded,
        c.graded / sum(c.graded) over (partition by c.yearterm) as weight,
        c.a_range / c.graded as share
    from courses as c
    inner join in_both as b on b.subject = c.subject and b.number = c.number
),

paired as (
    select
        f15.weight as w0,
        f25.weight as w1,
        f15.share as s0,
        f25.share as s1,
        f15.graded as graded_2015,
        f25.graded as graded_2025
    from weighted as f15
    inner join weighted as f25
        on f25.subject = f15.subject and f25.number = f15.number and f25.yearterm = '2025-fa'
    where f15.yearterm = '2015-fa'
),

parts as (
    select
        count(*) as n_courses,
        sum(graded_2015) as graded_2015,
        sum(graded_2025) as graded_2025,
        sum(w0 * s0) as share_2015,
        sum(w1 * s1) as share_2025,
        sum(w0 * (s1 - s0)) as within_course,
        sum(s0 * (w1 - w0)) as course_mix,
        sum((w1 - w0) * (s1 - s0)) as interaction
    from paired
),

all_courses as (
    select
        count(*) filter (where yearterm = '2015-fa') as n_2015,
        count(*) filter (where yearterm = '2025-fa') as n_2025,
        sum(graded) filter (where yearterm = '2015-fa') as graded_2015,
        sum(graded) filter (where yearterm = '2025-fa') as graded_2025,
        sum(a_range) filter (where yearterm = '2015-fa')
        / sum(graded) filter (where yearterm = '2015-fa') as share_2015,
        sum(a_range) filter (where yearterm = '2025-fa')
        / sum(graded) filter (where yearterm = '2025-fa') as share_2025
    from courses
)

select 1 as "Row", 'All courses: A-range share, Fall 2015' as "Measure",
    {{ fmt_pct('share_2015') }} || ' of ' || {{ fmt_int('graded_2015') }} || ' graded in '
    || n_2015 || ' courses' as "Value"
from all_courses
union all
select 2, 'All courses: A-range share, Fall 2025',
    {{ fmt_pct('share_2025') }} || ' of ' || {{ fmt_int('graded_2025') }} || ' graded in '
    || n_2025 || ' courses'
from all_courses
union all
select 3, 'All courses: change', {{ fmt_pts('share_2025 - share_2015') }} from all_courses
union all
select 4, 'Courses taught in both terms: A-range share, Fall 2015',
    {{ fmt_pct('share_2015') }} || ' of ' || {{ fmt_int('graded_2015') }} || ' graded in '
    || n_courses || ' courses'
from parts
union all
select 5, 'Courses taught in both terms: A-range share, Fall 2025',
    {{ fmt_pct('share_2025') }} || ' of ' || {{ fmt_int('graded_2025') }} || ' graded'
from parts
union all
select 6, 'Courses taught in both terms: change', {{ fmt_pts('share_2025 - share_2015') }}
from parts
union all
select 7, 'Within-course change', {{ fmt_pts('within_course') }} from parts
union all
select 8, 'Course mix', {{ fmt_pts('course_mix') }} from parts
union all
select 9, 'Interaction', {{ fmt_pts('interaction') }} from parts
union all
select 10, 'Courses entering or leaving (all-course change less the change in courses taught in both)',
    {{ fmt_pts('(a.share_2025 - a.share_2015) - (p.share_2025 - p.share_2015)') }}
from all_courses as a, parts as p
order by 1
