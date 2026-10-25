-- Gies course-terms from the GPA dataset. Only sections with 21 or more graded students are in
-- the data, so graded_sections counts those. grade_a to grade_d_f count graded students by band
-- (A+ to A-, B+ to B-, C+ to C-, D+ to F) and add up to students_graded. Grades are not
-- learning outcomes.
select
    c.yearterm,
    c.year,
    c.term,
    c.subject,
    c.number,
    c.course_title,
    cast(least(floor(try_cast(c.number as integer) / 100) * 100, 500) as integer) as course_level,
    try_cast(c.number as integer) < 500 as is_undergraduate,
    c.mode,
    cast(c.graded_sections as bigint) as graded_sections,
    cast(c.students_graded as bigint) as students_graded,
    cast(c.w as bigint) as w,
    cast(c.a_range as bigint) as grade_a,
    cast(c.b_range as bigint) as grade_b,
    cast(c.c_range as bigint) as grade_c,
    cast(c.d_or_f as bigint) as grade_d_f,
    cast(c.gpa as double) as gpa,
    cast(c.a_range_share as double) as a_range_share,
    cast(c.dfw_rate as double) as dfw_rate,
    cast(c.c_or_below_w_rate as double) as c_or_below_w_rate,
    f.term_flag
from {{ ref('int_course_terms') }} as c
left join {{ ref('stg_config__term_flags') }} as f on f.yearterm = c.yearterm
where c.is_gies
