-- 6c.1 Grades in undergraduate courses by long term, Gies subjects next to the whole campus
-- Sections with 21 or more graded students. covid_grading terms allowed credit/no credit and
-- nearly eliminated W, so they are flagged and left out of fitted trends. Spring 2012 was
-- removed from the source as a duplicate.
with by_group as (
    select
        yearterm,
        year,
        term,
        sum(students_graded) filter (where is_gies) as gies_graded,
        sum(grade_points) filter (where is_gies) as gies_points,
        sum(a_range) filter (where is_gies) as gies_a_range,
        sum(dfw) filter (where is_gies) as gies_dfw,
        sum(w) filter (where is_gies) as gies_w,
        sum(students_graded) as campus_graded,
        sum(grade_points) as campus_points,
        sum(a_range) as campus_a_range,
        sum(dfw) as campus_dfw,
        sum(w) as campus_w
    from {{ ref('int_course_terms') }}
    where is_undergraduate and term in ('Fall', 'Spring')
    group by yearterm, year, term
)

select
    g.yearterm as "Term",
    coalesce(f.term_flag, '') as "Flag",
    {{ fmt_int('gies_graded') }} as "Gies graded",
    {{ fmt_gpa('gies_points / gies_graded') }} as "Gies GPA",
    {{ fmt_pct('gies_a_range / gies_graded') }} as "Gies A-range",
    {{ fmt_pct('gies_dfw / (gies_graded + gies_w)') }} as "Gies DFW",
    {{ fmt_int('campus_graded') }} as "Campus graded",
    {{ fmt_gpa('campus_points / campus_graded') }} as "Campus GPA",
    {{ fmt_pct('campus_a_range / campus_graded') }} as "Campus A-range",
    {{ fmt_pct('campus_dfw / (campus_graded + campus_w)') }} as "Campus DFW"
from by_group as g
left join {{ ref('stg_config__term_flags') }} as f on f.yearterm = g.yearterm
order by {{ term_order('g.year', 'g.term') }}
