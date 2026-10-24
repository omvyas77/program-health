-- Applicants, admits, and enrolled for first-time, first-year students. IPEDS gives totals;
-- the Common Data Set adds Fall 2025 and the residency split, once each value is verified.
with ipeds as (
    select unitid, data_year as fall_year, 'ipeds' as source, 'all' as residency,
        applicants, admits, enrolled, is_provisional
    from {{ ref('stg_ipeds__adm') }}
),

cds as (
    select unitid, fall_year, 'cds' as source, 'all' as residency,
        applicants_total as applicants, admits_total as admits, enrolled_total as enrolled,
        false as is_provisional
    from {{ ref('stg_cds__c1') }}
    union all
    select unitid, fall_year, 'cds', 'in_state', applicants_in_state, admits_in_state,
        enrolled_in_state, false
    from {{ ref('stg_cds__c1') }}
    union all
    select unitid, fall_year, 'cds', 'out_of_state', applicants_out_of_state,
        admits_out_of_state, enrolled_out_of_state, false
    from {{ ref('stg_cds__c1') }}
    union all
    select unitid, fall_year, 'cds', 'international', applicants_international,
        admits_international, enrolled_international, false
    from {{ ref('stg_cds__c1') }}
),

funnel as (
    select * from ipeds
    union all
    select * from cds
    where applicants is not null or admits is not null or enrolled is not null
)

select
    f.unitid,
    p.school,
    p.is_illinois,
    p.control,
    f.fall_year,
    'Fall ' || f.fall_year as fall_term,
    f.source,
    f.residency,
    cast(f.applicants as bigint) as applicants,
    cast(f.admits as bigint) as admits,
    cast(f.enrolled as bigint) as enrolled,
    cast(f.admits / nullif(f.applicants, 0) as double) as admit_rate,
    cast(f.enrolled / nullif(f.admits, 0) as double) as yield_rate,
    f.is_provisional
from funnel as f
inner join {{ ref('stg_config__peers') }} as p on p.unitid = f.unitid
