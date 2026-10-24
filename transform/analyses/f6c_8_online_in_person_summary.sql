-- 6c.8 Online minus in-person, across the course-term pairs in 6c.7
-- Medians of the paired differences, so one large course does not set the result.
with modes as (
    select
        yearterm,
        subject,
        number,
        sum(grade_points) filter (where mode = 'in_person')
        / sum(students_graded) filter (where mode = 'in_person') as ip_gpa,
        sum(a_range) filter (where mode = 'in_person')
        / sum(students_graded) filter (where mode = 'in_person') as ip_a_range,
        sum(dfw) filter (where mode = 'in_person')
        / sum(students_graded + w) filter (where mode = 'in_person') as ip_dfw,
        sum(grade_points) filter (where mode = 'online')
        / sum(students_graded) filter (where mode = 'online') as ol_gpa,
        sum(a_range) filter (where mode = 'online')
        / sum(students_graded) filter (where mode = 'online') as ol_a_range,
        sum(dfw) filter (where mode = 'online')
        / sum(students_graded + w) filter (where mode = 'online') as ol_dfw
    from {{ ref('int_course_terms') }}
    where is_gies and is_undergraduate and term in ('Fall', 'Spring')
        and {{ term_order('year', 'term') }} >= {{ term_order(2018, "'Fall'") }}
    group by yearterm, year, term, subject, number
),

pairs as (
    select
        m.*,
        case when f.term_flag = 'covid_grading' then 'covid_grading terms' else 'Other terms' end
            as term_group
    from modes as m
    left join {{ ref('stg_config__term_flags') }} as f on f.yearterm = m.yearterm
    where m.ip_gpa is not null and m.ol_gpa is not null
)

select
    term_group as "Terms",
    count(*) as "Course-terms",
    count(distinct subject || number) as "Courses",
    count(*) filter (where ol_a_range > ip_a_range) as "Online A-range higher",
    printf('%+.2f', median(ol_gpa - ip_gpa)) as "Median GPA difference",
    {{ fmt_pts('median(ol_a_range - ip_a_range)') }} as "Median A-range difference",
    {{ fmt_pts('median(ol_dfw - ip_dfw)') }} as "Median DFW difference"
from pairs
group by term_group
order by term_group desc
