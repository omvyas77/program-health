select
    fall_year,
    'Fall ' || fall_year as fall_term,
    student_type,
    cast(total as bigint) as headcount,
    cast(freshman as bigint) as freshman,
    cast(sophomore as bigint) as sophomore,
    cast(junior as bigint) as junior,
    cast(senior as bigint) as senior,
    cast(non_degree as bigint) as non_degree,
    source
from {{ ref('int_new_students') }}
