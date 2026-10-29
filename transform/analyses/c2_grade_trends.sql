-- C2 Fitted linear trend per year in undergraduate grades, covid_grading terms left out
-- Least-squares slope on term-level rates, fall and spring terms fitted separately.
with by_group as (
    select
        yearterm,
        year,
        term,
        is_gies,
        sum(students_graded) as graded,
        sum(grade_points) as points,
        sum(a_range) as a_range,
        sum(dfw) as dfw,
        sum(w) as w
    from {{ ref('int_course_terms') }}
    where is_undergraduate and term in ('Fall', 'Spring')
    group by yearterm, year, term, is_gies
),

groups as (
    select yearterm, year, term, 'Gies' as courses, graded, points, a_range, dfw, w
    from by_group
    where is_gies
    union all
    select yearterm, year, term, 'Campus', sum(graded), sum(points), sum(a_range), sum(dfw), sum(w)
    from by_group
    group by yearterm, year, term
),

rates as (
    select
        courses,
        term,
        year,
        points / graded as gpa,
        a_range / graded as a_range_share,
        dfw / (graded + w) as dfw_rate
    from groups
    where yearterm not in (
        select yearterm from {{ ref('stg_config__term_flags') }} where term_flag = 'covid_grading'
    )
)

select
    courses as "Courses",
    term as "Terms",
    count(*) || ' terms, ' || min(year) || ' to ' || max(year) as "Fitted on",
    printf('%+.3f', regr_slope(gpa, year)) as "GPA per year",
    printf('%+.2f pts', 100 * regr_slope(a_range_share, year)) as "A-range per year",
    printf('%+.2f pts', 100 * regr_slope(dfw_rate, year)) as "DFW per year",
    printf('%.2f', regr_r2(a_range_share, year)) as "R squared, A-range"
from rates
group by courses, term
order by courses desc, term
