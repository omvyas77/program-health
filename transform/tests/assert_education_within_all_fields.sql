-- Education degrees can't exceed the school's all-fields total at the same degree level, and every
-- school, year, and level with education degrees must carry its all-fields row.
with totals as (
    select
        unitid,
        academic_year,
        degree_level,
        sum(completions) filter (where is_education) as education,
        sum(completions) filter (where not is_education) as all_fields
    from {{ ref('mart_education_completions') }}
    group by all
)

select *
from totals
where education > 0 and (all_fields is null or education > all_fields)
