-- 6a.2 Business completions with and without 30.7102 Business Analytics, Illinois and peer median
-- 30.7102 exists only in the 2020 CIP classification, used from 2019-20 awards on.
with paired as (
    select
        replace(i.metric, '_incl_307102', '') as metric,
        i.data_year,
        i.data_year_label,
        x.value as illinois_without,
        i.value as illinois_with,
        x.peer_median_excl_il as peer_without,
        i.peer_median_excl_il as peer_with,
        i.metric like '%share%' as is_share
    from {{ ref('mart_peer_metrics') }} as i
    inner join {{ ref('mart_peer_metrics') }} as x
        on x.unitid = i.unitid
        and x.data_year = i.data_year
        and x.metric = replace(i.metric, '_incl_307102', '')
    where i.is_illinois and i.metric like '%_incl_307102' and i.data_year >= 2020
)

select
    metric as "Metric",
    data_year_label as "Awards",
    case when is_share then {{ fmt_pct('illinois_without') }} else {{ fmt_int('illinois_without') }} end
        as "Illinois without 30.7102",
    case when is_share then {{ fmt_pct('illinois_with') }} else {{ fmt_int('illinois_with') }} end
        as "Illinois with 30.7102",
    case when is_share then {{ fmt_pct('peer_without') }} else {{ fmt_int('peer_without') }} end
        as "Peer median without",
    case when is_share then {{ fmt_pct('peer_with') }} else {{ fmt_int('peer_with') }} end
        as "Peer median with"
from paired
order by metric, data_year
