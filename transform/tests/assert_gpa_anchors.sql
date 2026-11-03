-- GPA dataset anchors, as of wadefagen/datasets commit c8d2678 (the Oct 29, 2026 update, which
-- added Spring and Summer 2026 and the previously unavailable Fall 2005 to Summer 2009, Summer
-- 2011, and Spring 2012). The row count covers every term through Winter 2026, so a later commit
-- that adds new terms still passes and one that revises or backfills those terms fails. Every
-- term from Spring 2010 on matched commit c6618ca row for row and student for student.
with checks as (
    select
        count(*) filter (where year < 2026 or yearterm = '2026-wi') as rows_total,
        min(students) as smallest_section,
        count(*) filter (
            where students != a_plus + a + a_minus + b_plus + b + b_minus + c_plus + c + c_minus
                + d_plus + d + d_minus + f
        ) as rows_not_summing,
        sum(students) filter (
            where yearterm = '2025-fa' and subject in ('ACCY', 'BADM', 'BUS', 'FIN')
        ) as fall_2025_graded,
        count(distinct subject || number) filter (
            where yearterm = '2025-fa' and subject in ('ACCY', 'BADM', 'BUS', 'FIN')
        ) as fall_2025_courses
    from {{ ref('stg_gpa') }}
)

select *
from checks
-- coalesce: a missing value must fail the test, not slip through as null.
where not coalesce(
    rows_total = 107758 and smallest_section = 21 and rows_not_summing = 0
    and fall_2025_graded = 26571 and fall_2025_courses = 126,
    false
)
