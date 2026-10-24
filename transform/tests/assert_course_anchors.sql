-- Course anchors from the GPA dataset, as of wadefagen/datasets commit c6618ca.
with gies_ug as (
    select
        yearterm,
        sum(grade_points) / sum(students_graded) as gpa,
        sum(a_range) / sum(students_graded) as a_range_share,
        sum(dfw) / (sum(students_graded) + sum(w)) as dfw_rate,
        sum(students_graded) as students_graded
    from {{ ref('int_course_terms') }}
    where is_gies and is_undergraduate and yearterm in ('2010-fa', '2025-fa')
    group by yearterm
),

campus as (
    select
        yearterm,
        sum(grade_points) filter (where is_undergraduate)
        / sum(students_graded) filter (where is_undergraduate) as ug_gpa,
        sum(w) filter (where is_undergraduate) as ug_w,
        sum(w) as all_w
    from {{ ref('int_course_terms') }}
    group by yearterm
),

gies_online_500 as (
    select
        g.yearterm,
        sum(g.students) filter (where g.sched_type in ('ONL', 'OLC', 'OLB')) as online,
        sum(g.students) as total
    from {{ ref('stg_gpa') }} as g
    inner join {{ ref('stg_config__gies_subjects') }} as s on s.subject = g.subject
    where try_cast(g.number as integer) >= 500 and g.yearterm in ('2018-fa', '2025-fa')
    group by g.yearterm
),

expected as (
    select 'gies 2010-fa gpa' as anchor, round(gpa, 2) as actual, 3.38 as wanted
    from gies_ug where yearterm = '2010-fa'
    union all select 'gies 2010-fa a-range %', round(100 * a_range_share, 1), 54.4
    from gies_ug where yearterm = '2010-fa'
    union all select 'gies 2010-fa dfw %', round(100 * dfw_rate, 1), 2.8
    from gies_ug where yearterm = '2010-fa'
    union all select 'gies 2025-fa gpa', round(gpa, 2), 3.72
    from gies_ug where yearterm = '2025-fa'
    union all select 'gies 2025-fa a-range %', round(100 * a_range_share, 1), 80.0
    from gies_ug where yearterm = '2025-fa'
    union all select 'gies 2025-fa dfw %', round(100 * dfw_rate, 1), 1.4
    from gies_ug where yearterm = '2025-fa'
    union all select 'gies 2025-fa graded', students_graded, 13070
    from gies_ug where yearterm = '2025-fa'
    union all select 'campus 2010-fa ug gpa', round(ug_gpa, 2), 3.21
    from campus where yearterm = '2010-fa'
    union all select 'campus 2025-fa ug gpa', round(ug_gpa, 2), 3.52
    from campus where yearterm = '2025-fa'
    union all select 'campus ug w ' || yearterm, ug_w, wanted_w
    from campus
    inner join (
        values ('2019-sp', 450), ('2020-sp', 37), ('2020-fa', 14), ('2021-sp', 8), ('2021-fa', 1009)
    ) as v (term_key, wanted_w) on v.term_key = campus.yearterm
    union all select 'campus all-level w ' || yearterm, all_w, wanted_w
    from campus
    inner join (
        values ('2019-sp', 499), ('2020-sp', 103), ('2020-fa', 14), ('2021-sp', 10), ('2021-fa', 1077)
    ) as v (term_key, wanted_w) on v.term_key = campus.yearterm
    union all select 'gies 500+ online 2018-fa', online, 5300
    from gies_online_500 where yearterm = '2018-fa'
    union all select 'gies 500+ online 2025-fa', online, 14202
    from gies_online_500 where yearterm = '2025-fa'
    union all select 'gies 500+ total 2025-fa', total, 16997
    from gies_online_500 where yearterm = '2025-fa'
)

-- 22 anchors; a missing one fails as surely as a wrong one.
select anchor, actual, wanted from expected where actual is distinct from wanted
union all
select 'anchor count', count(*), 22 from expected having count(*) != 22
