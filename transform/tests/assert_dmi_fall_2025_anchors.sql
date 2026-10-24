-- Fall 2025 numbers checked against DMI's published reports.
with enrollment as (
    select
        sum(headcount) as total,
        sum(headcount) filter (where level = 'undergraduate') as undergraduate,
        sum(headcount) filter (where level = 'graduate') as graduate,
        sum(headcount) filter (where program_family = 'MBA') as mba,
        sum(headcount) filter (where program_family = 'Business Undeclared') as undeclared
    from {{ ref('mart_gies_enrollment') }}
    where fall_year = 2025
),

new_students as (
    select
        max(headcount) filter (where student_type = 'first_time_freshman') as freshmen,
        max(freshman) filter (where student_type = 'first_time_freshman') as freshmen_fr,
        max(sophomore) filter (where student_type = 'first_time_freshman') as freshmen_so,
        max(junior) filter (where student_type = 'first_time_freshman') as freshmen_jr,
        max(senior) filter (where student_type = 'first_time_freshman') as freshmen_sr,
        max(headcount) filter (where student_type = 'new_transfer') as transfers
    from {{ ref('mart_gies_new_students') }}
    where fall_year = 2025
)

select *
from enrollment, new_students
-- coalesce: a missing value must fail the test, not slip through as null.
where not coalesce(
    total = 9640 and undergraduate = 3329 and graduate = 6311 and mba = 3572 and undeclared = 1030
    and freshmen = 787 and freshmen_fr = 442 and freshmen_so = 312 and freshmen_jr = 31
    and freshmen_sr = 2 and transfers = 84,
    false
)
