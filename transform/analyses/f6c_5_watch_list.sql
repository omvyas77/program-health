-- 6c.5 Watch list: Gies undergraduate courses averaging 150 or more graded students per term offered, with 15% or more at C or below or withdrawing in at least two of the last four long terms
-- Thresholds chosen Oct 24, 2026, and kept as the watch_* vars in dbt_project.yml; the list itself
-- is mart_course_watch_list. A course on this list is a question for its department about
-- preparation, placement, and support, not a verdict on its teaching.
select
    course as "Course",
    course_title as "Title",
    any_value(terms_offered) as "Terms offered",
    {{ fmt_int('any_value(graded_per_term_offered)') }} as "Graded per term offered",
    any_value(terms_at_threshold) as "Terms at 15% or more",
    string_agg(
        yearterm || ' ' || {{ fmt_pct('c_or_below_w_rate') }}, ', '
        order by {{ term_order('year', 'term') }}
    ) as "C or below or W, by term",
    {{ fmt_pct('any_value(course_c_or_below_w_rate)') }} as "C or below or W, four terms",
    {{ fmt_pct('any_value(course_dfw_rate)') }} as "DFW, four terms"
from {{ ref('mart_course_watch_list') }}
where is_on_watch_list
group by subject, number, course, course_title
order by subject, number
