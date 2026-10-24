-- DAIR's College, Class, Type sheet. "First Year Student" is DMI's "First time Freshman".
select
    cast(regexp_extract("Semester", '([0-9]{4})', 1) as integer) as fall_year,
    "College" as college,
    case "Student Type"
        when 'First Year Student' then 'first_time_freshman'
        when 'New Transfer' then 'new_transfer'
        when 'Readmit & Returning' then 'readmit'
        when 'Continuing & Nondegree' then 'continuing'
    end as student_type,
    case "Class"
        when 'Freshman' then 'freshman'
        when 'Sophomore' then 'sophomore'
        when 'Junior' then 'junior'
        when 'Senior' then 'senior'
        when 'Non-degree' then 'non_degree'
        when 'Total' then 'total'
    end as class,
    {{ to_count('"Count"') }} as headcount
from {{ source('dair', 'college_class_type') }}
