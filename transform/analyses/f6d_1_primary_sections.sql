-- 6d.1 Primary sections offered by Gies subject and long term, Fall 2016 to Fall 2026
-- Lecture, lecture-discussion, online, online lecture, online lecture-discussion, and seminar
-- types, counted as distinct CRNs in the course catalog, so a section with two primary meeting
-- types counts once. The catalog has no files before Fall 2016.
{%- set subjects = ['ACCY', 'BADM', 'BDI', 'BUS', 'FIN', 'MBA'] %}
with primary_sections as (
    select distinct c.yearterm, c.year, c.term, c.subject, c.crn
    from {{ ref('stg_catalog') }} as c
    inner join {{ ref('int_type_codes') }} as t on t.type_code = c.type_code
    where t.is_primary and c.term in ('Fall', 'Spring')
)

select
    yearterm as "Term",
    {%- for s in subjects %}
    count(distinct crn) filter (where subject = '{{ s }}') as "{{ s }}",
    {%- endfor %}
    count(distinct crn) as "All Gies"
from primary_sections
group by yearterm, year, term
order by {{ term_order('year', 'term') }}
