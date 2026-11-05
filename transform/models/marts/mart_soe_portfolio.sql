-- UW-Madison degrees in the fields the School of Education houses today, by award year, degree
-- level, and CIP code. IPEDS reports by field, not by school or college, so this is a first-pass
-- map (config/cip_soe_map.csv) with a confidence for each code, to be reconciled against
-- RADAR's Trends in Degrees before any number is used. Codes not in the map are left out.
with degrees as (
    select
        cipcode,
        academic_year,
        data_year,
        is_provisional,
        case
            when award_level = 5 then 'Bachelor''s'
            when award_level = 7 then 'Master''s'
            else 'Doctoral'
        end as degree_level,
        completions
    from {{ ref('stg_ipeds__c_a') }}
    where
        unitid = {{ var('soe_unitid') }}
        and majornum = 1
        and award_level in (5, 7, 17, 18, 19)
        and cipcode <> '99'
),

mapped as (
    select
        d.*,
        m.field_group,
        m.department,
        m.confidence
    from degrees as d
    inner join {{ ref('stg_config__cip_soe_map') }} as m
        on m.cipcode = d.cipcode
        or (m.cipcode = '13' and d.cipcode like '13.%')
)

select
    academic_year,
    data_year as award_year_end,
    degree_level,
    cipcode,
    field_group,
    department,
    confidence,
    cast(sum(completions) as bigint) as completions,
    bool_or(is_provisional) as is_provisional
from mapped
group by all
