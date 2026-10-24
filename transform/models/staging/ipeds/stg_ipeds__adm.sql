-- ADM{Y} covers first-time, degree-seeking undergraduates entering in fall Y.
{{ ipeds_rows('adm') }}

select
    unit_id as unitid,
    source_file,
    file_year as data_year,
    'Fall ' || file_year || ' entering class' as data_year_label,
    is_provisional,
    {{ to_count('APPLCN') }} as applicants,
    {{ to_count('ADMSSN') }} as admits,
    {{ to_count('ENRLT') }} as enrolled
from rows
