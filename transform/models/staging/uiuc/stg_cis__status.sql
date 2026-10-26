-- Enrollment status from the daily pass over the Gies course pages, one row per CRN and day.
-- Empty, with its columns typed, until the first pass writes a file.
-- depends_on: {{ source('uiuc', 'cis_status') }}
{% if files_exist('data/snapshots/cis_status/*/*.csv') %}
select
    cast(regexp_extract(filename, '([0-9]{4}-[0-9]{2}-[0-9]{2})\.csv$', 1) as date) as snapshot_date,
    regexp_extract(filename, '([0-9]{4}-[a-z]{2})/[^/]+$', 1) as term,
    cast(snapshot_utc as timestamp) as snapshot_utc,
    crn,
    status
from {{ source('uiuc', 'cis_status') }}
{% else %}
select
    cast(null as date) as snapshot_date,
    cast(null as varchar) as term,
    cast(null as timestamp) as snapshot_utc,
    cast(null as varchar) as crn,
    cast(null as varchar) as status
where false
{% endif %}
