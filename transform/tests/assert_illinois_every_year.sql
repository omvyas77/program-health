-- Illinois must have a value for every metric and data year that any school has.
select metric, data_year
from {{ ref('mart_peer_metrics') }}
group by metric, data_year
having count(*) filter (where is_illinois) = 0
