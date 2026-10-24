-- Every DMI curriculum row's class levels add up to its stated total.
select fall_year, program_code, major_code, conc_code
from {{ ref('stg_dmi__curriculum') }}
group by fall_year, program_code, major_code, conc_code, total_students
having sum(coalesce(headcount, 0)) is distinct from total_students
