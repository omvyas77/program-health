-- A1 Illinois against the other 17 Big Ten schools, latest data year of each metric
-- Peer statistics leave Illinois out; the public median also leaves out Northwestern and USC.
-- Rank 1 is the highest value. Change runs from the most recent year at least five years before
-- the latest, which is six years for business_major_share_of_ug (IPEDS collects it in even years).
with metrics as (
    select
        *,
        case
            when metric in (
                'applicants', 'business_bachelors', 'business_masters',
                'business_bachelors_incl_307102', 'business_masters_incl_307102'
            ) then 'count'
            when metric = 'pell_gap_6yr' then 'gap'
            else 'rate'
        end as kind
    from {{ ref('mart_peer_metrics') }}
    where is_illinois
),

latest as (
    select metric, max(data_year) as data_year
    from metrics
    group by metric
),

base_years as (
    select l.metric, max(m.data_year) as data_year
    from latest as l
    inner join metrics as m on m.metric = l.metric and m.data_year <= l.data_year - 5
    group by l.metric
),

paired as (
    select
        now.*,
        before.data_year_label as base_label,
        now.value - before.value as illinois_change,
        now.peer_median_excl_il - before.peer_median_excl_il as peer_change
    from metrics as now
    inner join latest as l on l.metric = now.metric and l.data_year = now.data_year
    left join base_years as b on b.metric = now.metric
    left join metrics as before on before.metric = b.metric and before.data_year = b.data_year
)

select
    metric as "Metric",
    data_year_label as "Data year",
    case kind
        when 'count' then {{ fmt_int('value') }}
        when 'gap' then {{ fmt_pts('value') }}
        else {{ fmt_pct('value') }}
    end as "Illinois",
    case kind
        when 'count' then {{ fmt_int('peer_median_excl_il') }}
        when 'gap' then {{ fmt_pts('peer_median_excl_il') }}
        else {{ fmt_pct('peer_median_excl_il') }}
    end as "Peer median",
    case kind
        when 'count' then {{ fmt_int('peer_p25') }} || ' to ' || {{ fmt_int('peer_p75') }}
        when 'gap' then {{ fmt_pts('peer_p25') }} || ' to ' || {{ fmt_pts('peer_p75') }}
        else {{ fmt_pct('peer_p25') }} || ' to ' || {{ fmt_pct('peer_p75') }}
    end as "Peer IQR",
    case kind
        when 'count' then {{ fmt_int('public_peer_median_excl_il') }}
        when 'gap' then {{ fmt_pts('public_peer_median_excl_il') }}
        else {{ fmt_pct('public_peer_median_excl_il') }}
    end as "Public peer median",
    rank_of_18 || ' of ' || n_ranked as "Rank",
    case kind
        when 'count' then {{ fmt_change('illinois_change') }}
        else {{ fmt_pts('illinois_change') }}
    end as "Illinois change",
    case kind
        when 'count' then {{ fmt_change('peer_change') }}
        else {{ fmt_pts('peer_change') }}
    end as "Peer median change",
    base_label as "Change since",
    case when is_provisional then 'yes' else '' end as "Provisional"
from paired
order by metric
