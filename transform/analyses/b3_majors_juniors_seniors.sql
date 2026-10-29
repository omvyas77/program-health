-- B3 Gies undergraduate majors measured by junior and senior headcount, Fall 2017 to Fall 2026
-- Most first- and second-year students sit in Business Undeclared, so juniors and seniors show
-- where students land. Nondegree students have no class level and are left out.
with majors as (
    select program_family, fall_year, sum(juniors_seniors) as juniors_seniors
    from {{ ref('mart_gies_enrollment') }}
    where level = 'undergraduate' and program_family != 'Nondegree'
        and fall_year between 2017 and 2026
    group by program_family, fall_year
),

all_rows as (
    select * from majors
    union all
    select 'All undergraduate', fall_year, sum(juniors_seniors) from majors group by fall_year
)

select
    program_family as "Program family",
    {%- for y in range(2017, 2027) %}
    {{ fmt_int('sum(juniors_seniors) filter (where fall_year = ' ~ y ~ ')') }} as "Fall {{ y }}",
    {%- endfor %}
    {{ fmt_change('sum(juniors_seniors) filter (where fall_year = 2026) - sum(juniors_seniors) filter (where fall_year = 2021)') }}
        as "Change, Fall 2021 to Fall 2026"
from all_rows
group by program_family
order by program_family = 'All undergraduate', program_family
