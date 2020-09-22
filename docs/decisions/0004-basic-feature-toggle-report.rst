4. basic feature toggle report
==============================

Status
------
Approved

Context
-------

edX uses feature toggles to modify code behavior during run time.
We use code annotations(comments above toggle declaration) to document various info about our feature toggles.

Very few of our toggles are documented properly.

Second context:

The team has already has already been working on a script to create a report on toggle state in our various environments(documented in `docs/decisions/0003-env-diff.rst`). Creating diff report between envirnonments is no longer a priority.


Decision
--------

Repurpose code written for `docs/decisions/0003-feature-toggles-state-in-different-environments.rst` and use it to output a report which contains state(from just one env) and annotations data about feature toggles.

The work for this decision is located at: `scripts/feature_toggle_report.py`

Concequences
------------

We will be repurposing code, which will result is some hacks in our code.


.. note:: This ADR is supersededs docs/decisions/0003-feature-toggles-state-in-different-environments.rst
