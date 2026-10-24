{# Source extracts keep every column as text, with blanks, padding ("05", " 2"), and
   thousands separators as published. These cast them, and return null for blanks. #}

{% macro to_count(column) -%}
    try_cast(nullif(replace(trim({{ column }}), ',', ''), '') as bigint)
{%- endmacro %}

{% macro to_code(column) -%}
    try_cast(nullif(trim({{ column }}), '') as integer)
{%- endmacro %}

{% macro blank_to_empty(column) -%}
    coalesce(trim({{ column }}), '')
{%- endmacro %}
