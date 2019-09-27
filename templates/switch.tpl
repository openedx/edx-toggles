<table>
    <tr>
        <th>Toggle Name</th>
        <th>Status</th>
        <th>Created on</th>
        <th>Modified on</th>
        <th>Description</th>
        <th>Category</th>
        <th>Use Cases</th>
        <th>Implementation</th>
        <th>Creation date</th>
        <th>Expiration date</th>
    </tr>
    {% for toggle in ida.toggles['WaffleSwitch'] %}
        {% if toggle.state_msg == 'On' %}
            <tr style="background-color:#C3FDB8;">
        {% elif toggle.state_msg == 'Off' %}
            <tr style="background-color:#FF4C4C;">
        {% else %}
            <tr>
        {% endif %}
            <td>{{ toggle.name }}</td>
            <td>{{ toggle.state_msg }}</td>
            <td>{{ toggle.data_for_template('state', 'created') }}</td>
            <td>{{ toggle.data_for_template('state', 'modified') }}</td>
            <td>{{ toggle.data_for_template('annotation', 'description') }}</td>
            <td>{{ toggle.data_for_template('annotation', 'category') }}</td>
            <td>{{ toggle.data_for_template('annotation', 'use_cases') }}</td>
            <td>{{ toggle.data_for_template('annotation', 'implementation') }}</td>
            <td>{{ toggle.data_for_template('annotation', 'creation_date') }}</td>
            <td>{{ toggle.data_for_template('annotation', 'expiration_date') }}</td>
        </tr>
    {% endfor %}
</table>
