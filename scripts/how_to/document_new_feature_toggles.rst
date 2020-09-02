===============================
Documenting new feature toggles
===============================

Feature toggles are boolean values that enable or disable the use of a certain feature. There are many of those across the Open edX codebase: in the form of Django settings, Waffle flags and switches, and  Configuration models, for example. It is important that these feature toggles be correctly annotated to address the following scenarios:

- Generation of human-readable documentation of existing feature toggles for Open edX operators: instead of grepping a large codebase, operators (sysadmins and product owners, for instance) should be able to search an online document to learn how to use and enable features on their platforms.
- Issue detection and resolution at runtime: feature toggles are exposed via an API on a running platform. This allows for automated discovery of feature toggles and, for instance, comparing the state of feature toggles between different environments at runtime. Annotations will allow operators to quickly understand the nature of the discrepancies, and to address issues more efficiently.

Examples
========

Boilerplate template
--------------------

Copy-paste this boilerplate template to document a feature toggle::

    # .. toggle_name: SOME_FEATURE_NAME
    # .. toggle_implementation: WaffleFlag OR WaffleSwitch OR CourseWaffleFlag OR ExperimentWaffleFlag OR ConfigurationModel OR SettingToggle OR SettingDictToggle
    # .. toggle_default: True OR False
    # .. toggle_description: Add here a detailed description of the consequences of enabling this feature toggle.
    #   Note that all annotations can be spread over multiple lines by prefixing every line after the first by
    #   at least two spaces, plus the leading space.
    # .. toggle_warnings: Add here additional instructions that users should be aware of. For instance, dependency
    #   on additional settings or feature toggles should be referenced here. If this field is not required, simply remove it.
    # .. toggle_use_cases: temporary OR circuit_breaker OR vip OR opt_out OR opt_in OR open_edx
    # .. toggle_creation_date: 2020-01-01
    # .. toggle_target_removal_date: 2020-07-01 (this is required if toggle_use_cases is temporary. If not, simply remove it.)
    # .. toggle_tickets: https://openedx.atlassian.net/browse/TICKET-xxx OR https://github.com/edx/edx-platform/pull/xxx
    SOME_FEATURE_NAME = ...

Configuration model
-------------------

Annotations can also be written in docstrings. This is particularly useful for documenting a ConfigurationModel class, for instance::

    class SomeFeatureFlag(ConfigurationModel):
        """
        .. toggle_name: SomeFeatureFlag.enabled
        .. toggle_implementation: ConfigurationModel
        ...
        """

Annotation fields
=================

Most annotation fields are self-explanatory. In this section we describe in more details some of the more complex annotation fields.

``toggle_implementation``
-------------------------

Must be one of the following:

- "WaffleFlag", "WaffleSwitch", "CourseWaffleFlag": for objects that inherit from `waffle_utils' <https://github.com/edx/edx-platform/blob/master/openedx/core/djangoapps/waffle_utils/__init__.py>`__ ``WaffleFlag``, ``WaffleSwitch`` or ``CourseWaffleFlag``, respectively.
- "ExperimentWaffleFlag": this is for objects that inherit from ``lms.djangoapps.experiments.flags.ExperimentWaffleFlag``. See `this documentation page <https://openedx.atlassian.net/wiki/spaces/AC/pages/1250623700/Bucketing+users+for+an+experiment>`__ and the `reference implementation <https://github.com/edx/edx-platform/blob/master/lms/djangoapps/experiments/flags.py#L21>`__.
- "ConfigurationModel": for objects that inherit from `config_models.models.ConfigurationModel <https://github.com/edx/django-config-models/>`__.
- "SettingToggle", "SettingDictToggle": feature toggles can also be enabled by defining a `Django setting <https://docs.djangoproject.com/en/dev/topics/settings/>`__. See the relevant `ADR <https://github.com/edx/edx-toggles/blob/master/docs/decisions/0003-django-setting-toggles.rst>`__.

``toggle_use_cases``
--------------------

To decide what are the use cases of a feature toggle, one should refer to the `list of use cases outlined in OEP-17 <https://open-edx-proposals.readthedocs.io/en/latest/oep-0017-bp-feature-toggles.html#use-cases>`__:

Temporary (``.. toggle_use_cases: temporary``):

* Use Case 1: Incremental Release (expected timeline: 3 months)
* Use Case 2: Launch Date (expected timeline: 3 months)
* Use Case 3: Ops - Monitored Rollout (expected timeline: 3 months)
* Use Case 5: Beta Testing (expected timeline: 6 months)

(Semi-)Permanent:

* Use Case 4: Ops - Circuit Breaker (expected timeline: 5 years, ``.. toggle_use_cases: circuit_breaker``)
* Use Case 6: VIP / White Label (expected timeline: 5 years, ``.. toggle_use_cases: vip``)
* Use Case 7: Opt-out/Opt-in (expected timeline: 2 years, ``.. toggle_use_cases: opt_out`` or ``.. toggle_use_cases: opt_in``)
* Use Case 8: Open edX option (expected timeline: 3 years, ``.. toggle_use_cases: open_edx``)

Note that if ``toggle_use_cases`` is "temporary" then ``toggle_target_removal_date`` **must** be defined.

Additional resources
====================

For more details on the individual annotations, see `OEP-17 <https://open-edx-proposals.readthedocs.io/en/latest/oep-0017-bp-feature-toggles.html#specification>`__.

The documentation format used to annotate feature toggles is stored in the code-annotations repository: `feature_toggle_annotations.yaml <https://github.com/edx/code-annotations/blob/master/code_annotations/config_and_tools/config/feature_toggle_annotations.yaml>`__.

Note that all annotation fields can be wrapped on multiple lines, as long as every line after the first is prefixed by at least two empty spaces, plus the base indentation of the first line. For instance::

    # .. toggle_description: line 1
    #   line2

Note also that the annotation values will be considered as raw text and will not be parsed in any way. For instance, links and text formatting such as bold, italic or verbatim tags are currently unsupported. This might change in the future.
