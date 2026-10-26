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

{#- True once a file matches the pattern. DuckDB fails on a read over an empty glob, so a model
    over files that don't exist yet checks first. -#}
{% macro files_exist(pattern) %}
    {% if execute %}
        {% set result = run_query("select count(*) from glob('" ~ pattern ~ "')") %}
        {{ return(result.columns[0].values()[0] > 0) }}
    {% endif %}
    {{ return(false) }}
{% endmacro %}
