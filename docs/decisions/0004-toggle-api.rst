Feature Toggle API
==================

Status
------

Accepted

Context
-------

The setting toggles introduced in `ADR 0003 <../0003-django-setting-toggles>`__ will be added to this repository. In order to expose a consistent API, the public classes that should be imported from other repositories, such as ``edx-platform``, will be accessible as follows::

    from edx_toggles.toggles import SettingToggle, SettingDictToggle

Decision
--------

All implementation code should be moved to an ``internal`` module. The Public API will be exposed as follows in ``edx_toggles/toggles/__init__.py``::

    from .internal.togglemodule import ...

The benefits of this setup include:

* A clear designation of what is part of the public API.
* The ability to refactor the implementation without changing the API.
* A clear reminder to developers adding new code that it needs to be exposed if it is public.

Consequences
------------

Whenever a new class or function is added to the edx_toggles public API, it should be implemented in the ``internal`` module and explicitly imported in the ``edx_toggles/toggles/__init__.py`` module.
