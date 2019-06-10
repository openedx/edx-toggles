Feature toggles configured for **{{ ida.name }}**:
------------------------------------{% for _ in ida.name %}-{% endfor %}

Summary:
~~~~~~~~

* Total Waffle Flags in {{ ida.name }}: {{ ida.toggle_states['waffle.flag'] |length }}
* Total Waffle Switches in {{ ida.name }}: {{ ida.toggle_states['waffle.switch'] |length }}

{% if ida.toggle_states['waffle.flag']  %}

**Waffle Flags**:

    {% for flag in ida.toggle_states['waffle.flag'] %}
        {% include 'flag.tpl' %}

    {% endfor %}

{% endif %}




{% if ida.toggle_states['waffle.switch']  %}

**Waffle Switches**:

    {% for switch in ida.toggle_states['waffle.switch'] %}
        {% include 'switch.tpl' %}

    {% endfor %}

{% endif %}
