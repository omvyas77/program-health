-- F1 Education degrees (CIP 13) at the 18 Big Ten schools, three-year averages, 2014-15 to 2016-17 against 2022-23 to 2024-25
-- First majors only. Each average is over the years a school reported; Penn State's 2019-20 and
-- 2020-21 files are excluded (docs/data_notes.md) but neither window uses them. 2024-25 is a
-- provisional IPEDS release. Rank 1 is the most degrees in the later window.
with windows as (
    select
        school,
        is_wisconsin,
        degree_level,
        case
            when award_year_end between 2015 and 2017 then 'early'
            when award_year_end between 2023 and 2025 then 'late'
        end as span,
        award_year_end,
        sum(completions) as n
    from {{ ref('mart_education_completions') }}
    where is_education and (award_year_end between 2015 and 2017 or award_year_end between 2023 and 2025)
    group by all
),

averages as (
    select
        school,
        is_wisconsin,
        degree_level,
        avg(n) filter (where span = 'early') as early,
        avg(n) filter (where span = 'late') as late
    from windows
    group by all
),

pivoted as (
    select
        school,
        is_wisconsin,
        max(early) filter (where degree_level = 'Bachelor''s') as ba_early,
        max(late) filter (where degree_level = 'Bachelor''s') as ba_late,
        max(early) filter (where degree_level = 'Master''s') as ma_early,
        max(late) filter (where degree_level = 'Master''s') as ma_late,
        max(early) filter (where degree_level = 'Doctoral') as doc_early,
        max(late) filter (where degree_level = 'Doctoral') as doc_late
    from averages
    group by all
)

select
    school as "School",
    {{ fmt_int('ba_early') }} as "Bachelor's, early",
    {{ fmt_int('ba_late') }} as "Bachelor's, late",
    case when ba_early >= 20 then {{ fmt_pct_change('ba_late', 'ba_early') }} end as "Bachelor's change",
    rank() over (order by coalesce(ba_late, 0) desc) || ' of 18' as "Bachelor's rank",
    {{ fmt_int('ma_early') }} as "Master's, early",
    {{ fmt_int('ma_late') }} as "Master's, late",
    case when ma_early >= 20 then {{ fmt_pct_change('ma_late', 'ma_early') }} end as "Master's change",
    {{ fmt_int('doc_early') }} as "Doctoral, early",
    {{ fmt_int('doc_late') }} as "Doctoral, late",
    case when doc_early >= 20 then {{ fmt_pct_change('doc_late', 'doc_early') }} end as "Doctoral change"
from pivoted
order by is_wisconsin desc, coalesce(ba_late, 0) desc
