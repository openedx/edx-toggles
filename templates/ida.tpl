Feature toggles configured for {{ ida.name }}:
--------------------------------{% for _ in ida.name %}-{% endfor %}

Summary:
~~~~~~~~

* Total Waffle Flags in {{ ida.name }}: {{ ida.toggles['waffle.flag'] |length }}
* Total Waffle Switches in {{ ida.name }}: {{ ida.toggles['waffle.switch'] |length }}

{% if ida.toggles['waffle.flag']  %}

**Waffle Flags**:

    {% for flag in ida.toggles['waffle.flag'] %}
        {% include 'flag.tpl' %}

    {% endfor %}

{% endif %}




{% if ida.toggles['waffle.switch']  %}

**Waffle Switches**:

    {% for switch in ida.toggles['waffle.switch'] %}
        {% include 'switch.tpl' %}

    {% endfor %}

{% endif %}
