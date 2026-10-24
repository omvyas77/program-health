-- GR{Y} follows the cohort that entered in fall Y-6 (checked against EF D; see
-- docs/ipeds_variables.md for the two dictionaries that label this wrongly).
{{ ipeds_rows('gr') }}

select
    unit_id as unitid,
    source_file,
    file_year - 6 as data_year,
    (file_year - 6) || ' cohort' as data_year_label,
    is_provisional,
    {{ to_code('GRTYPE') }} as grtype,
    {{ to_code('COHORT') }} as cohort_code,
    {{ to_count('GRTOTLT') }} as grand_total
from rows
