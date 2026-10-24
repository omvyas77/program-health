select
    term,
    cast(first_registration_date as date) as first_registration_date,
    cast(last_day_to_add as date) as last_day_to_add
from {{ source('config', 'registration') }}
