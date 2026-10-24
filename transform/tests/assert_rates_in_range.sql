-- Rate metrics are fractions between 0 and 1; the Pell gap is a difference between -1 and 1.
select unitid, metric, data_year, value
from {{ ref('mart_peer_metrics') }}
where (metric = 'pell_gap_6yr' and value not between -1 and 1)
    or (
        metric not in (
            'pell_gap_6yr', 'applicants', 'business_bachelors', 'business_masters',
            'business_bachelors_incl_307102', 'business_masters_incl_307102'
        )
        and value not between 0 and 1
    )
