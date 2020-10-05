"""
Waffle classes in the context of edx-platform and other IDAs.
"""
import logging
from contextlib import contextmanager

from waffle import switch_is_active

from .base import BaseNamespace, BaseToggle

log = logging.getLogger(__name__)


class WaffleSwitchNamespace(BaseNamespace):
    """
    Provides a single namespace for a set of waffle switches.

    All namespaced switch values are stored in a single request cache containing
    all switches for all namespaces.
    """

    def is_enabled(self, switch_name):
        """
        Returns and caches whether the given waffle switch is enabled.
        """
        namespaced_switch_name = self._namespaced_name(switch_name)
        value = self._cached_switches.get(namespaced_switch_name)
        if value is None:
            value = switch_is_active(namespaced_switch_name)
            self._cached_switches[namespaced_switch_name] = value
        return value

    @contextmanager
    def override(self, switch_name, active=True):
        """
        Overrides the active value for the given switch for the duration of this
        contextmanager.
        Note: The value is overridden in the request cache AND in the model.
        """
        previous_active = self.is_enabled(switch_name)
        try:
            self.override_for_request(switch_name, active)
            with self.override_in_model(switch_name, active):
                yield
        finally:
            self.override_for_request(switch_name, previous_active)

    def override_for_request(self, switch_name, active=True):
        """
        Overrides the active value for the given switch for the remainder of
        this request (as this is not a context manager).
        Note: The value is overridden in the request cache, not in the model.
        """
        namespaced_switch_name = self._namespaced_name(switch_name)
        self._cached_switches[namespaced_switch_name] = active
        log.info(
            "%sSwitch '%s' set to %s for request.",
            self.log_prefix,
            namespaced_switch_name,
            active,
        )

    @contextmanager
    def override_in_model(self, switch_name, active=True):
        """
        Overrides the active value for the given switch for the duration of this
        contextmanager.
        Note: The value is overridden in the model, not the request cache.
        Note: This should probably be moved to a test class.
        """
        # Import is placed here to avoid model import at project startup.
        # pylint: disable=import-outside-toplevel
        from waffle.testutils import override_switch as waffle_override_switch

        namespaced_switch_name = self._namespaced_name(switch_name)
        with waffle_override_switch(namespaced_switch_name, active):
            log.info(
                "%sSwitch '%s' set to %s in model.",
                self.log_prefix,
                namespaced_switch_name,
                active,
            )
            yield

    @property
    def _cached_switches(self):
        """
        Returns a dictionary of all namespaced switches in the request cache. By default, this namespace does not
        implement any caching.
        """
        return {}


class WaffleSwitch(BaseToggle):
    """
    Represents a single waffle switch, using a cached namespace.
    """

    NAMESPACE_CLASS = WaffleSwitchNamespace

    def __init__(self, waffle_namespace, switch_name, module_name=None):
        """
        Arguments:
            waffle_namespace (Namespace | String): Namespace for this switch.
            switch_name (String): The name of the switch (without namespacing).
            module_name (String): The name of the module where the flag is created. This should be ``__name__`` in most
            cases.
        """
        if isinstance(waffle_namespace, str):
            waffle_namespace = self.NAMESPACE_CLASS(name=waffle_namespace)

        self.waffle_namespace = waffle_namespace
        self.switch_name = switch_name
        name = self.waffle_namespace._namespaced_name(self.switch_name)
        # Note that the waffle constructor does not provide a default
        super().__init__(name, default=False, module_name=module_name)

    @property
    def namespaced_switch_name(self):
        """
        For backward compatibility, we still provide the `namespaced_switch_name`, property, even though users should
        now use the `name` attribute.
        """
        return self.name

    def is_enabled(self):
        return self.waffle_namespace.is_enabled(self.switch_name)

    @contextmanager
    def override(self, active=True):
        with self.waffle_namespace.override(self.switch_name, active):
            yield
