-- F4 UW-Madison degrees in the fields the School of Education houses today, 2024-25, through the first-pass CIP map
-- A first pass, not School of Education totals: IPEDS reports by field, and config/cip_soe_map.csv
-- carries a confidence for each code. Reconcile against RADAR's Trends in Degrees before use.
-- 2024-25 is a provisional IPEDS release.
with latest as (
    select field_group, degree_level, confidence, sum(completions) as n
    from {{ ref('mart_soe_portfolio') }}
    where award_year_end = 2025
    group by all
),

groups as (
    select
        field_group,
        sum(n) filter (where degree_level = 'Bachelor''s') as ba,
        sum(n) filter (where degree_level = 'Master''s') as ma,
        sum(n) filter (where degree_level = 'Doctoral') as doc,
        sum(n) as total,
        sum(n) filter (where confidence = 'medium') as medium
    from latest
    group by all
)

select
    field_group as "Field group",
    {{ fmt_int('coalesce(ba, 0)') }} as "Bachelor's",
    {{ fmt_int('coalesce(ma, 0)') }} as "Master's",
    {{ fmt_int('coalesce(doc, 0)') }} as "Doctoral",
    {{ fmt_int('total') }} as "All degrees",
    {{ fmt_pct('total / sum(total) over ()') }} as "Share of mapped degrees",
    {{ fmt_int('coalesce(medium, 0)') }} as "From medium-confidence codes"
from groups
order by total desc
