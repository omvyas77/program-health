-- First-year retention and four- and six-year graduation for first-time, full-time,
-- degree-seeking students, by college of entry, from DAIR's counts. "All colleges" sums the
-- colleges' counts. DAIR reports graduates by year after entry, so a four-year rate adds the
-- 3- and 4-year groups and a six-year rate adds all four.
with retention as (
    select
        entry_college,
        cohort_year,
        'first_year_retention' as outcome,
        max(value) filter (where measure = 'retained') as numerator,
        max(value) filter (where measure = 'adjusted_cohort') as denominator
    from {{ ref('stg_dair__retention') }}
    group by entry_college, cohort_year
),

graduation as (
    select
        entry_college,
        cohort_year,
        max(value) filter (where measure = 'adjusted_cohort') as cohort,
        coalesce(sum(value) filter (where measure = 'graduates' and years_after_entry <= 4), 0)
            as graduates_4yr,
        coalesce(sum(value) filter (where measure = 'graduates'), 0) as graduates_6yr
    from {{ ref('stg_dair__graduation') }}
    group by entry_college, cohort_year
),

by_college as (
    select * from retention
    union all
    select entry_college, cohort_year, 'grad_4yr', graduates_4yr, cohort from graduation
    union all
    select entry_college, cohort_year, 'grad_6yr', graduates_6yr, cohort from graduation
),

all_colleges as (
    select 'All colleges' as entry_college, cohort_year, outcome, sum(numerator) as numerator,
        sum(denominator) as denominator
    from by_college
    group by cohort_year, outcome
)

select
    entry_college,
    entry_college = 'Gies College of Business' as is_gies,
    cohort_year,
    outcome,
    cast(numerator as bigint) as numerator,
    cast(denominator as bigint) as denominator,
    cast(numerator / nullif(denominator, 0) as double) as rate
from (select * from by_college union all select * from all_colleges)
