-- Undergraduate student types by class, from DMI's ten-day Statistical Abstract.
select
    cast(fall as integer) as fall_year,
    case "Student Type"
        when 'First time Freshman' then 'first_time_freshman'
        when 'New Transfer' then 'new_transfer'
        when 'Readmit & Returning' then 'readmit'
        when 'Continuing & Nondegree' then 'continuing'
        when 'Total' then 'total'
    end as student_type,
    {{ to_count('"Fresh"') }} as freshman,
    {{ to_count('"Soph"') }} as sophomore,
    {{ to_count('"Junior"') }} as junior,
    {{ to_count('"Senior"') }} as senior,
    {{ to_count('"ND"') }} as non_degree,
    {{ to_count('"Total"') }} as total
from {{ source('dmi', 'student_type') }}
