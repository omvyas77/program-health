-- GPA dataset anchors, as of wadefagen/datasets commit c6618ca.
with checks as (
    select
        count(*) as rows_total,
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
    rows_total = 79918 and smallest_section = 21 and rows_not_summing = 0
    and fall_2025_graded = 26571 and fall_2025_courses = 126,
    false
)
