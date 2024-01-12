.. _documenting_new_feature_toggles:

***************************************
How to: Documenting new feature toggles
***************************************

.. contents::
   :depth: 1
   :local:

Purpose of feature toggle documentation
=======================================

To learn more about feature toggles and how they are used and reported on, see `OEP-17: Feature Toggles`_.

The documentation for feature toggles is a crucial source of information for a very wide audience, including Open edX operators, product owners and developers. The documentation will be available to developers directly in code, and extracted into a human-readable document to be used by all audiences, and especially for Open edX operators.

Please keep all of these audiences in mind when crafting your documentation.

Example Documentation
=====================

Boilerplate template
--------------------

Copy-paste this boilerplate template to document a feature toggle::

    # .. toggle_name: SOME_FEATURE_NAME
    # .. toggle_implementation: WaffleFlag OR WaffleSwitch OR CourseWaffleFlag OR ExperimentWaffleFlag OR ConfigurationModel OR SettingToggle OR SettingDictToggle OR DjangoSetting
    # .. toggle_default: True OR False
    # .. toggle_description: Add here a detailed description of the consequences of enabling this feature toggle.
    #   Note that all annotations can be spread over multiple lines by prefixing every line after the first by
    #   at least three spaces (two spaces plus the leading space).
    # .. toggle_warning: (Optional) Add here additional instructions that users should be aware of. For instance, dependency
    #   on additional settings or feature toggles should be referenced here. If this field is not needed, simply remove it.
    # .. toggle_use_cases: temporary OR circuit_breaker OR vip OR opt_out OR opt_in OR open_edx
    # .. toggle_creation_date: 2020-01-01
    # .. toggle_target_removal_date: 2020-07-01 (this is required if toggle_use_cases includes temporary. If not, simply remove it.)
    # .. toggle_tickets: (Optional) https://openedx.atlassian.net/browse/DEPR-xxx, https://github.com/openedx/edx-platform/blob/master/docs/decisions/xxx.rst, https://github.com/openedx/edx-platform/pull/xxx (details initial feature)
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

- "SettingToggle", "SettingDictToggle": for objects that inherit from each of these.
- "DjangoSetting": for boolean Django Setting toggles that do not yet use the setting toggle classes.
- "WaffleFlag", "WaffleSwitch", "CourseWaffleFlag", "ExperimentWaffleFlag": for objects that inherit from each of these.
- "ConfigurationModel": for objects that inherit from this.

For more details. see :doc:`implement_the_right_toggle_type`.

``toggle_use_cases``
--------------------

To decide what are the use cases of a feature toggle, one should refer to the `list of use cases outlined in OEP-17 on feature toggles <https://open-edx-proposals.readthedocs.io/en/latest/oep-0017-bp-feature-toggles.html#use-cases>`__:

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

Additional considerations:

* Bias should be toward "temporary" toggles.

  * See `OEP-17: Feature toggles use cases <https://open-edx-proposals.readthedocs.io/en/latest/oep-0017-bp-feature-toggles.html#use-cases>`__ for reasons and tips to avoid "permanent" toggles.

* For "temporary" toggles, you must include ``toggle_target_removal_date``. See below.
* For "temporary" toggles, see ``toggle_tickets`` below for recommendations.

``toggle_target_removal_date``
------------------------------

Set to the target date planned for removal of the toggle.

* Use YYYY-MM-DD format (e.g. 2021-04-07).
* Required for "temporary" toggles.
* Do **not** include this annotation for "permanent" toggles. Mark as "temporary" instead.
* If the date is uncertain, add 3-6 months to the creation date.

  * This is not a commitment, but may be used to trigger a conversation about removal.
  * For legacy toggles, it is ok for this date to be in the past.

* If you want to highlight a dependency on a named release, add additional notes to the ``toggle_warning`` or ``toggle_description`` as appropriate.

``toggle_tickets``
------------------

Initially, the ``toggle_tickets`` annotation was intended for removal tickets for "temporary" toggles. This might include:

* a link to a `DEPR(ecation) ticket`_, and/or
* a link to a JIRA ticket created to clean-up the "temporary" toggle.

This annotation is now also used to provide links to other useful supporting documentation, with the following considerations:

* Prefer using links to more permanent documentation, like ADRs, how-tos, READMEs, etc.
* Try to avoid links to PRs or private JIRA tickets. Some alternatives solutions include:

  * Enhance the ``toggle_description`` or ``toggle_warning`` with additional notes.
  * Update the PR description of the PR that adds or updates the annotation to include the links, if they don't need to be a part of the annotation.
  * Write a more permanent doc and use it instead.
  * If it still makes sense to use the link, include it with context (see below).

* If the link url doesn't contain context (e.g. PRs or JIRA tickets other than DEPR), add the context with additional text. For example::

    toggle_tickets: https://openedx.atlassian.net/browse/XXXX-XXX (private clean-up ticket)

.. _DEPR(ecation) ticket: https://open-edx-proposals.readthedocs.io/en/latest/oep-0021-proc-deprecation.html#document


Additional details
==================

Multi-line annotations
----------------------

Note that all annotation fields can be wrapped on multiple lines, as long as every line after the first is prefixed by at least three empty spaces, two spaces plus the base indentation of the first line. For instance::

    # .. toggle_description: line 1
    #   line2

Plain-text formatting
---------------------

Note also that the annotation values will be considered as raw text and will not be parsed in any way. For instance, links and text formatting such as bold, italic or verbatim tags are currently unsupported. This might change in the future.

Long-lines
----------

If you have a really long line, for example with a url that you don't want to break up, you may need to disable pylint using the following::

    # .. toggle_tickets: https://some.com/long/url/that/you/dont/want/to/break/up.rst  # pylint: disable=line-too-long,useless-suppression

Same toggle in multiple services
--------------------------------

If a toggle needs to be synchronized across services:

* The ``toggle_description`` could state that you should read the description for the same toggle in XXX service, rather than duplicating a description.
* The ``toggle_warning`` should note that the value must be consistent with XXX service. XXX will often be the LMS, but not necessarily.

Third-party toggles
-------------------

If we are setting a default for a toggle from a third-party library, include a link to the third-party library documentation for the toggle.

Documenting legacy feature toggles
==================================

This section is specifically geared toward documenting feature toggles that were implemented in the Open edX codebase before this annotation capability existed.

Research
--------

Here are a number of techniques you might use to learn about an existing toggle. Please add any helpful background links to the PR description of the PR that is adding the annotation.

* Search github by replacing the toggle name in the following search url: ``https://github.com/search?q=org%3Aedx+TYPE_YOUR_TOGGLE_OR_SETTING_HERE&type=code``.
* Use ``git blame`` or ``git log search`` (a.k.a. pickaxe).
* Search the `deprecated feature flag documentation in Confluence`_.
* Search the `additional reference tab`_ of the toggle docathon spreadsheet.
* When not a security concern, asking edX.org to compare its Production setting to the default can sometimes shed some light.

.. _deprecated feature flag documentation in Confluence: https://openedx.atlassian.net/wiki/spaces/AC/pages/34734726/edX+Feature+Flags
.. _additional reference tab: https://docs.google.com/spreadsheets/d/1xWbEL6oNu6D84WKBs3aViLRM40xk-vmnmmGAeLyR09A/edit?ts=6008a109#gid=1700780514

Refactor to use new toggle setting classes
------------------------------------------

Undocumented boolean Django Setting toggles defined in the Open edX codebase are probably not yet defined using a ``SettingToggle`` or ``SettingDictToggle``. Read about implementing these toggle classes in :doc:`implement_the_right_toggle_type`.

Refactor direct waffle usage
----------------------------

Replace ``waffle.flag_is_active`` with a new documented ``WaffleFlag``, or ``waffle.switch_is_active`` with a new documented ``WaffleSwitch``.

If the flag or switch name is not namespaced (i.e. doesn't contain a ``.``), use the ``NonNamespacedWaffleFlag`` or ``NonNamespacedWaffleSwitch`` class. All newly defined feature toggles should be namespaced, so these classes only support legacy toggles.

Additional resources
====================

For more details on the individual annotations, see `OEP-17: Feature Toggles`_.

The documentation format used to annotate feature toggles is stored in the code-annotations repository: `feature_toggle_annotations.yaml`_.

See `how-to document non-boolean Django settings`_, for Django settings which are not feature toggles.

.. _`OEP-17: Feature Toggles`: https://open-edx-proposals.readthedocs.io/en/latest/oep-0017-bp-feature-toggles.html
.. _feature_toggle_annotations.yaml: https://github.com/openedx/code-annotations/blob/master/code_annotations/contrib/config/feature_toggle_annotations.yaml
.. _how-to document non-boolean Django settings: https://code-annotations.readthedocs.io/en/latest/contrib/how_to/documenting_django_settings.html
