<h1>Feature Toggle Report for {{ environment }}</h1>

<p>This report was created on <b>{{ report_date }}</b></p>
<p>
Data is pulled from a combination of in-code annotations and database state to create the report described in:
<a href="https://open-edx-proposals.readthedocs.io/en/latest/oep-0017-bp-feature-toggles.html#req-12-report">oep-17</a>
</p>
<p>
To see if a feature toggle is currently turned on or off, the 'Status' column in the tables
below will be colorized and displayed accorind the following example:
    <table>
        <tr>
            <th>Status</th>
        </tr>
        <tr style="background-color:#C3FDB8;">
            <td>On - Toggles that are determined to be on in the database</td>
        </tr>
        <tr style="background-color:#FF4C4C;">
            <td>Off - Toggles that are determined to be off in the database</td>
        </tr>
        <tr>
            <td>
                Not found in database - Toggle's whose state could not be
                determined from the database, but are still annotated in the
                codebase
            </td>
        </tr>
    </table>
</p>

{% for ida_name, ida in idas.items() %}

    <h1>{{ ida_name }}</h1>

    <h2>Waffle Flags</h2>
    {% if ida.toggles['WaffleFlag']  %}
        {% include 'flag.tpl' %}
    {% else %}
        No waffle flags detected for this IDA
    {% endif %}


    <h2>Waffle Switches</h2>
    {% if ida.toggles['WaffleSwitch']  %}
        {% include 'switch.tpl' %}
    {% else %}
        No waffle switches detected for this IDA
    {% endif %}


{% endfor %}
