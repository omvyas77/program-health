{{ ipeds_rows('gr_pell') }}

select
    unit_id as unitid,
    source_file,
    file_year - 6 as data_year,
    (file_year - 6) || ' cohort' as data_year_label,
    is_provisional,
    {{ to_code('PSGRTYPE') }} as psgrtype,
    {{ to_count('PGADJCT') }} as pell_adjusted_cohort,
    {{ to_count('PGCMBAC') }} as pell_bachelors_completers,
    {{ to_count('SSADJCT') }} as loan_only_adjusted_cohort,
    {{ to_count('SSCMBAC') }} as loan_only_bachelors_completers,
    {{ to_count('NRADJCT') }} as neither_adjusted_cohort,
    {{ to_count('NRCMBAC') }} as neither_bachelors_completers
from rows
