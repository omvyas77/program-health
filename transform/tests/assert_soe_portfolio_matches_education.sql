-- The portfolio's Education group and the peer mart's UW-Madison education rows come from the
-- same staging rows by different paths; they must agree for every award year and degree level.
with portfolio as (
    select academic_year, degree_level, sum(completions) as n
    from {{ ref('mart_soe_portfolio') }}
    where field_group = 'Education'
    group by all
),

peers as (
    select academic_year, degree_level, sum(completions) as n
    from {{ ref('mart_education_completions') }}
    where is_wisconsin and is_education
    group by all
)

select *
from portfolio
full outer join peers using (academic_year, degree_level)
where portfolio.n is distinct from peers.n
