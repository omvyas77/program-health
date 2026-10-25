-- The four grade bands account for every graded student in each course-term.
select yearterm, subject, number, mode
from {{ ref('mart_course_terms') }}
where grade_a + grade_b + grade_c + grade_d_f != students_graded
