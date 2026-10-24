-- Undergraduate student types by class: DMI's ten-day abstracts, with DAIR filling the falls
-- DMI does not cover (Fall 2024, which the archive never captured, and Fall 2026).
with dmi as (
    select fall_year, student_type, freshman, sophomore, junior, senior, non_degree, total,
        'dmi' as source
    from {{ ref('stg_dmi__student_type') }}
    where student_type != 'total'
),

dair as (
    pivot (
        select fall_year, student_type, class, headcount
        from {{ ref('stg_dair__class_type') }}
    )
    on class in ('freshman', 'sophomore', 'junior', 'senior', 'non_degree', 'total')
    using sum(headcount)
),

dair_missing_from_dmi as (
    select
        fall_year, student_type, freshman, sophomore, junior, senior, non_degree, total,
        'dair' as source
    from dair
    where fall_year not in (select fall_year from dmi)
)

select * from dmi
union all
select * from dair_missing_from_dmi
