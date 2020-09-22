3. feature toggles state in different environments
==================================================

Status
------

Superseded

Context
-------

edX runs its code in multiple environments: devstack, edge, stage, prod.
And we use feature toggles to modify code behavior during run time.

Problem: the feature toggles are set differently in our different envs and its hard for developers know what feature toggles is active where

Decision
--------

Create script to aggregate data from multiple envs into one. Currently, this script exists at: scripts/env_diff_feature_toggle_report_generator.py


.. note:: This ADR is superseded by docs/decisions/0004-basic-feature-toggle-report.rst
