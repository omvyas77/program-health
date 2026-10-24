-- Every peer metric as numerator, denominator, and value, one row per school, metric, and data
-- year. Rates are fractions; counts carry no denominator; pell_gap_6yr is a difference.
with business as (
    select cipcode, is_optional from {{ ref('stg_config__cip_business') }}
),

admissions as (
    select unitid, 'admit_rate' as metric, data_year, data_year_label, admits as numerator,
        applicants as denominator, is_provisional, source_file
    from {{ ref('stg_ipeds__adm') }}
    union all
    select unitid, 'yield_rate', data_year, data_year_label, enrolled, admits, is_provisional,
        source_file
    from {{ ref('stg_ipeds__adm') }}
    union all
    select unitid, 'applicants', data_year, data_year_label, applicants, null, is_provisional,
        source_file
    from {{ ref('stg_ipeds__adm') }}
),

retention as (
    select unitid, 'ft_retention_rate' as metric, data_year, data_year_label,
        retained as numerator, adjusted_cohort as denominator, is_provisional, source_file
    from {{ ref('stg_ipeds__ef_d') }}
),

graduation as (
    -- Bachelor's subcohort: GRTYPE 8 is the adjusted cohort, 13 the completers within four
    -- years, 12 the completers within six (150% of normal time).
    select
        unitid,
        unnest(['grad_rate_4yr', 'grad_rate_6yr']) as metric,
        data_year,
        data_year_label,
        unnest([
            sum(grand_total) filter (where grtype = 13),
            sum(grand_total) filter (where grtype = 12)
        ]) as numerator,
        sum(grand_total) filter (where grtype = 8) as denominator,
        bool_or(is_provisional) as is_provisional,
        any_value(source_file) as source_file
    from {{ ref('stg_ipeds__gr') }}
    group by unitid, data_year, data_year_label
),

first_majors as (
    select c.*, b.cipcode is not null and not b.is_optional as is_business,
        b.cipcode is not null as is_business_incl_307102
    from {{ ref('stg_ipeds__c_a') }} as c
    left join business as b on b.cipcode = c.cipcode
    where c.majornum = 1 and c.cipcode != '99'
),

completions as (
    select
        unitid,
        data_year,
        data_year_label,
        bool_or(is_provisional) as is_provisional,
        any_value(source_file) as source_file,
        sum(completions) filter (where award_level = 5 and is_business) as bachelors,
        sum(completions) filter (where award_level = 5 and is_business_incl_307102) as bachelors_incl,
        sum(completions) filter (where award_level = 7 and is_business) as masters,
        sum(completions) filter (where award_level = 7 and is_business_incl_307102) as masters_incl,
        sum(completions) filter (where award_level = 5) as all_bachelors
    from first_majors
    group by unitid, data_year, data_year_label
),

completion_metrics as (
    select unitid, 'business_bachelors' as metric, data_year, data_year_label,
        bachelors as numerator, null as denominator, is_provisional, source_file
    from completions
    union all
    select unitid, 'business_bachelors_incl_307102', data_year, data_year_label, bachelors_incl,
        null, is_provisional, source_file
    from completions
    union all
    select unitid, 'business_masters', data_year, data_year_label, masters, null,
        is_provisional, source_file
    from completions
    union all
    select unitid, 'business_masters_incl_307102', data_year, data_year_label, masters_incl,
        null, is_provisional, source_file
    from completions
    union all
    select unitid, 'business_share_of_bachelors', data_year, data_year_label, bachelors,
        all_bachelors, is_provisional, source_file
    from completions
    union all
    select unitid, 'business_share_of_bachelors_incl_307102', data_year, data_year_label,
        bachelors_incl, all_bachelors, is_provisional, source_file
    from completions
),

distance as (
    select unitid, data_year, data_year_label, is_provisional, source_file,
        max(enrolled_total) filter (where efdelev = 2) as ug_total,
        max(enrolled_exclusively_distance) filter (where efdelev = 2) as ug_online,
        max(enrolled_total) filter (where efdelev = 12) as grad_total,
        max(enrolled_exclusively_distance) filter (where efdelev = 12) as grad_online
    from {{ ref('stg_ipeds__ef_dist') }}
    group by unitid, data_year, data_year_label, is_provisional, source_file
),

distance_metrics as (
    select unitid, 'pct_ug_exclusively_online' as metric, data_year, data_year_label,
        ug_online as numerator, ug_total as denominator, is_provisional, source_file
    from distance
    union all
    select unitid, 'pct_grad_exclusively_online', data_year, data_year_label, grad_online,
        grad_total, is_provisional, source_file
    from distance
),

business_majors as (
    -- EF CP has no all-fields total, so undergraduates come from EF A_DIST for the same fall.
    select
        cp.unitid,
        'business_major_share_of_ug' as metric,
        cp.data_year,
        cp.data_year_label,
        cp.enrollment as numerator,
        d.ug_total as denominator,
        cp.is_provisional or d.is_provisional as is_provisional,
        cp.source_file || ', ' || d.source_file as source_file
    from {{ ref('stg_ipeds__ef_cp') }} as cp
    inner join distance as d on d.unitid = cp.unitid and d.data_year = cp.data_year
    where cp.cipcode = '52.0000' and cp.lstudy = 2
),

counted as (
    select * from admissions
    union all select * from retention
    union all select * from graduation
    union all select * from completion_metrics
    union all select * from distance_metrics
    union all select * from business_majors
),

pell_gap as (
    -- Non-Pell students are those with a subsidized loan only plus those with neither,
    -- combined as a sum of numerators over a sum of denominators.
    select
        unitid,
        'pell_gap_6yr' as metric,
        data_year,
        data_year_label,
        cast(null as bigint) as numerator,
        cast(null as bigint) as denominator,
        pell_bachelors_completers / pell_adjusted_cohort
        - (loan_only_bachelors_completers + neither_bachelors_completers)
        / (loan_only_adjusted_cohort + neither_adjusted_cohort) as value,
        is_provisional,
        source_file
    from {{ ref('stg_ipeds__gr_pell') }}
    where psgrtype = 2
)

select
    unitid,
    metric,
    data_year,
    data_year_label,
    numerator,
    denominator,
    case
        when denominator is null then cast(numerator as double)
        else numerator / nullif(denominator, 0)
    end as value,
    is_provisional,
    source_file
from counted
where numerator is not null
union all
select * from pell_gap
where value is not null
