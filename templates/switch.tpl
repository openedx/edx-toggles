.. admonition:: {{ switch.name }}

    * waffle switch name: {{ switch.name }}
    * state: {{ switch.state_msg }}
    * created on: {{ switch.data_for_template['creation_date'] }}
    * last modified on: {{ switch.data_for_template['last_modified_date'] }}
    {% if switch._annotation_link %}
    * source: `{{ switch.annotation_link }}`_
    {% else %}
    * source: No source data found in annotation report
    {% endif %}

.. _{{ switch.annotation_link }}: {{ switch.annotation_link }}

