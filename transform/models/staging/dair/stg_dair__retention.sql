-- First-fall to second-fall retention of first-time, full-time, degree-seeking students, by
-- college of entry. Counts only; DAIR's rate rows are recomputed from them downstream.
select
    "Entry College" as entry_college,
    cast(regexp_extract("Fall Cohort", '([0-9]{4})', 1) as integer) as cohort_year,
    case "Measure"
        when 'Number Retained' then 'retained'
        when 'Size of Adjusted Cohort' then 'adjusted_cohort'
    end as measure,
    {{ to_count('"Value"') }} as value
from {{ source('dair', 'retention_by_entry_college') }}
where "Measure" in ('Number Retained', 'Size of Adjusted Cohort')
