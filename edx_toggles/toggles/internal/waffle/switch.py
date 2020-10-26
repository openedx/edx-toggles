"""
New-style switch classes: these classes no longer depend on namespaces to be created.
"""
from weakref import WeakSet

from waffle import switch_is_active

from .base import BaseWaffle
from .cache import _get_waffle_request_cache


class WaffleSwitch(BaseWaffle):
    """
    Represents a single waffle switch, using both a global and a request cache.
    """

    _class_instances = WeakSet()

    def is_enabled(self):
        """
        Legacy method preserved for backward compatibility.
        """
        value = self.get_request_cache()
        if value is None:
            value = switch_is_active(self.name)
            self.set_request_cache(value)
        return value

    def get_request_cache(self, default=None):
        """
        API for accessing the request cache. In general, users should avoid accessing the namespace cache.
        """
        return self._cached_switches.get(self.name, default)

    def set_request_cache(self, value):
        """
        Manually set the request cache value. Beware! There be dragons.
        """
        self._cached_switches[self.name] = value

    @property
    def _cached_switches(self):
        """
        Return a dictionary of all namespaced switches in the request cache.
        """
        return _get_waffle_request_cache().setdefault("switches", {})
