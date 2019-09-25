<h1>Feature Toggle Report for {{ environment }}</h1>

<p>This report was created on {{ report_date }}</p>
<p>
Data is pulled from a combination of in-code annotations and database state to create the report described in:
<a href="https://open-edx-proposals.readthedocs.io/en/latest/oep-0017-bp-feature-toggles.html#req-12-report">oep-17</a>
</p>
Key:
<ul>
    <li>Toggles that are ON are displayed in green and listed with 'status' as 'On'</li>
    <li>Toggles that are OFF are displayed in red and listed with 'status' as 'Off'</li>
    <li>Toggles that are not found within the database are displayed without color and no 'status' value</li>
</ul>

{% for ida_name, ida in idas.items() %}

    <h1>{{ ida_name }}</h1>

    <h2>Waffle Flags</h2>
    {% if ida.toggles['waffle.flag']  %}
        {% include 'flag.tpl' %}
    {% else %}
        No waffle flags detected for this IDA
    {% endif %}


    <h2>Waffle Switches</h2>
    {% if ida.toggles['waffle.switch']  %}
        {% include 'switch.tpl' %}
    {% else %}
        No waffle switches detected for this IDA
    {% endif %}


{% endfor %}
