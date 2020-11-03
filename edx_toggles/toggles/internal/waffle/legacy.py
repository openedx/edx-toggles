"""
Waffle classes in the context of edx-platform and other IDAs.

Includes namespacing and caching for waffle flags.

Usage:

For Waffle Flags, first set up the namespace, and then create flags using the
namespace.  For example::

   WAFFLE_FLAG_NAMESPACE = WaffleFlagNamespace(name='my_namespace')
   SOME_FLAG = WaffleFlag(WAFFLE_FLAG_NAMESPACE, 'some_feature', __name__)

You can check theis flag in code using the following::

    SOME_FLAG.is_enabled()

To test these WaffleFlags, see testutils.py.

In the above examples, you will use Django Admin "waffle" section to configure
for a flag named: my_namespace.some_course_feature

For Waffle Switches, follow the example above for WaffleFlags, but instead use the WaffleSwitchNamespace and
WaffleSwitch classes.

For long-lived flags, you may want to change the default for devstack, sandboxes,
or new Open edX releases. For help with this, see:
openedx/core/djangoapps/waffle_utils/docs/decisions/0001-refactor-waffle-flag-default.rst

Also see ``WAFFLE_FLAG_CUSTOM_ATTRIBUTES`` and docstring for _set_waffle_flag_attribute
for temporarily instrumenting/monitoring waffle flag usage.
"""
import warnings
from abc import ABC
from weakref import WeakSet

from edx_django_utils.monitoring import set_custom_attribute
from waffle import switch_is_active

from ..base import BaseToggle
from .cache import _get_waffle_request_cache as _get_waffle_namespace_request_cache
from .flag import WaffleFlag as NewWaffleFlag


class BaseNamespace(ABC):
    """
    A base class for a request cached namespace for waffle flags/switches.

    An instance of this class represents a single namespace
    (e.g. "course_experience"), and can be used to work with a set of
    flags or switches that will all share this namespace.
    """

    def __init__(self, name, log_prefix=None):
        """
        Initializes the waffle namespace instance.

        Arguments:
            name (String): Namespace string appended to start of all waffle
                flags and switches (e.g. "grades")
            log_prefix (String): Optional string to be appended to log messages
                (e.g. "Grades: "). Defaults to ''.

        """
        warnings.warn(
            (
                "{} is deprecated. Please use non-namespaced edx_toggles.toggles.WaffleFlag/WaffleSwitch"
                " classes instead."
            ).format(self.__class__.__name__),
            DeprecationWarning,
            stacklevel=2,
        )
        set_custom_attribute("deprecated_edx_toggles_waffle", self.__class__.__name__)
        assert name, "The name is required."
        self.name = name
        self.log_prefix = log_prefix if log_prefix else ""

    def _namespaced_name(self, setting_name):
        """
        Returns the namespaced name of the waffle switch/flag.

        For example, the namespaced name of a waffle switch/flag would be:
            my_namespace.my_setting_name

        Arguments:
            setting_name (String): The name of the flag or switch.
        """
        return "{}.{}".format(self.name, setting_name)


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
        value = self.get_request_cache(namespaced_switch_name)
        if value is None:
            value = switch_is_active(namespaced_switch_name)
            self.set_request_cache(namespaced_switch_name, value)
        return value

    def get_request_cache(self, namespaced_switch_name, default=None):
        """
        API for accessing the request cache. In general, users should avoid accessing the namespace cache.
        """
        return self._cached_switches.get(namespaced_switch_name, default)

    def get_request_cache_with_short_name(self, switch_name, default=None):
        """
        Compatibility method. This will be removed soon in favor of the namespaced `get_request_cache` method.
        """
        return self.get_request_cache(
            self._namespaced_name(switch_name), default=default
        )

    def set_request_cache(self, namespaced_switch_name, value):
        """
        Manually set the request cache value. Beware! There be dragons.
        """
        self._cached_switches[namespaced_switch_name] = value

    def set_request_cache_with_short_name(self, switch_name, value):
        """
        Compatibility method. This will be removed soon in favor of the namespaced `set_request_cache` method.
        """
        self.set_request_cache(self._namespaced_name(switch_name), value)

    @property
    def _cached_switches(self):
        """
        Return a dictionary of all namespaced switches in the request cache.
        """
        return _get_waffle_namespace_request_cache().setdefault("switches", {})


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


class WaffleFlagNamespace(BaseNamespace):
    """
    Legacy namespace class preserved for backward compatibility.
    """

    def is_flag_active(self, flag_name):
        """
        Returns and caches whether the provided flag is active.
        """
        return WaffleFlag(self, flag_name).is_enabled()


class WaffleFlag(NewWaffleFlag):
    """
    Legacy namespaced waffle flag preserved for backward compatibility.
    """

    def __init__(self, waffle_namespace, flag_name, module_name=None):
        warnings.warn(
            (
                "{} is deprecated. Please use non-namespaced edx_toggles.toggles.WaffleFlag instead."
            ).format(self.__class__.__name__),
            DeprecationWarning,
            stacklevel=2,
        )
        set_custom_attribute("deprecated_edx_toggles_waffle", "WaffleFlag")
        log_prefix = ""
        if not isinstance(waffle_namespace, str):
            log_prefix = waffle_namespace.log_prefix or log_prefix
            waffle_namespace = waffle_namespace.name

        # Non-namespaced flag_name attribute preserved for backward compatibility
        self.flag_name = flag_name
        name = "{}.{}".format(waffle_namespace, flag_name)
        super().__init__(name, module_name=module_name, log_prefix=log_prefix)

    @property
    def namespaced_flag_name(self):
        """
        Preserved for backward compatibility.
        """
        return self.name
