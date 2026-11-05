-- F2 Education degrees by award year, UW-Madison against the other Big Ten schools combined, indexed to 2014-15 = 100
-- The combined line leaves out Penn State (var soe_peer_line_excludes), whose 2019-20 and
-- 2020-21 files are excluded, so it is the same 16 schools every year. 2024-25 is provisional.
with yearly as (
    select
        award_year_end,
        academic_year,
        degree_level,
        sum(completions) filter (where is_wisconsin) as wisconsin,
        sum(completions) filter (
            where not is_wisconsin and unitid not in ({{ var('soe_peer_line_excludes') | join(', ') }})
        ) as others
    from {{ ref('mart_education_completions') }}
    where is_education and degree_level in ('Bachelor''s', 'Master''s')
    group by all
),

indexed as (
    select
        *,
        100.0 * wisconsin / first(wisconsin) over w as wisconsin_index,
        100.0 * others / first(others) over w as others_index
    from yearly
    window w as (partition by degree_level order by award_year_end)
)

select
    degree_level as "Degree level",
    academic_year as "Award year",
    {{ fmt_int('wisconsin') }} as "UW-Madison",
    {{ fmt_int('others') }} as "Other 16 combined",
    printf('%.0f', wisconsin_index) as "UW-Madison index",
    printf('%.0f', others_index) as "Other 16 index"
from indexed
order by degree_level, award_year_end
