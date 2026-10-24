select
    cipcode,
    cast(is_optional as boolean) as is_optional
from {{ source('config', 'cip_business') }}
