-- B2 Online programs' share of Gies graduate headcount, Fall 2012 to Fall 2026
-- DMI lists no Gies program code ending in U, the online marker, before Fall 2017.
select
    fall_year as "Fall",
    {{ fmt_int('sum(headcount)') }} as "Graduate headcount",
    {{ fmt_int("coalesce(sum(headcount) filter (where modality = 'online'), 0)") }} as "In online programs",
    {{ fmt_pct("coalesce(sum(headcount) filter (where modality = 'online'), 0) / sum(headcount)") }}
        as "Online share",
    any_value(source) as "Source"
from {{ ref('mart_gies_enrollment') }}
where level = 'graduate'
group by fall_year
order by fall_year
