{% macro generate_schema_name(custom_schema_name, node) -%}
  {# Keep Week 1–2 objects in the explicit assignment schemas. #}
  {%- if custom_schema_name is none -%}
    {{ target.schema }}
  {%- else -%}
    {{ custom_schema_name | trim }}
  {%- endif -%}
{%- endmacro %}
