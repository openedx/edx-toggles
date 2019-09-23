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
