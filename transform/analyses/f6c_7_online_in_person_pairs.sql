-- 6c.7 Online and in-person sections of the same Gies undergraduate course in the same long term, Fall 2018 on
-- Online and in-person sections often serve different students, so a gap here describes the
-- sections, not the format.
-- Schedule type is blank on every row from 2016-fa to 2018-sp.
with modes as (
    select
        yearterm,
        year,
        term,
        subject,
        number,
        sum(students_graded) filter (where mode = 'in_person') as ip_graded,
        sum(grade_points) filter (where mode = 'in_person') as ip_points,
        sum(a_range) filter (where mode = 'in_person') as ip_a_range,
        sum(dfw) filter (where mode = 'in_person') as ip_dfw,
        sum(w) filter (where mode = 'in_person') as ip_w,
        sum(students_graded) filter (where mode = 'online') as ol_graded,
        sum(grade_points) filter (where mode = 'online') as ol_points,
        sum(a_range) filter (where mode = 'online') as ol_a_range,
        sum(dfw) filter (where mode = 'online') as ol_dfw,
        sum(w) filter (where mode = 'online') as ol_w
    from {{ ref('int_course_terms') }}
    where is_gies and is_undergraduate and term in ('Fall', 'Spring')
        and {{ term_order('year', 'term') }} >= {{ term_order(2018, "'Fall'") }}
    group by yearterm, year, term, subject, number
)

select
    m.yearterm as "Term",
    coalesce(f.term_flag, '') as "Flag",
    m.subject || ' ' || m.number as "Course",
    {{ fmt_int('ip_graded') }} as "In-person graded",
    {{ fmt_int('ol_graded') }} as "Online graded",
    {{ fmt_gpa('ip_points / ip_graded') }} as "In-person GPA",
    {{ fmt_gpa('ol_points / ol_graded') }} as "Online GPA",
    {{ fmt_pct('ip_a_range / ip_graded') }} as "In-person A-range",
    {{ fmt_pct('ol_a_range / ol_graded') }} as "Online A-range",
    {{ fmt_pct('ip_dfw / (ip_graded + ip_w)') }} as "In-person DFW",
    {{ fmt_pct('ol_dfw / (ol_graded + ol_w)') }} as "Online DFW"
from modes as m
left join {{ ref('stg_config__term_flags') }} as f on f.yearterm = m.yearterm
where ip_graded > 0 and ol_graded > 0
order by {{ term_order('m.year', 'm.term') }}, m.subject, m.number
