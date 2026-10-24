-- One row per school, metric, and data year. Peer statistics leave Illinois out; the public
-- median also leaves out Northwestern and USC. Rank 1 is the highest value among schools
-- reporting that year.
with metric_values as (
    select v.*, p.school, p.is_illinois, p.control
    from {{ ref('int_peer_metric_values') }} as v
    inner join {{ ref('stg_config__peers') }} as p on p.unitid = v.unitid
),

peer_stats as (
    select
        metric,
        data_year,
        median(value) filter (where not is_illinois) as peer_median_excl_il,
        quantile_cont(value, 0.25) filter (where not is_illinois) as peer_p25,
        quantile_cont(value, 0.75) filter (where not is_illinois) as peer_p75,
        median(value) filter (where not is_illinois and control = 'public')
            as public_peer_median_excl_il
    from metric_values
    group by metric, data_year
)

select
    v.unitid,
    v.school,
    v.is_illinois,
    v.control,
    v.metric,
    v.data_year,
    v.data_year_label,
    cast(v.value as double) as value,
    cast(v.numerator as bigint) as numerator,
    cast(v.denominator as bigint) as denominator,
    s.peer_median_excl_il,
    s.peer_p25,
    s.peer_p75,
    s.public_peer_median_excl_il,
    cast(rank() over (partition by v.metric, v.data_year order by v.value desc) as integer)
        as rank_of_18,
    cast(count(*) over (partition by v.metric, v.data_year) as integer) as n_ranked,
    v.is_provisional,
    v.source_file
from metric_values as v
inner join peer_stats as s on s.metric = v.metric and s.data_year = v.data_year
