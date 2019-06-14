Feature Toggle Data for {{ ida.name }}
------------------------{% for _ in ida.name %}-{% endfor %}


.. _feature_toggle_state: {{ ida.name }}-feature-toggle-state.rst

* `feature_toggle_state`_

{% if ida.annotation_report_path %}

.. _code annotation report: {{ ida.name }}/index.rst

* `code annotation report`_

{% else %}

* no code annotation data for {{ ida.name }}

{% endif %}

