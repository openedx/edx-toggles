Toggle life expectancy and use cases
====================================

Status
------

Accepted

Context
-------

At this time, our toggle annotations have the following problems:

* The toggle life expectancy isn't as clear as it could be.
* The justification for permanent toggles is not clear.
* Our use of toggle use cases is also unclear.

The following provides some historical background.

As of the writing of this decision, OEP-17 on Feature Toggles:

* Documents a `set of use cases for toggles`_.
* `Details a reporting requirement`_ of including the toggle use cases in the toggle documentation.

The initial attempt to meet this requirement led to the ``toggle_use_cases`` annotation with the following options:

* incremental_release, launch_date, monitored_rollout, graceful_degradation, beta_testing, vip, opt_out, opt_in, open_edx

In a `PR discussion about toggle_use_cases`_, the following proposal was made:

#. Add ``toggle_life_expectancy`` with values of "temporary" or "permanent".
#. Make ``toggle_use_cases`` required when ``toggle_life_expectancy`` was "permanent".

The second point was proposed to force people to be more intentional around "permanent" toggles, so someone could not simply mark a toggle as "permanent" to avoid the clean-up required for "temporary" toggles without hopefully being a bit more intentional.

In the `PR to implement this proposal`_, the solution was tweaked based on some lost decisions. The update adjusted the ``toggle_uses_cases`` to the following values:

* *temporary*: A new use case that replaced all uses case options that were considered temporary.
* *circuit_breaker*: Replaced "graceful_degradation", although the OEP has not yet been updated.
* *vip, opt_out, opt_in, open_edx*: The other original permanent use case options.

The current implementation has the following flaws:

* Defining "permanent" as the absence of "temporary" reduces clarity for "permanent" toggles.
* The current choices for ``toggle_use_cases`` aren't optimal.

  * The options "circuit_breaker" and "opt_out" ("opt_in") seem like two types of toggles. The former is ops related, and the latter is business related.

    * Note that "opt_out" and "opt_in" only differ in language based on the default of the toggle. For example, if the default is True, then "opt_out" linguistically makes sense as the purpose of the toggle, and if the default is False, "opt_in" makes more sense.

  * The options "vip" vs "open_edx" seem more about the scope at which one might apply the ability to opt-out/opt-in. However, this scope may vary depending on the Open edX instance, and it may not make sense to document the scope selected for edX.org. Additionally, the ``toggle_implementation`` annotation may duplicate this information, assuming the scoping features of the implementation match the intent.
  * In practice, it seems that "open_edx" is often chosen as a general option for permanent toggles, and negates the intent to use ``toggle_use_cases`` to force intentional design and consideration for permanent toggles.

If a stakeholder wanted to review our "permanent" toggles to determine which really must be permanent, and which could potentially be deprecated/removed:

* Most permanent toggles have ``.. toggle_use_cases: open_edx``, which provides no information about the confidence around it being a permanent toggle.
* If confidence were boosted using additional research or a failed attempt to DEPR, there would be no consistent way to document this change in confidence, other than adding text to the ``toggle_description`` and hoping it would be seen.

.. _set of use cases for toggles: https://github.com/edx/open-edx-proposals/blob/c2d3b2a/oeps/oep-0017-bp-feature-toggles.rst#use-cases
.. _Details a reporting requirement: https://github.com/edx/open-edx-proposals/blob/c2d3b2a/oeps/oep-0017-bp-feature-toggles.rst#req-12-report
.. _PR discussion about toggle_use_cases: https://github.com/edx/edx-platform/pull/24815#issuecomment-681174018
.. _PR to implement this proposal: https://github.com/edx/code-annotations/pull/49

Decision
--------

In order to make the toggle life expectancy more clear, and the justification
for permanent toggles more clear, we will take the following actions:

* As originally proposed, introduce ``toggle_life_expectancy`` with values of "temporary" or "permanent". This makes the options very clear.
* Replace ``toggle_use_cases`` with a free-form ``toggle_permanent_justification``.

  * ``toggle_permanent_justification`` would be required for "permanent" toggles.
  * ``toggle_target_removal_date`` would be required for "temporary" toggles (as was the case with the earlier version of "temporary" toggles).
  * The value would be a string description justifying why the toggle is marked as permanent.
  * The purpose of the annotation would be very clear, and will hopefully deter declaring a toggle as "permanent" that really could be "temporary".
  * Authors could reference use cases as required to provide justification.
  * Legacy permanent toggles could use a value like: "Seems permanent, but toggle defined before justification was required." This would make it easier to tell the difference between a toggle marked "permanent" with a strong or weak justification.
  * This annotation would **not** be included in the published documentation, but used for reporting purposes only.
  * "Permanent" toggles with a weak justification could still be candidates for a DEPR(ecation) process to either remove the toggle or strengthen the justification.

* We can remind authors to include use cases in the ``toggle_description`` as well, if it aids documentation for operators or other audiences.

Consequences
------------

* Toggle life expectancy and justification should be more clear.
* Toggle use cases can be noted in other free text toggle annotations, rather than having its own annotation.
* If a stakeholder wanted to review our "permanent" toggles to determine which really must be permanent, and which could potentially be deprecated/removed:

  * They might see ``toggle_permanent_justification`` with any of the following example values:

    * `"See ADR detailing why this toggle must be permanent: ..."`
    * `"See OSPR that added this feature and explains why it is needed for different Open edX instances: ..."`
    * `"Tried DEPR-XXX, but got push back because ..."`
    * `"None"`  (An example of how people work around required fields.)
    * `"Seems permanent, but toggle defined before justification was required."`
    * ...

  * For each of these, the stakeholder could decide whether the justification is strong enough, or whether to initiate DEPR to test the strength of the justification.
  * Stakeholders could also add a prefix like "[Director Approved]", or something else that hopefully won't get copy/pasted, so that the same toggles don't need to be reviewed multiple times once determined to have a strong justification.

* A rollout plan is required for annotation changes. We can use optional code-annotations to expand with new annotations before contracting (removing ``toggle_use_cases``).

  * The longer we wait for the expand phase, the longer we lose useful justification data for new toggles. The updates also may affect more repos over time.
  * Linting should be updated as required as part of the contraction phase of the rollout plan.

* The `how-to documenting_new_feature_toggles.rst`_ should be updated as necessary.
* OEP-17 should be updated to reflect these choices. Note that the OEP is outdated in other ways as well.

.. _how-to documenting_new_feature_toggles.rst: https://github.com/edx/edx-toggles/blob/master/docs/how_to/documenting_new_feature_toggles.rst
