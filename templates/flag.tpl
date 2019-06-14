.. admonition:: {{ flag.name }}

    * waffle flag name: {{ flag.name }}
    * state: {{ flag.state_msg }}
    * on for everyone: {{ flag.data_for_template['everyone'] }}
    * on for: {{ flag.data_for_template['percent'] }} %
    * on for tests: {{ flag.data_for_template['testing'] }}
    * on for superusers: {{ flag.data_for_template['superusers'] }}
    * on for staff: {{ flag.data_for_template['staff'] }}
    * on for authenticated users: {{ flag.data_for_template['authenticated'] }}
    * on for the following languages:
    {% for lang in flag.data_for_template['languages'] %}
        * {{ lang }}
    {% endfor %}
    * on as part of a rollout: {{ flag.data_for_template['rollout'] }}
    * created on: {{ flag.data_for_template['creation_date'] }}
    * last modified on: {{ flag.data_for_template['last_modified_date'] }}
    {% if flag._annotation_link %}
    * source: `{{ flag.annotation_link }}`_
    {% else %}
    * source: No source data found in annotation report
    {% endif %}

.. _{{ flag.annotation_link }}: {{ flag.annotation_link }}

