-- EF{Y}D: the full-time fall {Y-1} cohort, enrolled again in fall Y.
{{ ipeds_rows('ef_d') }}

select
    unit_id as unitid,
    source_file,
    file_year as data_year,
    'Fall ' || (file_year - 1) || ' cohort returning in fall ' || file_year as data_year_label,
    is_provisional,
    {{ to_count('RRFTCTA') }} as adjusted_cohort,
    {{ to_count('RET_NMF') }} as retained,
    {{ to_count('RET_PCF') }} as reported_retention_pct
from rows
