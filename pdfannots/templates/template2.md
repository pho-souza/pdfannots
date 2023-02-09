# {{title}}

{% macro color_type(color) %}
{%- if color == "Green" %}


> [!question]
{%- elif color == 'Orange' %}


> [!example]
{%- elif color == 'Red' %}


> [!atencao]
{%- endif -%}
{% endmacro %}

{% set anterior = namespace('') %}
{% set anterior.contents = anotacoes[0].contents %}
{%- for anotacao  in anotacoes %}
{% if anotacao.type == 'Square' %}

{% if anotacao.has_img %}
![[{{anotacao.img_path}}]]
{% endif %}
{% elif anotacao.color_name == 'Cyan' %}

{% if anotacao.contents == "#h1" or anotacao.contents == "#H1" or  anotacao.contents == "H1"%}
# {{anotacao.text}}

{% elif anotacao.contents == "#h2" or anotacao.contents == "#H2" or  anotacao.contents == "H2" %}
## {{anotacao.text}}

{% elif anotacao.contents == "#h2" or anotacao.contents == "#H2" or  anotacao.contents == "H2" %}
### {{anotacao.text}}

{% else %}
# {{anotacao.text}}

{% endif %}
{% elif anotacao.color_name == 'Yellow' %}
{% if anotacao.contents == '-' %}
{{"- " ~ anotacao.text ~ "\n" }}

{%- elif anotacao.contents == '+' and anterior.contents == '+' -%}
{{- " " ~ anotacao.text ~ " " -}}
{%- elif anterior.contents == '+' -%}
{% if anotacao.contents and anotacao.contents != "+" %}
{{- "> " ~ anotacao.text}}
{{"> - " ~ anotacao.contents}}
{% else %}
{{- " " ~ anotacao.text}}
{% endif %}
{% elif anotacao.contents == '+' -%}

{{anotacao.text}} 
{%- elif anotacao.contents %}

{{anotacao.text}}
> {{anotacao.contents}}

{% else %}

{{anotacao.text}}

{% endif %}
{# Casos de callout #}
{% else %}
{%- if anotacao.contents == '+' and anterior.contents == '+' -%}
{{- " " ~ anotacao.text ~ " " -}}
{%- elif anterior.contents == '+' -%}
{% if anotacao.contents and anotacao.contents != "+" %}
{{- " " ~ anotacao.text}}
> - - -
{{"> - " ~ anotacao.contents}}
{% else %}
{{- " " ~ anotacao.text}}
{% endif %}
{% elif anotacao.contents == '+' -%}
{{color_type(anotacao.color_name)}}
> {{anotacao.text}} 

{%- elif anotacao.contents %}
{{color_type(anotacao.color_name)}}
> {{anotacao.text}}
> - - -
> {{anotacao.contents}}

{% else %}
{{color_type(anotacao.color_name)}}
> {{anotacao.text}}


{% endif %}
{% endif %}
{%- if anotacao.contents %}
{%- set anterior.contents = anotacao.contents -%}
{%- else -%}
{%- set anterior.contents = '' -%}
{% endif -%}
{% endfor -%}