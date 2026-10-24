-- 6c.5 Watch list: Gies undergraduate courses averaging 150 or more graded students per term offered, with 15% or more at C or below or withdrawing in at least two of the last four long terms
-- Thresholds chosen Oct 24, 2026. A course on this list is a question for its department about
-- preparation, placement, and support, not a verdict on its teaching.
{%- set min_graded = 150 %}
{%- set min_rate = 0.15 %}
{%- set min_terms = 2 %}
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
        sum(c.students_graded) as graded,
        sum(c.w) as w,
        sum(c.c_or_below_w) as c_or_below_w,
        sum(c.dfw) as dfw
    from {{ ref('int_course_terms') }} as c
    inner join last_four as l on l.yearterm = c.yearterm
    where c.is_gies and c.is_undergraduate
    group by c.yearterm, c.year, c.term, c.subject, c.number
),

courses as (
    select
        subject,
        number,
        max(course_title) as course_title,
        count(*) as terms_offered,
        avg(graded) as avg_graded,
        count(*) filter (where c_or_below_w / (graded + w) >= {{ min_rate }}) as terms_at_threshold,
        string_agg(
            yearterm || ' ' || {{ fmt_pct('c_or_below_w / (graded + w)') }}, ', '
            order by {{ term_order('year', 'term') }}
        ) as by_term,
        sum(c_or_below_w) / sum(graded + w) as pooled_c_or_below_w,
        sum(dfw) / sum(graded + w) as pooled_dfw
    from course_terms
    group by subject, number
)

select
    subject || ' ' || number as "Course",
    course_title as "Title",
    terms_offered as "Terms offered",
    {{ fmt_int('avg_graded') }} as "Graded per term offered",
    terms_at_threshold as "Terms at 15% or more",
    by_term as "C or below or W, by term",
    {{ fmt_pct('pooled_c_or_below_w') }} as "C or below or W, four terms",
    {{ fmt_pct('pooled_dfw') }} as "DFW, four terms"
from courses
where avg_graded >= {{ min_graded }} and terms_at_threshold >= {{ min_terms }}
order by subject, number
