-- D4 Spring 2027 primary sections in each daily snapshot, Gies subjects
-- Registration opens Nov 2, 2026. The Course Explorer API carries no enrollment status, so the
-- watch tracks sections added and removed, not seats or closed sections.
select
    snapshot_date as "Snapshot",
    days_since_registration_open as "Days since registration opened",
    sum(primary_sections) as "Primary sections",
    count(*) filter (where primary_sections > 0) as "Courses",
    sum(sections_added_since_previous) as "Added since previous",
    sum(sections_removed_since_previous) as "Removed since previous",
    sum(sections_added_since_open) as "Added since registration opened"
from {{ ref('mart_registration_watch') }}
group by snapshot_date, days_since_registration_open
order by snapshot_date
