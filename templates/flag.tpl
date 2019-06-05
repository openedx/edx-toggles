.. admonition:: {{ flag.name }}

    * waffle flag name: {{ flag.name }}
    * waffle flag state (True=On, False=Off): {{ flag.state }}
    * waffle flag on for everyone: {{ flag.data_for_template['everyone'] }}
    * waffle flag on for: {{ flag.data_for_template['percent'] }} %
    * waffle flag on for tests: {{ flag.data_for_template['testing'] }}
    * waffle flag on for superusers: {{ flag.data_for_template['superusers'] }}
    * waffle flag on for staff: {{ flag.data_for_template['staff'] }}
    * waffle flag on for authenticated users: {{ flag.data_for_template['authenticated'] }}
    * waffle flag on for the following languages:
    {% for lang in flag.data_for_template['languages'] %}
        * {{ lang }}
    {% endfor %}
    * waffle flag on as part of a rollout: {{ flag.data_for_template['rollout'] }}
    * created on: {{ flag.data_for_template['creation_date'] }}
    * last modified on: {{ flag.data_for_template['last_modified_date'] }}

