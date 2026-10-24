-- Sections offered by course, term, and schedule type, counted as distinct CRNs so a section
-- listed on several catalog lines (one per meeting) counts once.
select
    c.yearterm,
    c.subject,
    c.number,
    coalesce(c.type_code, 'UNKNOWN') as type_code,
    t.type_label,
    case when c.type_code is null then 'unknown' when t.is_online then 'online' else 'in_person' end
        as mode,
    cast(count(distinct c.crn) as bigint) as sections,
    coalesce(t.is_primary, false) as is_primary_type
from {{ ref('stg_catalog') }} as c
left join {{ ref('int_type_codes') }} as t on t.type_code = c.type_code
group by c.yearterm, c.subject, c.number, c.type_code, t.type_label, t.is_online, t.is_primary
