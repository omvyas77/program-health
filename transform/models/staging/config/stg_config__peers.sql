select
    cast(unitid as integer) as unitid,
    short_name as school,
    state,
    control,
    cast(unitid as integer) = 145637 as is_illinois,
    control = 'public' as is_public
from {{ source('config', 'peers') }}
