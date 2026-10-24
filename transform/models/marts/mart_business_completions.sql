-- Completions in business CIP codes, plus each school's all-fields total (CIP 99) so shares
-- can be computed. Award level labels are the IPEDS dictionary's, in C2024_A's wording; code 1
-- is C2019_A's, retired when C2020_A split it into 20 and 21.
with business as (
    select cipcode, is_optional from {{ ref('stg_config__cip_business') }}
),

kept as (
    select c.*, b.cipcode is not null as is_listed, coalesce(b.is_optional, false) as is_optional
    from {{ ref('stg_ipeds__c_a') }} as c
    left join business as b on b.cipcode = c.cipcode
    where b.cipcode is not null or c.cipcode = '99'
)

select
    k.unitid,
    p.school,
    p.is_illinois,
    p.control,
    k.academic_year,
    k.data_year as award_year_end,
    k.award_level,
    case k.award_level
        when 1 then 'Award of less than 1 academic year'
        when 2 then 'Certificates of at least 1 but less than 2 years'
        when 3 then 'Associate''s degree'
        when 4 then 'Certificates of at least 2 but less than 4 years'
        when 5 then 'Bachelor''s degree'
        when 6 then 'Postbaccalaureate certificate'
        when 7 then 'Master''s degree'
        when 8 then 'Post-master''s certificate'
        when 17 then 'Doctor''s degree - research/scholarship'
        when 18 then 'Doctor''s degree - professional practice'
        when 19 then 'Doctor''s degree - other'
        when 20 then 'Certificates of less than 12 weeks'
        when 21 then 'Certificates of at least 12 weeks but less than 1 year'
    end as award_level_label,
    k.cipcode,
    k.is_listed and not k.is_optional as is_business,
    k.is_optional as is_optional_business,
    cast(coalesce(sum(k.completions) filter (where k.majornum = 1), 0) as bigint)
        as completions_first_major,
    cast(coalesce(sum(k.completions) filter (where k.majornum = 2), 0) as bigint)
        as completions_second_major,
    bool_or(k.is_provisional) as is_provisional,
    any_value(k.source_file) as source_file
from kept as k
inner join {{ ref('stg_config__peers') }} as p on p.unitid = k.unitid
group by
    k.unitid, p.school, p.is_illinois, p.control, k.academic_year, k.data_year,
    k.award_level, k.cipcode, k.is_listed, k.is_optional
