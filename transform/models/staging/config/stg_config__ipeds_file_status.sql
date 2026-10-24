-- Each file belongs to collection Y to Y+1 and to the season its survey is collected in; it is
-- provisional while that collection and season have only a provisional release.
with files as (
    select
        file,
        family,
        cast(regexp_extract(file, '20[0-9]{2}') as integer) as file_year
    from {{ source('config', 'ipeds_files') }}
),

collections as (
    select
        *,
        file_year || '-' || right(cast(file_year + 1 as varchar), 2) as collection,
        case
            when family in ('hd', 'c_a') then 'Fall'
            when family in ('adm', 'gr', 'gr_pell') then 'Winter'
            else 'Spring'
        end as season
    from files
)

select
    c.file,
    c.family,
    c.file_year,
    c.collection,
    c.season,
    coalesce(r.release_type, 'final') as release_type,
    coalesce(r.release_type, 'final') = 'provisional' as is_provisional
from collections as c
left join {{ source('config', 'ipeds_releases') }} as r
    on r.collection = c.collection and r.season = c.season
