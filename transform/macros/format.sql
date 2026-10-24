{#- Formatting for docs/findings.md, done in SQL so each table is exactly what its query returns. -#}
{% macro fmt_pct(x) %}printf('%.1f%%', 100 * ({{ x }})){% endmacro %}

{% macro fmt_pts(x) %}printf('%+.1f pts', 100 * ({{ x }})){% endmacro %}

{% macro fmt_int(x) %}printf('%,d', cast(round({{ x }}) as bigint)){% endmacro %}

{% macro fmt_change(x) %}printf('%+,d', cast(round({{ x }}) as bigint)){% endmacro %}

{% macro fmt_gpa(x) %}printf('%.2f', {{ x }}){% endmacro %}

{#- Fall and spring only; summer and winter terms are small and stay out of trends. -#}
{% macro term_order(year, term) %}({{ year }} * 10 + case {{ term }} when 'Spring' then 1 when 'Summer' then 2 when 'Fall' then 3 else 0 end){% endmacro %}
