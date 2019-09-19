<h1>Feature Toggle Report for {{ environment }}</h1>

This report was created on {{ report_date }}

{% for ida_name, ida in idas.items() %}

    <h1>{{ ida_name }}</h1>

    <h2>Waffle Flags</h2>
    <table>
        <tr>
            <th>Toggle Name</th>
            <th>Status</th>
            <th>Everyone</th>
            <th>Percent</th>
            <th>Tests</th>
            <th>Superusers</th>
            <th>Staff</th>
            <th>Authenticated users</th>
            <th>Languages</th>
            <th>Rollout</th>
            <th>First modified</th>
            <th>Last modified</th>
            <th>Description</th>
            <th>Category</th>
            <th>Use Cases</th>
            <th>Type</th>
            <th>Creation date</th>
            <th>Expiration date</th>
        </tr>
        {% for toggle in ida.toggles['waffle.flag'] %}
            <tr>
                <td>{{ toggle.name }}</td>
                <td>{{ toggle.state.state_msg }}</td>
                <td>{{ toggle.data_for_template('state', 'everyone') }}</td>
                <td>{{ toggle.data_for_template('state', 'percent') }}</td>
                <td>{{ toggle.data_for_template('state', 'testing') }}</td>
                <td>{{ toggle.data_for_template('state', 'superusers') }}</td>
                <td>{{ toggle.data_for_template('state', 'staff') }}</td>
                <td>{{ toggle.data_for_template('state', 'authenticated') }}</td>
                <td>
                    <ul>
                        {% for lang in toggle.data_for_template('state', 'languages') %}
                            <li>{{ lang }}</li>
                        {% endfor %}
                    </ul>
                </td>
                <td>{{ toggle.data_for_template('state', 'rollout') }}</td>
                <td>{{ toggle.data_for_template('state', 'created') }}</td>
                <td>{{ toggle.data_for_template('state', 'modified') }}</td>
                <td>{{ toggle.data_for_template('annotation', 'description') }}</td>
                <td>{{ toggle.data_for_template('annotation', 'category') }}</td>
                <td>{{ toggle.data_for_template('annotation', 'use_cases') }}</td>
                <td>{{ toggle.data_for_template('annotation', 'type') }}</td>
                <td>{{ toggle.data_for_template('annotation', 'creation_date') }}</td>
                <td>{{ toggle.data_for_template('annotation', 'expiration_date') }}</td>
            </tr>
        {% endfor %}
    </table>


    <h2>Waffle Switches</h2>
    <table>
        <tr>
            <th>Toggle Name</th>
            <th>Status</th>
            <th>Created on</th>
            <th>Modified on</th>
            <th>Description</th>
            <th>Category</th>
            <th>Use Cases</th>
            <th>Type</th>
            <th>Creation date</th>
            <th>Expiration date</th>
        </tr>
        {% for toggle in ida.toggles['waffle.switch'] %}
            <tr>
                <td>{{ toggle.name }}</td>
                <td>{{ toggle.state.state_msg }}</td>
                <td>{{ toggle.data_for_template('state', 'created') }}</td>
                <td>{{ toggle.data_for_template('state', 'modified') }}</td>
                <td>{{ toggle.data_for_template('annotation', 'description') }}</td>
                <td>{{ toggle.data_for_template('annotation', 'category') }}</td>
                <td>{{ toggle.data_for_template('annotation', 'use_cases') }}</td>
                <td>{{ toggle.data_for_template('annotation', 'type') }}</td>
                <td>{{ toggle.data_for_template('annotation', 'creation_date') }}</td>
                <td>{{ toggle.data_for_template('annotation', 'expiration_date') }}</td>
            </tr>
        {% endfor %}
    </table>


{% endfor %}

