.. admonition:: {{ switch.name }}

    * waffle switch name: {{ switch.name }}
    * state: {{ switch.state.state_msg }}
    * created on: {{ switch.state.data_for_template['creation_date'] }}
    * last modified on: {{ switch.state.data_for_template['last_modified_date'] }}
    {% if switch.state._annotation_link %}
    * source: `{{ switch.state.annotation_link }}`_
    {% else %}
    * source: No source data found in annotation report
    {% endif %}

.. _{{ switch.state.annotation_link }}: {{ switch.state.annotation_link }}

