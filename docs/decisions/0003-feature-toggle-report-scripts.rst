3. Feature toggle report scripts
================================

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

* We will introduce a new script ``feature_toggle_report.py`` with a simplified script API to report against toggle state from a single environment.
* We will rename the existing script to ``env_diff_feature_toggle_report.py``.
* We will share code between the two scripts.

Consequences
------------

Reusing shared code from the original environment diff script has the benefit of retaining the capabilities of the environment diff script, as well as making this a smaller change, not having to refactor the entire script. This approach has the disadvantage of having a data structure and code that is more complicated than necessary in the simple case of a single environment.
