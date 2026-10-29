-- Common Data Set C1, only the rows checked by hand against each school's file.
select
    cast(unitid as integer) as unitid,
    cds_year,
    cast(left(cds_year, 4) as integer) as fall_year,
    fall_term,
    {{ to_count('applicants_total') }} as applicants_total,
    {{ to_count('admits_total') }} as admits_total,
    {{ to_count('enrolled_total') }} as enrolled_total,
    {{ to_count('applicants_in_state') }} as applicants_in_state,
    {{ to_count('admits_in_state') }} as admits_in_state,
    {{ to_count('enrolled_in_state') }} as enrolled_in_state,
    {{ to_count('applicants_out_of_state') }} as applicants_out_of_state,
    {{ to_count('admits_out_of_state') }} as admits_out_of_state,
    {{ to_count('enrolled_out_of_state') }} as enrolled_out_of_state,
    {{ to_count('applicants_international') }} as applicants_international,
    {{ to_count('admits_international') }} as admits_international,
    {{ to_count('enrolled_international') }} as enrolled_international,
    source_url,
    verified_by,
    cast(nullif(verified_on, '') as date) as verified_on
from {{ source('manual', 'cds_c1') }}
