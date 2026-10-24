-- Gies headcount by fall, program family, level, and modality. Majors are measured by junior
-- and senior headcount, since most first- and second-year students are Business Undeclared.
select
    fall_year,
    'Fall ' || fall_year as fall_term,
    program_family,
    level,
    modality,
    cast(sum(headcount) as bigint) as headcount,
    cast(
        case
            when level = 'undergraduate'
                then coalesce(sum(headcount) filter (where class_level in ('junior', 'senior')), 0)
        end as bigint
    ) as juniors_seniors,
    source
from {{ ref('int_gies_enrollment') }}
group by fall_year, program_family, level, modality, source
