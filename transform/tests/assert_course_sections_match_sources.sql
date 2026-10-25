-- mart_course_sections keeps every primary section and every graded student: its totals equal
-- the catalog's distinct primary CRNs per course-term and the GPA dataset's Gies students.
with mart as (
    select sum(primary_sections) as primary_sections, sum(students_graded) as students_graded
    from {{ ref('mart_course_sections') }}
),

catalog as (
    select count(*) as primary_sections
    from (
        select distinct c.yearterm, c.subject, c.number, c.crn
        from {{ ref('stg_catalog') }} as c
        inner join {{ ref('int_type_codes') }} as t on t.type_code = c.type_code
        where t.is_primary
    )
),

gpa as (
    select sum(students_graded) as students_graded
    from {{ ref('int_course_terms') }}
    where is_gies
)

select *
from mart, catalog, gpa
where mart.primary_sections is distinct from catalog.primary_sections
    or mart.students_graded is distinct from gpa.students_graded
