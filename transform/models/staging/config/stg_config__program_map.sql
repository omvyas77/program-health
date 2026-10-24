select
    program_code,
    major_code,
    {{ blank_to_empty('conc_code') }} as conc_code,
    degree,
    major_name,
    program_family,
    level,
    modality
from {{ source('config', 'program_map') }}
