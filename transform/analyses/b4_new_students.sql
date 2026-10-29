-- B4 New Gies first-time freshmen and transfers, Fall 2012 to Fall 2026
-- Class levels come from credit hours, so many first-time freshmen start with sophomore standing.
select
    fall_year as "Fall",
    {{ fmt_int("sum(headcount) filter (where student_type = 'first_time_freshman')") }}
        as "First-time freshmen",
    {{ fmt_int("sum(coalesce(sophomore, 0) + coalesce(junior, 0) + coalesce(senior, 0)) filter (where student_type = 'first_time_freshman')") }}
        as "Of whom sophomore standing or above",
    {{ fmt_int("sum(headcount) filter (where student_type = 'new_transfer')") }} as "New transfers",
    any_value(source) as "Source"
from {{ ref('mart_gies_new_students') }}
group by fall_year
order by fall_year
