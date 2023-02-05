# {{title}}

{% for anotacao  in anotacoes %}
{% if anotacao.color_name == 'Yellow' %}
{% if anotacao.text == '-' %}
- {{anotacao.text}}
{% elif anotacao.text == '+' %}
{{anotacao.text}}
{% else %}
{{anotacao.text}}
{% endif %}
{% if anotacao.contents %}
- {{anotacao.contents}}
{% endif %}
{% elif anotacao.color_name == 'Red' %}
{% endif %}
{% endfor %}