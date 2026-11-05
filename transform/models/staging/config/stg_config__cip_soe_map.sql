select
    cipcode,
    field_group,
    department,
    confidence,
    note
from {{ source('config', 'cip_soe_map') }}
