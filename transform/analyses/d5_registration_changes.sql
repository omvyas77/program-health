-- D5 Spring 2027 Gies courses that gained or lost primary sections since the previous snapshot
select
    snapshot_date as "Snapshot",
    days_since_registration_open as "Days since registration opened",
    subject || ' ' || number as "Course",
    primary_sections as "Primary sections",
    sections_added_since_previous as "Added",
    sections_removed_since_previous as "Removed"
from {{ ref('mart_registration_watch') }}
where sections_added_since_previous > 0 or sections_removed_since_previous > 0
order by snapshot_date, subject, number
