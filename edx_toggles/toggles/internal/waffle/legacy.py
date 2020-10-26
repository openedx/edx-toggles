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

from edx_django_utils.monitoring import set_custom_attribute

from .flag import WaffleFlag as NewWaffleFlag
from .switch import WaffleSwitch as NewWaffleSwitch


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
    Legacy waffle switch namespace class.
    """

    def is_enabled(self, switch_name):
        """
        Legacy method preserved for backward compatibility.
        """
        return NewWaffleSwitch(self._namespaced_name(switch_name)).is_enabled()

    def get_request_cache(self, namespaced_switch_name, default=None):
        return NewWaffleSwitch(namespaced_switch_name).get_request_cache(
            default=default
        )

    def get_request_cache_with_short_name(self, switch_name, default=None):
        return self.get_request_cache(
            self._namespaced_name(switch_name), default=default
        )

    def set_request_cache(self, namespaced_switch_name, value):
        NewWaffleSwitch(namespaced_switch_name).set_request_cache(value)

    def set_request_cache_with_short_name(self, switch_name, value):
        self.set_request_cache(self._namespaced_name(switch_name), value)


class WaffleSwitch(NewWaffleSwitch):
    """
    Legacy namespaced waffle switch class.
    """

    def __init__(self, waffle_namespace, switch_name, module_name=None):
        warnings.warn(
            (
                "{} is deprecated. Please use non-namespaced edx_toggles.toggles.WaffleSwitch instead."
            ).format(self.__class__.__name__),
            DeprecationWarning,
            stacklevel=2,
        )
        set_custom_attribute("deprecated_edx_toggles_waffle", "WaffleSwitch")
        if not isinstance(waffle_namespace, str):
            waffle_namespace = waffle_namespace.name

        # Non-namespaced flag_name attribute preserved for backward compatibility
        self.switch_name = switch_name
        name = "{}.{}".format(waffle_namespace, switch_name)
        super().__init__(name, module_name=module_name)

    @property
    def namespaced_switch_name(self):
        return self.name


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
