-- C{Y}_A: awards conferred from July 1 of Y-1 to June 30 of Y.
{{ ipeds_rows('c_a') }}

select
    unit_id as unitid,
    source_file,
    file_year as data_year,
    (file_year - 1) || '-' || right(cast(file_year as varchar), 2) as academic_year,
    'July ' || (file_year - 1) || ' to June ' || file_year as data_year_label,
    is_provisional,
    trim(CIPCODE) as cipcode,
    {{ to_code('MAJORNUM') }} as majornum,
    {{ to_code('AWLEVEL') }} as award_level,
    {{ to_count('CTOTALT') }} as completions
from rows
