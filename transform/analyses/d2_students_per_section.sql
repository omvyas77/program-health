-- D2 Graded students per primary section by Gies subject and long term, Fall 2016 to Fall 2025
-- Graded students from the GPA dataset over primary sections from the catalog, for course-terms
-- with both. The GPA data leaves out sections of 20 or fewer graded students, so the figure runs
-- a little low. The GPA data's own section count isn't used: where grades were recorded moved from
-- discussions to lectures over these years (docs/data_notes.md).
{%- set subjects = ['ACCY', 'BADM', 'BDI', 'BUS', 'FIN', 'MBA'] %}
with both_counts as (
    select *
    from {{ ref('mart_course_sections') }}
    where term in ('Fall', 'Spring') and primary_sections > 0 and students_graded > 0
)

select
    yearterm as "Term",
    {%- for s in subjects %}
    printf(
        '%.1f',
        sum(students_graded) filter (where subject = '{{ s }}')
        / sum(primary_sections) filter (where subject = '{{ s }}')
    ) as "{{ s }}",
    {%- endfor %}
    printf('%.1f', sum(students_graded) / sum(primary_sections)) as "All Gies"
from both_counts
group by yearterm, year, term
order by {{ term_order('year', 'term') }}
