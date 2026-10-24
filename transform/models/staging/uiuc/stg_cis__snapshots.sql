select
    cast(regexp_extract(filename, '([0-9]{4}-[0-9]{2}-[0-9]{2})\.csv$', 1) as date) as snapshot_date,
    cast(snapshot_utc as timestamp) as snapshot_utc,
    term,
    subject,
    number,
    crn,
    section,
    upper(type_code) as type_code,
    part_of_term,
    section_status
from {{ source('uiuc', 'cis_snapshots') }}
