-- UW-Madison's education degrees and all-fields bachelor's, as read from C2015_A and C2025_A
-- (first majors). Pinned so a change to the staging logic or a re-release of either file fails
-- the build instead of quietly moving the addendum's numbers.
with wisconsin as (
    select
        award_year_end,
        sum(completions) filter (where is_education and degree_level = 'Bachelor''s') as ed_ba,
        sum(completions) filter (where is_education and degree_level = 'Master''s') as ed_ma,
        sum(completions) filter (where is_education and degree_level = 'Doctoral') as ed_doc,
        sum(completions) filter (where not is_education and degree_level = 'Bachelor''s') as all_ba
    from {{ ref('mart_education_completions') }}
    where is_wisconsin and award_year_end in (2015, 2025)
    group by award_year_end
),

pinned as (
    select * from (values
        (2015, 134, 109, 55, 6854),
        (2025, 212, 164, 50, 9241)
    ) as t (award_year_end, ed_ba, ed_ma, ed_doc, all_ba)
)

select p.*, w.ed_ba as got_ba, w.ed_ma as got_ma, w.ed_doc as got_doc, w.all_ba as got_all_ba
from pinned as p
left join wisconsin as w using (award_year_end)
-- coalesce: a missing year must fail the test, not slip through as null.
where not coalesce(
    w.ed_ba = p.ed_ba and w.ed_ma = p.ed_ma and w.ed_doc = p.ed_doc and w.all_ba = p.all_ba,
    false
)
