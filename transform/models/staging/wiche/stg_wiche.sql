select
    "Stabbr" as geography_code,
    "StateRegionUS" as geography,
    cast(regexp_extract("ClassOf", '([0-9]{4})', 1) as integer) as class_of,
    "SchoolYear" as school_year,
    "SchoolSector" as school_sector,
    "RaceEthnicity" as race_ethnicity,
    {{ to_count('"Students"') }} as graduates,
    "ActualProjected" as actual_projected
from {{ source('wiche', 'hs_graduates') }}
