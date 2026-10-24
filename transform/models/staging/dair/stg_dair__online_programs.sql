select
    cast(regexp_extract("Term", '([0-9]{4})', 1) as integer) as fall_year,
    "College" as college,
    "Academic Program Code" as program_code,
    "Level" as level,
    {{ to_count('"Count"') }} as headcount
from {{ source('dair', 'online_programs') }}
