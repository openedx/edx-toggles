3. Feature toggle report scripts
==============================

Status
------
Approved

Context
-------

EdX uses feature toggles to modify code behavior during run time. We use code annotations (comments above toggle declaration) to document various info about our feature toggles.

However, there are several problems:

* It is difficult to discover which toggles are missing annotations, and many of them are missing annotations.
* It is difficult to see toggle state data from an environment, combined with toggle annotations from code.

A feature toggle report script was already in progress to address these concerns, however it was focused on the ability to compare toggle state across environments, which has since been de-prioritized. The greater priority is for code owners to be able to determine what toggles could be deprecated.


Decision
--------

Repurpose code written for `docs/decisions/0003-feature-toggles-state-in-different-environments.rst` and use it to output a report which contains state(from just one env) and annotations data about feature toggles.

The work for this decision is located at: `scripts/feature_toggle_report.py`

Concequences
------------

We will be repurposing code, which will result is some hacks in our code.


.. note:: This ADR is supersededs docs/decisions/0003-feature-toggles-state-in-different-environments.rst
