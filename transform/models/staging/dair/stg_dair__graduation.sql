-- Graduates by year after entry (not cumulative), by college of entry. The export uses the
-- label "Size of Adjusted Cohort" twice: with two trailing spaces it is the cohort size, and
-- without them it repeats the graduate count, so labels are matched exactly, untrimmed.
select
    "College At Entry" as entry_college,
    cast(regexp_extract("Fall Cohort", '([0-9]{4})', 1) as integer) as cohort_year,
    cast(regexp_extract("Graduation Year Group", '([0-9])-Year', 1) as integer) as years_after_entry,
    case "Measure"
        when 'Size of Adjusted Cohort  ' then 'adjusted_cohort'
        when 'Graduate Count ' then 'graduates'
    end as measure,
    {{ to_count('"Value"') }} as value
from {{ source('dair', 'graduation_by_entry_college') }}
where "Measure" in ('Size of Adjusted Cohort  ', 'Graduate Count ')
