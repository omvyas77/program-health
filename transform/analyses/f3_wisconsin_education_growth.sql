-- F3 Where UW-Madison's growth in education degrees came from, by CIP series, three-year totals 2014-15 to 2016-17 against 2022-23 to 2024-25
-- Totals, not averages, so the rows add to the change. A series new to the later window is a
-- program that began conferring degrees in between, or a program recoded into it. Series are
-- four-digit, so 13.1099, which first appears in 2024-25 as 13.1001 falls, stays in the
-- Special Education row.
with spans as (
    select
        degree_level,
        series,
        series_label,
        sum(completions) filter (where award_year_end between 2015 and 2017) as early,
        sum(completions) filter (where award_year_end between 2023 and 2025) as late
    from {{ ref('mart_education_completions') }}
    where is_wisconsin and is_education and degree_level in ('Bachelor''s', 'Master''s')
    group by all
),

changes as (
    select
        *,
        coalesce(late, 0) - coalesce(early, 0) as change,
        sum(coalesce(late, 0) - coalesce(early, 0)) over (partition by degree_level) as level_change
    from spans
)

select
    degree_level as "Degree level",
    series as "Series",
    series_label as "Field",
    {{ fmt_int('coalesce(early, 0)') }} as "2014-15 to 2016-17",
    {{ fmt_int('coalesce(late, 0)') }} as "2022-23 to 2024-25",
    {{ fmt_change('change') }} as "Change",
    {{ fmt_pct('change / level_change') }} as "Share of level's change"
from changes
where coalesce(early, 0) + coalesce(late, 0) > 0
order by degree_level, changes.change desc
