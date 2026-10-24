-- Schedule type codes and their labels from the catalog. A section is online when its label
-- starts with "Online"; primary types are the ones a section count should include.
with labels as (
    select type_code, type_label, count(*) as lines
    from {{ ref('stg_catalog') }}
    where type_code is not null and type_label is not null
    group by type_code, type_label
)

select
    type_code,
    arg_max(type_label, lines) as type_label,
    count(*) as distinct_labels,
    starts_with(arg_max(type_label, lines), 'Online') as is_online,
    arg_max(type_label, lines) in (
        'Lecture',
        'Lecture-Discussion',
        'Online',
        'Online Lecture',
        'Online Lecture Discussion',
        'Seminar'
    ) as is_primary
from labels
group by type_code
