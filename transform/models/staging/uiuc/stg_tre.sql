-- Teachers Ranked as Excellent, already counted by term, unit, and role at ingest.
select
    right(term, 4) || '-' || left(term, 2) as yearterm,
    unit,
    role,
    cast(listings as integer) as listings
from {{ source('uiuc', 'tre') }}
