Feature Toggle Data for {{ ida.name }}
--------------------------------------


.. _feature_toggle_state: {{ ida.name }}-feature-toggle-state.rst

* `feature_toggle_state`_

{% if ida.annotation_report_path %}

* code annotation report: {{ ida.annotation_report_path }}

{% else %}

* no code annotation data for {{ ida.name }}

{% endif %}

