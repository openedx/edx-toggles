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
        {% if toggle.state_msg == 'On' %}
            <tr style="background-color:#C3FDB8;">
        {% elif toggle.state_msg == 'Off' %}
            <tr style="background-color:#FF4C4C;">
        {% else %}
            <tr>
        {% endif %}
            <td>{{ toggle.name }}</td>
            <td>{{ toggle.state_msg }}</td>
            <td>{{ toggle.data_for_template('state', 'everyone') }}</td>
            <td>{{ toggle.data_for_template('state', 'percent') }}</td>
            <td>{{ toggle.data_for_template('state', 'testing') }}</td>
            <td>{{ toggle.data_for_template('state', 'superusers') }}</td>
            <td>{{ toggle.data_for_template('state', 'staff') }}</td>
            <td>{{ toggle.data_for_template('state', 'authenticated') }}</td>
            <td>
                {% if toggle.data_for_template('state', 'languages') == 'No data found' %}
                    No data found
                {% else %}
                    <ul>
                        {% for lang in toggle.data_for_template('state', 'languages') %}
                            <li>{{ lang }}</li>
                        {% endfor %}
                    </ul>
                {% endif %}
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
