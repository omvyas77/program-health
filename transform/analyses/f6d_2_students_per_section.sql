-- 6d.2 Graded students per section by Gies subject and long term, Fall 2016 to Fall 2025
-- Both counts come from the GPA dataset, which holds only sections with 21 or more graded
-- students, so this is the average size of those sections.
{%- set subjects = ['ACCY', 'BADM', 'BDI', 'BUS', 'FIN', 'MBA'] %}
select
    yearterm as "Term",
    {%- for s in subjects %}
    printf(
        '%.1f',
        sum(students_graded) filter (where subject = '{{ s }}')
        / sum(graded_sections) filter (where subject = '{{ s }}')
    ) as "{{ s }}",
    {%- endfor %}
    printf('%.1f', sum(students_graded) / sum(graded_sections)) as "All Gies"
from {{ ref('int_course_terms') }}
where is_gies and term in ('Fall', 'Spring')
    and {{ term_order('year', 'term') }} >= {{ term_order(2016, "'Fall'") }}
group by yearterm, year, term
order by {{ term_order('year', 'term') }}
