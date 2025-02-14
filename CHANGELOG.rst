Change Log
----------

..
   All enhancements and patches to edx_toggles will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
~~~~~~~~~~

* Log error on waffle object creation when name includes a blank space as a prefix or suffix.

[5.3.0] - 2025-02-14
--------------------

* Drop Python 3.8 support.

[5.2.0] - 2024-03-31
--------------------

* Added python3.11 and 3.12 support. Dropped django32 support.

[5.1.1] - 2024-01-31
--------------------

* Fix toggle report to output all settings.

[5.1.0] - 2023-08-02
--------------------

* Added support for Django 4.2
* Rename toggle_warnings to toggle_warning for consistency with setting_warning.
* Switch from ``edx-sphinx-theme`` to ``sphinx-book-theme`` since the former is
  deprecated

[5.0.0] - 2022-04-22
--------------------

* BREAKING CHANGE: Removed LegacyWaffle* classes. Although this is a breaking change, all known uses have already been fixed.
* Handle the case where certain toggle names come in as ``None`` when generating summary reports.
* Add ADR for updating annotations for toggle life expectancy and use cases.

[4.3.0] - 2022-01-31
--------------------

Removed
~~~~~~~

* Removed Django22, 30, 31

Added
~~~~~~~
* Added Django40 support in CI

[4.2.0] - 2021-07-07
~~~~~~~~~~~~~~~~~~~~

* Added support for django3.0, 3.1 and 3.2

[4.1.0] - 2021-02-10
~~~~~~~~~~~~~~~~~~~~

* Expose toggle state report via a Python API.

[4.0.0] - 2021-01-24
~~~~~~~~~~~~~~~~~~~~

* BREAKING CHANGE: Remove now unnecessary ``edx_toggles.toggles.__future__`` module.
* BREAKING CHANGE: Remove the following methods and properties: ``LegacyWaffleFlagNamespace.set_monitor_value``,  ``LegacyWaffleSwitch.switch_name``, ``LegacyWaffleSwitch.namespaced_switch_name``, ``LegacyWaffleFlag.flag_name``, ``LegacyWaffleFlag.namespaced_flag_name``, ``LegacyWaffleFlag.waffle_namespace``.
* BREAKING CHANGE: Remove ``LegacyWaffleFlagNamespace._set_monitor_value`` method
* Monitoring:

    * Add the following custom attribute: "deprecated_legacy_waffle_class"
    * Remove the following custom attributes: "deprecated_module_not_supplied", "warn_flag_no_request_return_value", "deprecated_waffle_method", "deprecated_waffle_legacy_method", "deprecated_compatible_legacy_waffle_class".
* Rename ``toggles.internal.legacy.Waffle*`` classes to ``toggles.internal.legacy.LegacyWaffle*``.

[3.1.0] - 2021-01-18
~~~~~~~~~~~~~~~~~~~~

* Dropped support for ``Python3.5``.
* Fix ``toggle_type`` column value from the toggle state report for the ``SettingToggle`` and ``SettingDictToggle`` classes: the column is now set to "django_settings".

[2.1.0] - 2021-01-12
~~~~~~~~~~~~~~~~~~~~

* Stop monitoring waffle flag values via ``WaffleFlag.set_monitor_value`` calls. The deprecated method is preserved for backward compatibility.


[2.0.0] - 2020-11-05
~~~~~~~~~~~~~~~~~~~~

* BREAKING CHANGE: The ``WaffleFlagNamespace`` and ``WaffleSwitchNamespace`` classes have been removed. You can either rename to ``LegacyWaffleFlagNamespace`` and ``LegacyWaffleSwitchNamespace``, which are deprecated, or you can move to the newer waffle classes that no longer use these Namespace classes (see below).
* BREAKING CHANGE: The ``WaffleFlag`` and ``WaffleSwitch`` classes exposed in ``toggles`` no longer use the Namespace classes and are now the classes which were previously only available in ``toggles.__future__``.

    * If you were importing from ``edx_toggles.toggles.__future__`` before, then you simply need to import from ``edx_toggles.toggles``. Importing from ``__future__`` will continue to work but will trigger a deprecation warning.
    * If you were importing from ``edx_toggles.toggles``, then you either need to:

        * Migrate your legacy namespaced classes to the new-style classes (see the new behaviour below), or
        * Import ``LegacyWaffleFlag`` instead of ``WaffleFlag`` and ``LegacyWaffleSwitch`` instead of ``WaffleSwitch``. Note that these classes will be removed soon, so it's preferable to migrate to the new classes already.

    * The new Waffle classes introduce the following changes:

        * They no longer use Namespace classes like ``WaffleSwitchNamespace`` or ``WaffleFlagNamespace``.
        * The ``WaffleSwitchNamespace._namespaced_name`` and ``WaffleFlagNamespace._namespaced_name`` methods are replaced by the ``WaffleSwitch.name`` and ``WaffleFlag.name`` attributes.
        * The ``WaffleSwitchNamespace.is_enabled`` method is replaced by the ``WaffleSwitch.is_enabled`` method.
        * The ``WaffleSwitchNamespace.set_request_cache_with_short_name`` method has no replacement because an alternative solution should be found.  You could (but really shouldn't) use the ``WaffleSwitch._cached_switches`` property.
        * The ``WaffleSwitch.switch_name`` attribute is deprecated: switches should only ever be referred to using their fully namespaced names.
        * The ``WaffleSwitch.switch_name`` attribute no longer exists. Switches should only ever be referred to using their fully namespaced names.  If you need the non-namespaced name, it must be parsed from the namespaced name.
        * The ``WaffleFlagNamespace.is_flag_active`` method is replaced by ``WaffleFlag.is_enabled``.
        * The ``WaffleFlagNamespace._monitor_value`` method is replaced by ``WaffleFlag.set_monitor_value``.
        * The ``WaffleFlagNamespace._cached_flags`` attribute is replaced by the ``WaffleFlag.cached_flags`` method.
        * The ``WaffleFlag`` and ``WaffleSwitch`` ``module_name`` constructor argument is now mandatory.
        * The ``WaffleFlag.flag_name`` attribute is deprecated.
        * The ``WaffleFlag.flag_name`` attribute no longer exists. Flags should only ever be referred to using their fully namespaced names.  If you need the non-namespaced name, it must be parsed from the namespaced name.
        * The ``WaffleFlag.waffle_namespace`` attribute no longer exists, since there is no longer a separate namespace object.

[1.2.2] - 2020-12-22
~~~~~~~~~~~~~~~~~~~~

More improvements to monitoring of legacy waffle class imports.

* Add ``deprecated_incompatible_legacy_waffle_class`` custom attribute to any class (including subclasses), using the backward-incompatible imports that will be removed in 2.0.0.
* Add ``deprecated_compatible_legacy_waffle_class`` custom attribute to any class (including subclasses) using the legacy classes compatible with 2.0.0 imports, but which should be removed in 3.0.0 (or some future major version).
* Remove ``deprecated_edx_toggles_waffle`` custom attribute. In two cases, it was replaced by the new ``*_legacy_waffle_class`` custom attributes.  In one case, it was replaced with the already existing and more appropriate ``deprecated_waffle_legacy_method`` custom attribute.

[1.2.1] - 2020-12-17
~~~~~~~~~~~~~~~~~~~~

* Improve monitoring of legacy Waffle class imports. We should watch for "edx_toggles.toggles.internal.waffle.legacy.WaffleSwitch" custom attributes.

[1.2.0] - 2020-11-05
~~~~~~~~~~~~~~~~~~~~

* Start the deprecation process of the waffle namespace classes:

  * Introduce LegacyWaffleFlag, LegacyWaffleSwitch for use with namespaces.
  * Begin deprecation/refactoring of namespacing code, including deprecation monitoring and warnings.
  * Note: WaffleFlag and WaffleSwitch still use namespaces as well (for now).
  * Introduce the ``toggles.__future__`` module for applications that need to be forward-compatible right away.

[1.1.1] - 2020-10-27
~~~~~~~~~~~~~~~~~~~~

* Fix cache-checking in WaffleSwitchNamespace

[1.1.0] - 2020-10-23
~~~~~~~~~~~~~~~~~~~~

* Backport ``override_waffle_switch`` test utility function from edx-platform

[1.0.0] - 2020-10-13
~~~~~~~~~~~~~~~~~~~~

* Fix missing ``module_name`` argument in ``SettingDictToggle`` constructor.
* Extract waffle classes from edx-platform and move them here following ADR `#2 <docs/decisions/0002-application-toggle-state.rst>`__, `#3 <docs/decisions/0003-django-setting-toggles.rst>`__, `#4 <docs/decisions/0004-toggle-api.rst>`__. This does not introduce backward-incompatible changes, *yet*.
* Fix pinned requirements and incorrect root url that overrode edx-platform's.

[0.3.0] - 2020-09-23
~~~~~~~~~~~~~~~~~~~~

First release to PyPI (2020-10-02)

* Implement ``SettingToggle`` and ``SettingDictToggle``.

[0.2.2] - 2020-09-11
~~~~~~~~~~~~~~~~~~~~

* Document the writing of feature toggles annotations.

[0.2.1] - 2020-08-03
~~~~~~~~~~~~~~~~~~~~

* Add ADR for the purpose of this repository.
* Add ADR for implementing a Toggle State endpoint.
* Add toggles report with CSV output using new CsvRenderer.
* Add CourseWaffleFlag and course override data to toggle report.
* Add output for waffle flag course overrides to data gatherer
* Add additional options to scripts/feature_toggle_report_generator

    * filter toggle types and envs, add github_url, and change name of ida in report

* Modified scripts/feature_toggle_report_generator to work based on envs
* Removed confluence integration
* Moved HtmlRenderer to its own file
* Add ADR for new SettingToggle. (see 0003-django-setting-toggles.rst)

[0.2.0] - 2020-05-27
~~~~~~~~~~~~~~~~~~~~

* Removed caniusepython3.

[0.2.0] - 2020-05-05
~~~~~~~~~~~~~~~~~~~~

* Added support for python 3.8 and dropped support Django versions older than 2.2

[0.1.0] - 2019-04-08
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Initial version
