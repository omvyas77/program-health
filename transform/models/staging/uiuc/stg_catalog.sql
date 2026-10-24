-- Gies sections offered, one row per catalog line (a section with several meetings has
-- several lines).
select
    "YearTerm" as yearterm,
    cast("Year" as integer) as year,
    "Term" as term,
    "Subject" as subject,
    "Number" as number,
    "Name" as course_name,
    "CRN" as crn,
    "Section" as section,
    nullif(trim("Type"), '') as type_label,
    upper(nullif(trim("Type Code"), '')) as type_code,
    "Part of Term" as part_of_term,
    "Section Status" as section_status,
    "Enrollment Status" as enrollment_status,
    "Credit Hours" as credit_hours
from {{ source('uiuc', 'catalog') }}
