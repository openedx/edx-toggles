<h1>Feature Toggle Report for {{ environment }}</h1>

This report was created on {{ report_date }}

{% for ida_name, ida in idas.items() %}

    <h1>{{ ida_name }}</h1>

    <h2>Waffle Flags</h2>
    {% if ida.toggles['waffle.flag']  %}
        {% include 'flag.tpl' %}
    {% else %}
        No flags
    {% endif %}


    <h2>Waffle Switches</h2>
    {% if ida.toggles['waffle.switch']  %}
        {% include 'switch.tpl' %}
    {% else %}
        No switches
    {% endif %}


{% endfor %}

