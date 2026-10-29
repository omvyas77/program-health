-- D6 Spring 2027 Gies courses that added primary sections 3, 7, and 14 days after registration opened
-- Day 3 is Nov 5, day 7 is Nov 9, and day 14 is Nov 16, 2026.
with at_open as (
    select subject, number, primary_sections
    from {{ ref('mart_registration_watch') }}
    where snapshot_date = (
        select max(snapshot_date)
        from {{ ref('mart_registration_watch') }}
        where days_since_registration_open <= 0
    )
),

later as (
    select
        subject,
        number,
        max(sections_added_since_open) filter (where days_since_registration_open = 3) as day_3,
        max(sections_added_since_open) filter (where days_since_registration_open = 7) as day_7,
        max(sections_added_since_open) filter (where days_since_registration_open = 14) as day_14
    from {{ ref('mart_registration_watch') }}
    where days_since_registration_open in (3, 7, 14)
    group by subject, number
)

select
    l.subject || ' ' || l.number as "Course",
    o.primary_sections as "Primary sections when registration opened",
    l.day_3 as "Added by day 3",
    l.day_7 as "Added by day 7",
    l.day_14 as "Added by day 14"
from later as l
left join at_open as o on o.subject = l.subject and o.number = l.number
where coalesce(l.day_3, 0) + coalesce(l.day_7, 0) + coalesce(l.day_14, 0) > 0
order by l.subject, l.number
