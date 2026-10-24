-- Primary sections per course in each daily snapshot, with the sections added and removed
-- since the previous snapshot and since registration opened. The Course Explorer API carries
-- no enrollment status, so this tracks the schedule's response to demand, not seats.
with section_types as (
    select snapshot_date, term, subject, number, crn, unnest(string_split(type_code, ';')) as code
    from {{ ref('stg_cis__snapshots') }}
),

primary_sections as (
    select distinct s.snapshot_date, s.term, s.subject, s.number, s.crn
    from section_types as s
    inner join {{ ref('int_type_codes') }} as t on t.type_code = s.code
    where t.is_primary
),

dates as (
    select
        d.snapshot_date,
        d.term,
        lag(d.snapshot_date) over (partition by d.term order by d.snapshot_date) as previous_date,
        r.first_registration_date
    from (select distinct snapshot_date, term from primary_sections) as d
    inner join {{ ref('stg_config__registration') }} as r on r.term = d.term
),

baselines as (
    -- The last snapshot on or before the first day of registration.
    select term, max(snapshot_date) as baseline_date
    from dates
    where snapshot_date <= first_registration_date
    group by term
),

courses as (
    select distinct d.snapshot_date, d.term, d.previous_date, d.first_registration_date,
        b.baseline_date, p.subject, p.number
    from dates as d
    left join baselines as b on b.term = d.term
    inner join primary_sections as p
        on p.term = d.term and p.snapshot_date in (d.snapshot_date, d.previous_date)
)

select
    c.snapshot_date,
    cast(c.snapshot_date - c.first_registration_date as integer) as days_since_registration_open,
    c.subject,
    c.number,
    cast(count(distinct now.crn) as bigint) as primary_sections,
    -- The first snapshot has nothing before it, so both of its since-previous counts are null.
    cast(
        case
            when c.previous_date is not null
                then count(distinct now.crn) filter (where before.crn is null)
        end as bigint
    ) as sections_added_since_previous,
    cast(case when c.previous_date is not null then (
        select count(*)
        from primary_sections as p
        where p.snapshot_date = c.previous_date and p.subject = c.subject and p.number = c.number
            and p.crn not in (
                select crn from primary_sections as q
                where q.snapshot_date = c.snapshot_date and q.subject = c.subject
                    and q.number = c.number
            )
    ) end as bigint) as sections_removed_since_previous,
    cast(
        case
            when c.snapshot_date > c.baseline_date
                then count(distinct now.crn) filter (where baseline.crn is null)
        end as bigint
    ) as sections_added_since_open
from courses as c
left join primary_sections as now
    on now.snapshot_date = c.snapshot_date and now.subject = c.subject and now.number = c.number
left join primary_sections as before
    on before.snapshot_date = c.previous_date and before.crn = now.crn
left join primary_sections as baseline
    on baseline.snapshot_date = c.baseline_date and baseline.crn = now.crn
group by
    c.snapshot_date, c.first_registration_date, c.previous_date, c.baseline_date, c.subject,
    c.number
