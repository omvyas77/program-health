-- Gies undergraduate courses over the last four long terms, one row per course and term, with
-- the course-level measures and the watch-list flag repeated on each row. Thresholds are the
-- watch_* vars in dbt_project.yml. A course on the list is a question for its department about
-- preparation, placement, and support, not a verdict on its teaching.
with last_four as (
    select yearterm, year, term
    from (select distinct yearterm, year, term from {{ ref('int_course_terms') }})
    where term in ('Fall', 'Spring')
    order by {{ term_order('year', 'term') }} desc
    limit 4
),

course_terms as (
    select
        c.yearterm,
        c.year,
        c.term,
        c.subject,
        c.number,
        max(c.course_title) as course_title,
        sum(c.students_graded) as students_graded,
        sum(c.w) as w,
        sum(c.c_or_below_w) as c_or_below_w,
        sum(c.dfw) as dfw
    from {{ ref('int_course_terms') }} as c
    inner join last_four as l on l.yearterm = c.yearterm
    where c.is_gies and c.is_undergraduate
    group by c.yearterm, c.year, c.term, c.subject, c.number
),

rated as (
    select
        *,
        c_or_below_w / (students_graded + w) as c_or_below_w_rate,
        dfw / (students_graded + w) as dfw_rate
    from course_terms
),

courses as (
    select
        subject,
        number,
        count(*) as terms_offered,
        avg(students_graded) as graded_per_term_offered,
        count(*) filter (where c_or_below_w_rate >= {{ var('watch_min_rate') }})
            as terms_at_threshold,
        sum(c_or_below_w) / sum(students_graded + w) as course_c_or_below_w_rate,
        sum(dfw) / sum(students_graded + w) as course_dfw_rate
    from rated
    group by subject, number
)

select
    r.subject,
    r.number,
    r.subject || ' ' || r.number as course,
    max(r.course_title) over (partition by r.subject, r.number) as course_title,
    r.yearterm,
    r.year,
    r.term,
    cast(r.students_graded as bigint) as students_graded,
    cast(r.w as bigint) as w,
    cast(r.c_or_below_w_rate as double) as c_or_below_w_rate,
    cast(r.dfw_rate as double) as dfw_rate,
    r.c_or_below_w_rate >= {{ var('watch_min_rate') }} as is_term_at_threshold,
    cast(c.terms_offered as bigint) as terms_offered,
    cast(c.graded_per_term_offered as double) as graded_per_term_offered,
    cast(c.terms_at_threshold as bigint) as terms_at_threshold,
    cast(c.course_c_or_below_w_rate as double) as course_c_or_below_w_rate,
    cast(c.course_dfw_rate as double) as course_dfw_rate,
    c.graded_per_term_offered >= {{ var('watch_min_graded') }}
    and c.terms_at_threshold >= {{ var('watch_min_terms') }} as is_on_watch_list
from rated as r
inner join courses as c on c.subject = r.subject and c.number = r.number
