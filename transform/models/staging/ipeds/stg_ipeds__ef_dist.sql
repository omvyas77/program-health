{{ ipeds_rows('ef_dist') }}

select
    unit_id as unitid,
    source_file,
    file_year as data_year,
    'Fall ' || file_year as data_year_label,
    is_provisional,
    {{ to_code('EFDELEV') }} as efdelev,
    {{ to_count('EFDETOT') }} as enrolled_total,
    {{ to_count('EFDEEXC') }} as enrolled_exclusively_distance
from rows
