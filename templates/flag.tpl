.. admonition:: {{ flag.name }}

    * waffle flag name: {{ flag.name }}
    * state: {{ flag.state.state_msg }}
    * on for everyone: {{ flag.state.data_for_template['everyone'] }}
    * on for: {{ flag.state.data_for_template['percent'] }} %
    * on for tests: {{ flag.state.data_for_template['testing'] }}
    * on for superusers: {{ flag.state.data_for_template['superusers'] }}
    * on for staff: {{ flag.state.data_for_template['staff'] }}
    * on for authenticated users: {{ flag.state.data_for_template['authenticated'] }}
    * on for the following languages:
    {% for lang in flag.state.data_for_template['languages'] %}
        * {{ lang }}
    {% endfor %}
    * on as part of a rollout: {{ flag.state.data_for_template['rollout'] }}
    * created on: {{ flag.state.data_for_template['creation_date'] }}
    * last modified on: {{ flag.state.data_for_template['last_modified_date'] }}
    {% if flag.state._annotation_link %}
    * source: `{{ flag.state.annotation_link }}`_
    {% else %}
    * source: No source data found in annotation report
    {% endif %}

.. _{{ flag.state.annotation_link }}: {{ flag.state.annotation_link }}

