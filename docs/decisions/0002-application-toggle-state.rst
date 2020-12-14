.. _toggle_state_decision:

Application Toggle State
========================

Status
------

Draft

Context
-------

* Toggle State reporting tools are partially implemented, supporting waffle, but not Django Setting values.
* Toggle state data gathering was originally implemented by reading databases directly. It is possible this was done for security purposes, but details of that original decision are uncertain.
* Additional environments and IDAs (beyond LMS) would require special handling for connecting to databases, including devstack and sandboxes.

Decision
--------

In a shared library, we will implement a Django App plugin to expose a new REST endpoint that would return the state of all toggles in the application.

For Django Settings, the endpoint can recurse over any dict settings and return any settings that are explicitly True or False.

For `WaffleFlag`_ (and other waffle based wrapping classes), we can include all initialized instances, whether or not they have a record in the database. Note: although WaffleFlag exists in `edx-platform` as of the writing of this ADR, it is in process of being moved to this repository.

This approach has the following benefits:

* Toggle Django Settings can easily report their values, and the reported value would account for any defaults in common.py.
* It would be simple to see up-to-date state for a specific IDA and environment in a consistent manner, and this capability would exist for all Open edX instances. This would include devtack and Sandboxes.
* Since the application already has access to both its settings and database, the required results are easy to access.
* Since the application can access both the data in the database, as well as any initialized toggle classes, state gathering could be simplified and more accurate. For example, a CourseWaffleFlag wouldn’t be misreported as a WaffleFlag if it had no override data in the database.

For security purposes:

* The endpoint will require staff access.
* No Django Setting values will be returned directly without ensuring that explicitly True/False are the only possible values.

Note: Django Setting toggles could also have a default provided upon retrieval. That topic will be covered under a separate ADR.

.. _WaffleFlag: https://github.com/edx/edx-platform/blob/77e490f0578cbaa5a4c2e6110b848cceef30962b/openedx/core/djangoapps/waffle_utils/__init__.py#L373

Consequences
------------

The implementation of this toggle state endpoint needs to live with the toggle classes that currently live in `waffle_utils`_ in edx-platform. These toggle classes will need to finally be moved to this repository, as originally planned.

The current implementation of toggle state gathering will be refactored/reworked into the new endpoint.

.. _waffle_utils: https://github.com/edx/edx-platform/tree/77e490f0578cbaa5a4c2e6110b848cceef30962b/openedx/core/djangoapps/waffle_utils

Rejected Alternatives
---------------------

This decision would be a rejection of the current implementation of going directly to the database of each environment, bypassing the application, to try to get the current state of certain toggles like WaffleFlag.
