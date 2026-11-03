"""
New-style switch classes: these classes no longer depend on namespaces to be created.
"""
from weakref import WeakSet

from waffle import switch_is_active  # lint-amnesty, pylint: disable=invalid-django-waffle-import

from .base import BaseWaffle
from .cache import _get_waffle_request_cache


class WaffleSwitch(BaseWaffle):
    """
    Represents a single waffle switch, enhanced with request-level caching.
    """

    _class_instances = WeakSet()

    def is_enabled(self):
        """
        Returns whether or not the switch is enabled.
        """
        value = self._cached_switches.get(self.name)
        if value is None:
            value = switch_is_active(self.name)
            self._cached_switches[self.name] = value
        return value

    @property
    def _cached_switches(self):
        """
        Return a dictionary of all namespaced switches in the request cache.
        Note that this property might be used elsewhere, in edx-platform for instance (although it probably shouldn't).
        """
        return _get_waffle_request_cache().setdefault("switches", {})


class NonNamespacedWaffleSwitch(WaffleSwitch):
    """
    Same as the WaffleSwitch class, but does not require that the instance name be namespaced. This class is useful for
    migrating existing Switch objects; new instances should always be namespaced.
    """

    @classmethod
    def validate_name(cls, name):
        pass
