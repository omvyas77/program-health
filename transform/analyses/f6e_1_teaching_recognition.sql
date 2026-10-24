-- 6e.1 Teachers Ranked as Excellent listings per 100 primary sections, by Gies subject and long term, Fall 2016 to Spring 2025
-- TRE lists by unit: Accountancy is ACCY, Business Administration BADM, Finance FIN, Business
-- BUS, Business Data and Innovation BDI, and the MBA units MBA. Business and Technical Writing
-- belongs to English and is left out. Unit names switch to mixed case in 2024-sp, so they are
-- matched without case. Counts only: names never leave data/raw. BUS has more TA listings than
-- primary sections in Falls 2017 to 2019, so its TA rate passes 100; it does against every
-- section type too, so the listings outnumber the sections rather than the denominator being
-- too narrow.
{%- set subjects = ['ACCY', 'BADM', 'BDI', 'BUS', 'FIN', 'MBA'] %}
with listings as (
    select
        yearterm,
        case upper(unit)
            when 'ACCOUNTANCY' then 'ACCY'
            when 'BUSINESS ADMINISTRATION' then 'BADM'
            when 'FINANCE' then 'FIN'
            when 'BUSINESS' then 'BUS'
            when 'BUSINESS DATA AND INNOVATION' then 'BDI'
            when 'MBA' then 'MBA'
            when 'MBA PROGRAM' then 'MBA'
            when 'MASTERS OF BUSINESS ADMINISTRATION' then 'MBA'
        end as subject,
        role,
        listings
    from {{ ref('stg_tre') }}
),

sections as (
    select c.yearterm, c.year, c.term, c.subject, count(distinct c.crn) as sections
    from {{ ref('stg_catalog') }} as c
    inner join {{ ref('int_type_codes') }} as t on t.type_code = c.type_code
    where t.is_primary and c.term in ('Fall', 'Spring')
    group by c.yearterm, c.year, c.term, c.subject
),

by_role as (
    select s.yearterm, s.year, s.term, s.subject, r.role, s.sections,
        coalesce(sum(l.listings), 0) as listings
    from sections as s
    cross join (values ('Instructor'), ('TA')) as r (role)
    left join listings as l
        on l.yearterm = s.yearterm and l.subject = s.subject and l.role = r.role
    where s.yearterm in (select distinct yearterm from {{ ref('stg_tre') }})
    group by s.yearterm, s.year, s.term, s.subject, r.role, s.sections
)

select
    role as "Role",
    yearterm as "Term",
    {%- for s in subjects %}
    printf(
        '%.1f',
        100.0 * sum(listings) filter (where subject = '{{ s }}')
        / sum(sections) filter (where subject = '{{ s }}')
    ) as "{{ s }}",
    {%- endfor %}
    printf('%.1f', 100.0 * sum(listings) / sum(sections)) as "All Gies"
from by_role
group by role, yearterm, year, term
order by role, {{ term_order('year', 'term') }}
