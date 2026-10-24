-- DAIR's Data Table - Curriculum and Level, with DAIR's measure names mapped to DMI's class
-- levels. DAIR labels the doctoral column "Grad 2 (Master)"; it holds the PhD students.
select
    cast(regexp_extract("Term Display", 'Fall ([0-9]{4})', 1) as integer) as fall_year,
    "Academic Program Code" as program_code,
    "Dept Code" as dept_code,
    "Department" as department,
    "Major Code" as major_code,
    "Major Name" as major_name,
    {{ blank_to_empty('"Conc Code"') }} as conc_code,
    nullif(trim("Concentration Name"), '') as conc_name,
    trim("Measure Names") as measure,
    case trim("Measure Names")
        when 'Freshman' then 'freshman'
        when 'Sophomore' then 'sophomore'
        when 'Junior' then 'junior'
        when 'Senior' then 'senior'
        when 'Non-Degree Undergrad' then 'ndeg_ugrad'
        when 'Grad 1 (Master)' then 'grad_1'
        when 'Grad 2 (Master)' then 'grad_2'
        when 'Non-Degree Grad' then 'ndeg_grad'
        when 'Total Professional' then 'professional'
    end as class_level,
    {{ to_count('"Measure Values"') }} as headcount,
    file
from {{ source('dair', 'curriculum_level') }}
