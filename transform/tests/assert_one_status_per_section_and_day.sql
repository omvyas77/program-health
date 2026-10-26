-- The course-page pass records each CRN once a day.
select snapshot_date, crn, count(*) as n
from {{ ref('stg_cis__status') }}
group by snapshot_date, crn
having count(*) > 1
