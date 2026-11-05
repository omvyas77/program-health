-- Education degrees (CIP 13) at the 18 Big Ten schools, by school, award year, degree level, and
-- four-digit CIP series, plus each school's all-fields total (series '99') so shares can be
-- computed. Degrees only: bachelor's (AWLEVEL 5), master's (7), and doctoral (17, 18, 19);
-- certificates are left out. First majors only, so each degree is counted once.
with degrees as (
    select
        unitid,
        academic_year,
        data_year,
        is_provisional,
        source_file,
        case when cipcode = '99' then '99' else left(cipcode, 5) end as series,
        case
            when award_level = 5 then 'Bachelor''s'
            when award_level = 7 then 'Master''s'
            else 'Doctoral'
        end as degree_level,
        completions
    from {{ ref('stg_ipeds__c_a') }}
    where
        majornum = 1
        and award_level in (5, 7, 17, 18, 19)
        and (cipcode like '13.%' or cipcode = '99')
)

select
    d.unitid,
    p.school,
    d.unitid = {{ var('soe_unitid') }} as is_wisconsin,
    d.academic_year,
    d.data_year as award_year_end,
    d.degree_level,
    d.series,
    case when d.series = '99' then 'All fields' else s.label end as series_label,
    d.series <> '99' as is_education,
    coalesce(s.is_teacher_prep, false) as is_teacher_prep,
    cast(sum(d.completions) as bigint) as completions,
    bool_or(d.is_provisional) as is_provisional,
    any_value(d.source_file) as source_file
from degrees as d
inner join {{ ref('stg_config__peers') }} as p on p.unitid = d.unitid
left join {{ ref('stg_config__cip_education_series') }} as s on s.series = d.series
group by all
