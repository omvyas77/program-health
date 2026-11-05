select
    series,
    label,
    cast(is_teacher_prep as boolean) as is_teacher_prep
from {{ source('config', 'cip_education_series') }}
