select
    cast(unitid as integer) as unitid,
    file,
    reason
from {{ source('config', 'ipeds_exclusions') }}
