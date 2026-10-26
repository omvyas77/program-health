{{ config(severity = 'warn') }}
-- Course-page CRNs that the same morning's API snapshot doesn't list. Sections can change between
-- the two reads, so this warns and lists them rather than failing.
select s.snapshot_date, s.crn, s.status
from {{ ref('stg_cis__status') }} as s
left join {{ ref('stg_cis__snapshots') }} as a
    on a.snapshot_date = s.snapshot_date and a.crn = s.crn
where a.crn is null
