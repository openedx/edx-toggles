Feature toggles configured for **{{ ida.name }}**:

{% if ida.toggles_by_type('waffle.flag')  %}

**Waffle Flags**:

    {% for flag in ida.toggles_by_type('waffle.flag') %}
        {% include 'flag.tpl' %}

    {% endfor %}

{% endif %}




{% if ida.toggles_by_type('waffle.switch')  %}
    
**Waffle Switches**:

    {% for switch in ida.toggles_by_type('waffle.switch') %}
        {% include 'switch.tpl' %}

    {% endfor %}

{% endif %}
