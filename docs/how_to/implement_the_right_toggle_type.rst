***************************************
How to: Implement the right toggle type
***************************************

First choose the general type of toggle and then the more specific implementation below.

There is also a `decision map in OEP-17 on feature toggles <https://open-edx-proposals.readthedocs.io/en/latest/oep-0017-bp-feature-toggles.html#decision-map>`__.

.. contents::
   :depth: 1
   :local:

Choosing the general toggle type
================================

.. list-table::
   :header-rows: 1
   :widths: 15 60 5 5 15

   * - type
     - description
     - config as data
     - config as code
     - beyond on/off
   * - Boolean Django Settings
     - Boolean Django Settings are simple on/off toggles. At edX, this would be set and deployed via remote config.
     -
     - X
     -
   * - Waffle Switches
     - Waffle switches are simple on/off toggles. These are configured through Django admin.
     - X
     -
     -
   * - Waffle Flags
     - Waffle flags are on/off toggles with a variety of other capabilities, such as percent rollout, setting for individual users or courses, etc. These are configured through Django admin.
     - X
     -
     - Percent rollout, setting by user or course, potentially handles A/B experiments.
   * - Config Models with Boolean Fields
     - Config models enable more complex configuration models with audit capabilities. Like Django Settings, config models would only contain toggles if it contained boolean fields. These are configured through Django admin.
     - X
     -
     -

Using your toggle
=================

This section covers waffle switches and flags as well as Django Settings toggles.
For information on `Configuration Models`_ refer to that library.

.. _Configuration Models: https://github.com/edx/django-config-models/

Creating toggles
-----------------

Flags and switches are created with a name. The namespace prefix is used to categorize them and prevent conflicts.

.. code:: python

    FLAG_FOO = WaffleFlag('namespace.feature', module_name=__name__)
    SWITCH_BAR = WaffleSwitch('namespace.feature', module_name=__name__)
    SETTING_TOGGLE_BAZ = SettingToggle("SETTING_NAME", default=False, module_name=__name__)

Administering and testing toggles
----------------------------------

For the waffle flag and switch, you will use Django Admin "waffle" section to configure for a flag named ``namespace.feature``. Setting toggles are a wrapper around standard Django settings.

Functions to override waffle flags in test are provided in `testutils`_.

.. _testutils: https://github.com/edx/edx-toggles/blob/master/edx_toggles/toggles/testutils.py

Accessing toggles
------------------

Unlike the underlying waffle and settings libraries which look up values by name, toggles are imported and used directly:

.. code:: python

    from whereever import FLAG_FOO, SWITCH_BAR, SETTING_TOGGLE_BAZ

    FLAG_FOO.is_enabled()
    SWITCH_BAR.is_enabled()
    SETTING_TOGGLE_BAZ.is_enabled()

State used by toggles
---------------------

Obviously since some toggles take into account the user they must have more data than the zero arguments of ``is_enabled()``.

Waffle switches and flags have a few hidden sources of information. Both use a per-request cache, so a toggle value is stable during a request if there is one. Flags (including Course and Experiment types) additionally access the request via ``crum.get_request`` and through it the user. This means that in an environment without a request, flags will fail unless they are turned on for everyone like a simple switch.

Settings toggles are unsurprisingly reading from the django settings object.

Using other toggles
--------------------

As a best practice, when implementing toggles in a library, we recommend keeping those toggles limited to private or internal use within the library. In other words, only code within the library should refer directly to the toggle.

If you wish to expose whether a library, service, or feature is available to its consumers, we recommend you instead expose a boolean method that may be implemented by wrapping a toggle.

Documenting your new toggle
===========================

As part of implementing your new toggle, read :doc:`how to document the toggle <documenting_new_feature_toggles>`, which should also help you think through the use cases and life expectancy of the toggle.

Toggle Implementation References
===================================

For additional details, see references to the actual toggle class implementations.

Django Setting toggles
----------------------

Use the `SettingToggle and SettingDictToggle classes`_ to implement toggles based on a Django Setting. This new class should be added to the Django app that most closely relates to the setting. See the `ADR for the Setting Toggle classes`_ to understand the advantages over using the Django Setting directly.

If the toggle is being added to edx-platform, and it needs to be used by both LMS and Studio, you can add it to ``openedx/core/toggles.py``.

Avoid referring to boolean Django Settings directly. However, if a boolean setting toggle is implemented without one of the wrapping classes, its annotation implementation would be `DjangoSetting`.

.. _SettingToggle and SettingDictToggle classes: https://github.com/edx/edx-toggles/blob/master/edx_toggles/toggles/internal/setting_toggle.py
.. _ADR for the Setting Toggle classes: ../decisions/0003-django-setting-toggles.rst

Waffle Switches
---------------

Use the `WaffleSwitch class`_, a wrapper around the `waffle`_ switch.

If you are wrapping a legacy switch that does not have a namespaced name (i.e. no ``.`` in the name), use the ``NonNamespacedWaffleSwitch`` instead.

.. _WaffleSwitch class: ../edx_toggles.toggles.internal.waffle.html#module-edx_toggles.toggles.internal.waffle

Waffle Flags
------------

For the basic capabilities, use the `WaffleFlag class`_, a wrapper around the `waffle`_ flag.

If you are wrapping a legacy flag that does not have a namespaced name (i.e. no ``.`` in the name), use the ``NonNamespacedWaffleFlag`` instead.

In edx-platform, there is also:

* `CourseWaffleFlag`_: A WaffleFlag that adds override capabilities per course.
* `ExperimentWaffleFlag`_: A somewhat complex CourseWaffleFlag that enables bucketing of users for A/B experiments.

.. _WaffleFlag class: ../edx_toggles.toggles.internal.waffle.html#module-edx_toggles.toggles.internal.waffle
.. _waffle: https://waffle.readthedocs.io/
.. _CourseWaffleFlag: https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/waffle_utils/__init__.py
.. _ExperimentWaffleFlag: https://github.com/edx/edx-platform/blob/master/lms/djangoapps/experiments/flags.py

Config Models
--------------

A `ConfigurationModel`_ can be used if all other options do not suit your needs. In most cases, it is no longer necessary.

.. _ConfigurationModel: https://github.com/edx/django-config-models/
