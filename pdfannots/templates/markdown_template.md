# {{title}}

> The author : {{author}}

{# This is a comment :

{{ }} it's used to print
{% %} it's used to add instruction (for, if, ...)

#}

{# test if the PDF contains at least ONE highlight to print the template #}
{% if highlights|length > 0 %}

## Notes

{# 
  Use namespace to assign (update) the same variable in the loop 
  if you don't using namespace , example :
  set x = highlights[0].page_string|trim|int
  and you assign the same variable in the loop , the value of the var won't change
#}

{# x contain  the number of the firs page in (int) #}
{# in simple mode : x.foo =  highlights[0].page_string|trim|int #}
{% set x = namespace(foo=highlights[0].page_string|trim|int)  %}

{# print the first page number if the page_string is not None #}
{{ highlights[0].page_string + ": " if highlights[0].page_string != None}}


{% for h in highlights%}

{#  test if the highlight have the same page number as the last highlights printed to avoid 
case of printing the same page  number each time , example :
page 1 : hg..
page 1 : hg..
#}
{{ h.page_string + ": " if h.page_string|trim|int !=  x.foo and h.page_string != None }}

{#  for testing if The page number is printed correctly
{{"page number= " + h.page_string +", x= " + x.foo|string + "\n"}} 
{{"set x = " + h.page_string|trim }} 
#}

{# update the variable x.foo #}
{% set x.foo = h.page_string|trim|int %}

{% if h.colorname=="blue" %}

{{ h.text|trim }}
{% elif h.colorname=="lilac" %}

{{ h.text|trim }}
{% elif h.colorname=="green" %}

{{ h.text|trim }}
{% elif h.colorname=="yellow" %}

{{ h.text|trim }}
{% else %}

{{ h.text }}
{% endif %}
{% endfor %}
{% endif %}

{% if comments|length > 0 %}

## Comments

{% for h in comments %}

- {{ h.page_string + ": " if h.page_string != None }}
  > {{ h.text|trim }} > {{ h.contents }} > {% endfor %} > {% endif %}

{% if editing|length > 0 %}

## Editing

{% for h in editing %}
{% if h.subtype == "strikeout" %}
{% set editing_formatter = "~~" %}
{% elif h.subtype == "underline" %}
{% set editing_formatter = "_" %}
{% elif h.subtype == "squiggly" %}
{% set editing_formatter = "*" %}
{% endif %}

- {{ editing_formatter }}{{ h.text|trim }}{{ editing_formatter }} -> {{ h.contents|trim + ": " if h.contents != None }}
  {% endfor %}
  {% endif %}
