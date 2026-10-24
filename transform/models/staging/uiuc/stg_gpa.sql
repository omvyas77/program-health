-- One row per section with 21 or more graded students; Students counts graded students only
-- and leaves out W.
select
    cast("Year" as integer) as year,
    "Term" as term,
    "YearTerm" as yearterm,
    "Subject" as subject,
    "Number" as number,
    "Course Title" as course_title,
    upper(nullif(trim("Sched Type"), '')) as sched_type,
    {{ to_count('"A+"') }} as a_plus,
    {{ to_count('"A"') }} as a,
    {{ to_count('"A-"') }} as a_minus,
    {{ to_count('"B+"') }} as b_plus,
    {{ to_count('"B"') }} as b,
    {{ to_count('"B-"') }} as b_minus,
    {{ to_count('"C+"') }} as c_plus,
    {{ to_count('"C"') }} as c,
    {{ to_count('"C-"') }} as c_minus,
    {{ to_count('"D+"') }} as d_plus,
    {{ to_count('"D"') }} as d,
    {{ to_count('"D-"') }} as d_minus,
    {{ to_count('"F"') }} as f,
    {{ to_count('"W"') }} as w,
    {{ to_count('"Students"') }} as students
from {{ source('uiuc', 'gpa') }}
