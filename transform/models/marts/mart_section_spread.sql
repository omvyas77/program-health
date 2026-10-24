-- How much sections of the same course differ in GPA, for course-terms with three or more
-- sections. No instructor or section identifiers are carried.
with sections as (
    select
        g.yearterm,
        g.subject,
        g.number,
        g.students,
        (4.0 * (g.a_plus + g.a) + 3.67 * g.a_minus + 3.33 * g.b_plus + 3.0 * g.b + 2.67 * g.b_minus
        + 2.33 * g.c_plus + 2.0 * g.c + 1.67 * g.c_minus + 1.33 * g.d_plus + 1.0 * g.d
        + 0.67 * g.d_minus) / g.students as gpa
    from {{ ref('stg_gpa') }} as g
    inner join {{ ref('stg_config__gies_subjects') }} as s on s.subject = g.subject
)

select
    yearterm,
    subject,
    number,
    cast(count(*) as bigint) as n_sections,
    cast(sum(students) as bigint) as students_graded,
    cast(min(gpa) as double) as gpa_min,
    cast(max(gpa) as double) as gpa_max,
    cast(stddev_samp(gpa) as double) as gpa_sd
from sections
group by yearterm, subject, number
having count(*) >= 3
