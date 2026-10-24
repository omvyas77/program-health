-- Gies headcount by curriculum and class level: DMI's reports through Fall 2025, DAIR's
-- dashboard for Fall 2026. Fall 2025 appears in both and matches on every curriculum.
with dmi as (
    select fall_year, program_code, major_code, conc_code, class_level, headcount, 'dmi' as source
    from {{ ref('stg_dmi__curriculum') }}
),

dair as (
    select fall_year, program_code, major_code, conc_code, class_level, headcount, 'dair' as source
    from {{ ref('stg_dair__curriculum') }}
    where class_level is not null
        and fall_year > (select max(fall_year) from {{ ref('stg_dmi__curriculum') }})
)

select
    curricula.*,
    programs.program_family,
    programs.level,
    programs.modality
from (select * from dmi union all select * from dair) as curricula
left join {{ ref('stg_config__program_map') }} as programs
    on programs.program_code = curricula.program_code
    and programs.major_code = curricula.major_code
    and programs.conc_code = curricula.conc_code
