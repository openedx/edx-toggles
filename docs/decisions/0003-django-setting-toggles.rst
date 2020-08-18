Django Setting Toggles
======================

Status
------

Draft

Context
-------

Django Settings are implicitly defined when they are used.  For example, in ``edx-platform`` the ``FEATURES`` setting dict is used, and an example usage might look like::

    settings.FEATURES.get('EXAMPLE_FEATURE', False)

There are several problems with this style of implicit definition:

* Each usage may or may not define a default value, and the default values are not guaranteed to be consistent.
* It is unclear when and if a default value should be provided with the usage.
* If there are multiple uses of a setting, it unclear where the code annotation that documents the toggle should live.
* Django Settings toggles are unable to report the same level of detail in the toggle state report as Waffle toggles, because they can't be queried for location or code ownership information.

Decision
--------

We will introduce a simple wrapping class that can be used to explicitly define a Django Setting toggle.

Here is an example declaration::

    EXAMPLE_FEATURE_TOGGLE = DjangoSettingToggle(
        "FEATURES['EXAMPLE_FEATURE']",
        default_value=False,
    )

It's usage can now match that of the waffle wrapping classes (e.g. WaffleFlag).

Here is an example usage::

    EXAMPLE_FEATURE_TOGGLE.is_enabled()

DjangoSettingToggle will allow for expicit toggle definitions, with the following benefits:

* A clear definition to annotate with documentation.
* A clear place to set a consistent default value.
* The ability to report in the toggle state endpoint the location and code ownership of any DjangoSettingToggle.
* Additional linting would be possible to ensure manually created annotations are consistent with the code (e.g. default).

Note: The method of using ``defaults.py`` for Django Setting defaults, as detailed in `OEP-45: Configuring and Operating Open edX`_, should only be used if the given IDA requires a different default from the one provided in code. The default provided in code should be the mostly widely used, or the safest from a security perspective, but may not be appropriate for all IDAs.

.. _`OEP-45: Configuring and Operating Open edX`: https://open-edx-proposals.readthedocs.io/en/latest/oep-0045-arch-ops-and-config.html#configuration

Consequences
------------

The main negative consequence is that developers would need to get used to a non-standard interface to working with Django Settings. Hopefully, the consistency with other toggle classes, like WaffleFlag and WaffleSwitch, should make this issue relatively trivial. Additionally, the decision to implement DjangoSettingToggle assumes the many advantages listed above outweigh this negative.

Implementation Steps:

* DjangoSettingToggle class needs to be implemented.
* The new class should be added to the toggle state endpoint, including querying all instances (like WaffleFlag).
* Any existing settings can be refactored to use the new class.

Rejected Alternatives
---------------------

The status-quo, which implicitly defines settings through their usage.
