-- Course-terms from the GPA dataset for every subject, split by mode, with the grade counts kept
-- so group rates can be summed from counts. GPA is on the 4.0 scale with A+ = 4.0. Mode is
-- unknown when the section has no schedule type or one the catalog never defines (Q, once, in
-- 2010-sp).
with sections as (
    select
        g.*,
        s.subject is not null as is_gies,
        case
            when t.type_code is null then 'unknown'
            when t.is_online then 'online'
            else 'in_person'
        end as mode
    from {{ ref('stg_gpa') }} as g
    left join {{ ref('stg_config__gies_subjects') }} as s on s.subject = g.subject
    left join {{ ref('int_type_codes') }} as t on t.type_code = g.sched_type
),

grade_counts as (
    select
        *,
        4.0 * (a_plus + a) + 3.67 * a_minus + 3.33 * b_plus + 3.0 * b + 2.67 * b_minus
        + 2.33 * c_plus + 2.0 * c + 1.67 * c_minus + 1.33 * d_plus + 1.0 * d + 0.67 * d_minus
            as points,
        a_plus + a + a_minus as a_range,
        d_plus + d + d_minus + f as d_or_f,
        c_plus + c + c_minus + d_plus + d + d_minus + f as c_or_below
    from sections
)

select
    yearterm,
    year,
    term,
    subject,
    number,
    is_gies,
    try_cast(number as integer) < 500 as is_undergraduate,
    max(course_title) as course_title,
    mode,
    count(*) as graded_sections,
    sum(students) as students_graded,
    sum(w) as w,
    sum(points) as grade_points,
    sum(a_range) as a_range,
    sum(d_or_f) + sum(w) as dfw,
    sum(c_or_below) + sum(w) as c_or_below_w,
    sum(points) / sum(students) as gpa,
    sum(a_range) / sum(students) as a_range_share,
    (sum(d_or_f) + sum(w)) / (sum(students) + sum(w)) as dfw_rate,
    (sum(c_or_below) + sum(w)) / (sum(students) + sum(w)) as c_or_below_w_rate
from grade_counts
group by yearterm, year, term, subject, number, is_gies, mode
