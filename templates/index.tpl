{% block content %}
Feature Toggle Report
---------------------

Feature toggles are currently configured in the following IDAs:

{% for ida in idas %}

.. _{{ ida }}: {{ ida }}.rst

* `{{ ida }}`_

{% endfor %}

{% endblock %}

