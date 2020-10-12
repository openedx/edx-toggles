"""
Waffle classes in the context of edx-platform and other IDAs.
"""
import logging
from contextlib import contextmanager
from weakref import WeakSet

import crum
from waffle import flag_is_active, switch_is_active

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
    _class_instances = WeakSet()

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

        # Note that the waffle constructor does not provide a default
        name = self.waffle_namespace._namespaced_name(self.switch_name)
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


class WaffleFlagNamespace(BaseNamespace):
    """
    Provides a single namespace for a set of waffle flags.

    All namespaced flag values are stored in a single request cache containing
    all flags for all namespaces.
    """

    @property
    def _cached_flags(self):
        """
        Returns a dictionary of all namespaced flags in the request cache. By default, this namespace does not
        implement any caching.
        """
        return {}

    def is_flag_active(self, flag_name):
        """
        Returns and caches whether the provided flag is active.

        If the flag value is already cached in the request, it is returned.

        Note: A waffle flag's default is False if not defined. If you think you
            need the default to be True, see the module docstring for
            alternatives.

        Arguments:
            flag_name (String): The name of the flag to check.
        """
        namespaced_flag_name = self._namespaced_name(flag_name)
        value = self._get_flag_active(namespaced_flag_name)
        return value

    def _get_flag_active(self, namespaced_flag_name):
        """
        Return the value of the flag activation without touching the _waffle_flag_attribute.
        """
        # Check namespace cache
        value = self._cached_flags.get(namespaced_flag_name)
        if value is not None:
            return value

        # Check in context of request
        request = crum.get_current_request()
        value = self._get_flag_active_request(namespaced_flag_name, request)
        if value is not None:
            return value

        # Return default value
        return self._get_flag_active_default(namespaced_flag_name)

    def _get_flag_active_request(self, namespaced_flag_name, request):
        """
        Get flag value in the context of the current request.
        """
        if request:
            value = flag_is_active(request, namespaced_flag_name)
            self._cached_flags[namespaced_flag_name] = value
            return value
        return None

    def _get_flag_active_default(self, namespaced_flag_name):
        """
        Return default value in the absence of any other, more specific flag value.
        """
        # Check value in the absence of any context
        log.warning(
            u"%sFlag '%s' accessed without a request",
            self.log_prefix,
            namespaced_flag_name,
        )
        # Return the Flag's Everyone value if not in a request context.
        # Note: this skips the cache as the value might be different
        # in a normal request context. This case seems to occur when
        # a page redirects to a 404, or for celery workers.
        value = is_flag_active_for_everyone(namespaced_flag_name)
        return value


def is_flag_active_for_everyone(namespaced_flag_name):
    """
    Returns True if the waffle flag is configured as active for Everyone,
    False otherwise.
    """
    # Import is placed here to avoid model import at project startup.
    # pylint: disable=import-outside-toplevel
    from waffle.models import Flag

    try:
        waffle_flag = Flag.objects.get(name=namespaced_flag_name)
        return waffle_flag.everyone is True
    except Flag.DoesNotExist:
        return False


class WaffleFlag(BaseToggle):
    """
    Represents a single waffle flag, using a cached waffle namespace.
    """

    NAMESPACE_CLASS = WaffleFlagNamespace
    _class_instances = WeakSet()

    def __init__(self, waffle_namespace, flag_name, module_name=None):
        """
        Initializes the waffle flag instance.

        Arguments:
            waffle_namespace (WaffleFlagNamespace | String): Namespace for this flag.
            flag_name (String): The name of the flag (without namespacing).
            module_name (String): The name of the module where the flag is created. This should be ``__name__`` in most
            cases.
        """
        if isinstance(waffle_namespace, str):
            waffle_namespace = self.NAMESPACE_CLASS(name=waffle_namespace)

        self.waffle_namespace = waffle_namespace
        self.flag_name = flag_name

        # Note that the waffle constructor does not provide a default
        name = self.waffle_namespace._namespaced_name(self.flag_name)
        super().__init__(name, default=False, module_name=module_name)

    @property
    def namespaced_flag_name(self):
        """
        Returns the fully namespaced flag name.
        """
        return self.name

    def is_enabled(self):
        """
        Returns whether or not the flag is enabled.
        """
        return self.waffle_namespace.is_flag_active(self.flag_name)
