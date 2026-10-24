{{ ipeds_rows('hd') }}

select
    unit_id as unitid,
    source_file,
    file_year as data_year,
    file_year || '-' || right(cast(file_year + 1 as varchar), 2) as data_year_label,
    is_provisional,
    trim(INSTNM) as institution_name,
    trim(CITY) as city,
    trim(STABBR) as state,
    {{ to_code('CONTROL') }} as control_code
from rows
