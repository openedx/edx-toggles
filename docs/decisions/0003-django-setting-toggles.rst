Django Setting Toggles
======================

Status
------

Accepted

Context
-------

Django Setting toggles are Django Settings with True/False values.  Django Setting toggles are implicitly defined when they are used.  For example, example usage might look like::

    getattr(settings, "EXAMPLE_TOGGLE", False)

    # or

    settings.EXAMPLE_SETTING_DICT.get('EXAMPLE_TOGGLE', False)

There are several problems with this style of implicit definition:

* Each usage may or may not define a default value, and the default values are not guaranteed to be consistent.
* It is unclear when and if a default value should be provided with the usage.
* If there are multiple uses of the toggle, it unclear where the code annotation that documents the toggle should live.
* Django Settings toggles are unable to report the same level of detail in the toggle state report as Waffle toggles, because they can't be queried for location or code ownership information.

Decision
--------

We will introduce a simple wrapping class (or classes) that can be used to explicitly define a Django Setting toggle.

Here are some example instances::

    # Toggle setting
    EXAMPLE_SETTING_TOGGLE = SettingToggle("EXAMPLE_TOGGLE", default=False)

    # or

    # Toggle setting in a dict
    EXAMPLE_SETTING_TOGGLE = SettingDictToggle(
        'EXAMPLE_SETTING_DICT',
        'EXAMPLE_TOGGLE',
        default=False,
    )

Its usage can now match that of the waffle wrapping classes (e.g. WaffleFlag).

Here is an example usage::

    EXAMPLE_SETTING_TOGGLE.is_enabled()

SettingToggle will allow for explicit toggle definitions, with the following benefits:

* The definition can live with the app where it will be used, rather than in `common.py` or with no explicit definition.
* The explicit definition can be annotated with documentation.
* The explicit definition provides a single place to set a consistent default value.
* The `toggle state endpoint`_ can provide the location and code ownership of all SettingToggle instances used in an enviroment, because the class will track its instances.
* Additional linting would be possible to ensure manually created annotations are consistent with the code (e.g. default).

Note: The method of using ``defaults.py`` for Django Setting defaults, as detailed in `OEP-45: Configuring and Operating Open edX`_, should only be used if the given IDA requires a different default from the one provided in code. The default provided in code should be the mostly widely used, or the safest from a security perspective, but may not be appropriate for all IDAs.

.. _`OEP-45: Configuring and Operating Open edX`: https://open-edx-proposals.readthedocs.io/en/latest/oep-0045-arch-ops-and-config.html#configuration

Consequences
------------

The main negative consequence is that developers would need to get used to a non-standard interface to working with Django Settings. Hopefully, the consistency with other toggle classes, like WaffleFlag and WaffleSwitch, should make this issue relatively trivial. Additionally, the decision to implement SettingToggle assumes the many advantages listed above outweigh this negative.

Implementation Steps:

* SettingToggle and SettingDictToggle classes need to be implemented.

  * **UPDATE:** See the `implemented setting toggle classes`_.

* The new class should be added to the `toggle state endpoint`_, including querying all instances (like WaffleFlag).

  * **UPDATE:** This is done.

* Any existing settings can be refactored to use instances of the new class.

  * Cleaning up `common.py` where appropriate by removing unnecessary defaults should also be done.
  * We can define these in a `toggles.py` file in the apps. We can consider moving (permanent) waffle definitions from `waffle.py` to `toggles.py`.

.. _implemented setting toggle classes: https://github.com/openedx/edx-toggles/blob/53cf1f71be35ee886521d3d6badafee69198a551/edx_toggles/toggles/internal/setting_toggle.py
.. _toggle state endpoint: https://github.com/openedx/edx-platform/blob/216b99264a50011cb313f5b391abeae61870acee/openedx/core/djangoapps/waffle_utils/views.py#L20

Rejected Alternatives
---------------------

The status-quo, which implicitly defines settings through their usage and may or may not define defaults in `common.py`, even when the default does need to be set.
