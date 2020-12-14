Toggle Reporting
================

Toggle reporting is based on the decision documented in `OEP-17: Feature Toggles`_.

.. _`OEP-17: Feature Toggles`: Feature Toggles:https://open-edx-proposals.readthedocs.io/en/latest/oep-0017-bp-feature-toggles.html

Toggle Reporting Data
---------------------

Toggle reporting consists of two parts:

* Toggle State: Provides runtime data of the current state of toggles in a given environment. See the decision :ref:`toggle_state_decision`.

* Toggle Annotations: Provides static documentation based on code annotations. See the following how-tos:

  * :ref:`documenting_new_feature_toggles`

  * :ref:`get_toggle_annotations`

Toggle Reports Combining Data
-----------------------------

It is possible to combine toggle state and toggle code annotation data into a single report.

Here are some relevant how-tos:

* :ref:`report_for_devstack_or_sandbox`

* :ref:`adding_new_ida`
