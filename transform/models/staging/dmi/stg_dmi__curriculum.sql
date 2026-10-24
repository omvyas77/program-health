-- One row per fall, curriculum, and class level, from DMI's Enrollment by Curriculum and Class
-- Level report. The full-time and part-time columns (from Fall 2020) are not carried here.
with curricula as (
    select
        cast(fall as integer) as fall_year,
        "Academic Program Code" as program_code,
        "Dept" as dept,
        "Degr" as degree,
        "Major Code" as major_code,
        "Major Name" as major_name,
        {{ blank_to_empty('"Conc Code"') }} as conc_code,
        nullif(trim("Concentration Name (if any)"), '') as conc_name,
        {{ to_count('"FRESH MAN"') }} as freshman,
        {{ to_count('"SOPHO MORE"') }} as sophomore,
        {{ to_count('"JUNIOR"') }} as junior,
        {{ to_count('"SENIOR"') }} as senior,
        {{ to_count('"NDEG UGRAD"') }} as ndeg_ugrad,
        {{ to_count('"GRAD I (master)"') }} as grad_1,
        {{ to_count('"GRAD II (doctoral)"') }} as grad_2,
        {{ to_count('"NDEG GRAD"') }} as ndeg_grad,
        {{ to_count('"PROFES SIONAL"') }} as professional,
        {{ to_count('"TOTAL STUDENTS"') }} as total_students
    from {{ source('dmi', 'enrollment_by_curriculum') }}
)

unpivot curricula
on freshman, sophomore, junior, senior, ndeg_ugrad, grad_1, grad_2, ndeg_grad, professional
into name class_level value headcount
