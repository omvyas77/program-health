{# The shared start of every IPEDS staging model: the file each row came from, rows for the
   peers' excluded files dropped (config/ipeds_exclusions.csv), and the file's release status. #}
{% macro ipeds_rows(family) %}
    with source as (
        select
            *,
            regexp_extract(filename, '([A-Z0-9_]+)\.parquet$', 1) as source_file,
            cast(trim(UNITID) as integer) as unit_id
        from {{ source('ipeds', family) }}
    ),

    kept as (
        select source.*
        from source
        anti join {{ ref('stg_config__ipeds_exclusions') }} as excluded
            on excluded.unitid = source.unit_id and excluded.file = source.source_file
    ),

    rows as (
        select
            kept.*,
            status.file_year,
            status.is_provisional
        from kept
        inner join {{ ref('stg_config__ipeds_file_status') }} as status
            on status.file = kept.source_file
    )
{% endmacro %}
