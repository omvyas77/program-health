-- 6b.1 Gies headcount by program family and modality, Fall 2017 to Fall 2026
-- DMI through Fall 2025, DAIR for Fall 2026.
with families as (
    select level, program_family, modality, fall_year, sum(headcount) as headcount
    from {{ ref('mart_gies_enrollment') }}
    where fall_year between 2017 and 2026
    group by level, program_family, modality, fall_year
),

level_totals as (
    select level, 'All ' || level as program_family, 'all' as modality, fall_year,
        sum(headcount) as headcount
    from families
    group by level, fall_year
),

college_total as (
    select 'all' as level, 'All Gies' as program_family, 'all' as modality, fall_year,
        sum(headcount) as headcount
    from families
    group by fall_year
),

all_rows as (
    select * from families
    union all
    select * from level_totals
    union all
    select * from college_total
)

select
    level as "Level",
    program_family as "Program family",
    modality as "Modality",
    {%- for y in range(2017, 2027) %}
    {{ fmt_int('sum(headcount) filter (where fall_year = ' ~ y ~ ')') }} as "Fall {{ y }}",
    {%- endfor %}
    {{ fmt_change('sum(headcount) filter (where fall_year = 2026) - sum(headcount) filter (where fall_year = 2021)') }}
        as "Change, Fall 2021 to Fall 2026",
    printf(
        '%+.1f%%',
        100 * (sum(headcount) filter (where fall_year = 2026)
        / sum(headcount) filter (where fall_year = 2021) - 1)
    ) as "Percent change"
from all_rows
group by level, program_family, modality
order by
    case level when 'undergraduate' then 1 when 'graduate' then 2 else 3 end,
    program_family like 'All %',
    program_family,
    modality
