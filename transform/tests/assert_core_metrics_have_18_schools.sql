{{ config(severity = 'warn') }}
-- Every core metric-year should have all 18 schools, less any left out on purpose in
-- config/ipeds_exclusions.csv (Penn State, 2019 to 2021 collections). A gap nobody has explained
-- warns rather than fails, since a provisional release can be missing a school for a while.
with counts as (
    select metric, data_year, any_value(source_file) as source_file, count(*) as schools
    from {{ ref('mart_peer_metrics') }}
    where metric in (
        'ft_retention_rate', 'grad_rate_4yr', 'grad_rate_6yr', 'admit_rate', 'yield_rate',
        'applicants'
    )
    group by metric, data_year
),

excluded as (
    select file, count(distinct unitid) as schools
    from {{ ref('stg_config__ipeds_exclusions') }}
    group by file
)

select c.metric, c.data_year, c.source_file, c.schools, coalesce(e.schools, 0) as excluded
from counts as c
left join excluded as e on e.file = c.source_file
where c.schools + coalesce(e.schools, 0) < 18
