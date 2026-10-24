{{ ipeds_rows('ef_cp') }}

select
    unit_id as unitid,
    source_file,
    file_year as data_year,
    'Fall ' || file_year as data_year_label,
    is_provisional,
    trim(CIPCODE) as cipcode,
    {{ to_code('LSTUDY') }} as lstudy,
    {{ to_count('EFTOTLT') }} as enrollment
from rows
