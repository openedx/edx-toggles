"""
This module contains legacy code for backward compatibility. Waffle flag and switch objects previously required the
creation of namespace objects. The namespace features were all moved to the WaffleSwitch/Flag classes.

To upgrade your code, use the following guidelines. Where previously you had::

    from edx_toggles.toggles import LegacyWaffleSwitch, LegacyWaffleSwitchNamespace
    SOME_NAMESPACE = LegacyWaffleSwitchNamespace("some_namespace")
    SOME_SWITCH = LegacyWaffleSwitch(SOME_NAMESPACE, "some_switch", module_name=__name__)

You should now write::

    from edx_toggles.toggles import WaffleSwitch
    SOME_SWITCH = WaffleSwitch("some_namespace.some_switch", module_name=__name__)

And similarly for waffle flags, replace::

    from edx_toggles.toggles import LegacyWaffleFlag, LegacyWaffleFlagNamespace
    SOME_NAMESPACE = LegacyWaffleFlagNamespace("some_namespace", log_prefix="some_namespace")
    SOME_FLAG = LegacyWaffleFlag(SOME_NAMESPACE, "some_flag", module_name=__name__)

by::

    from edx_toggles.toggles import WaffleFlag
    SOME_FLAG = WaffleFlag("some_namespace.some_flag", module_name=__name__, log_prefix="some_namespace")
"""
from abc import ABC

from edx_django_utils.monitoring import set_custom_attribute

from .flag import WaffleFlag
from .switch import WaffleSwitch


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
        assert name, "The name is required."
        self.name = name
        self.log_prefix = log_prefix if log_prefix else ""
        set_custom_attribute(
            "deprecated_legacy_waffle_class",
            "{}.{}[{}]".format(
                self.__class__.__module__, self.__class__.__name__, self.name
            ),
        )

    def _namespaced_name(self, toggle_name):
        """
        Returns the namespaced name of the waffle switch/flag.

        For example, the namespaced name of a waffle switch/flag would be:
            my_namespace.my_toggle_name

        Arguments:
            toggle_name (String): The name of the flag or switch.
        """
        return f"{self.name}.{toggle_name}"


class LegacyWaffleSwitchNamespace(BaseNamespace):
    """
    Legacy waffle switch namespace class.
    """

    def is_enabled(self, switch_name):
        """
        Returns whether or not the switch is enabled.
        """
        return WaffleSwitch(  # lint-amnesty, pylint: disable=toggle-missing-annotation
            self._namespaced_name(switch_name), __name__
        ).is_enabled()

    def set_request_cache_with_short_name(self, switch_name, value):
        """
        Explicitly set request cache value for the (non-namespaced) switch name. You should avoid using this method as
        much as possible as it may have unexpected side-effects.
        """
        namespaced_name = self._namespaced_name(switch_name)
        # pylint: disable=protected-access
        WaffleSwitch(  # lint-amnesty, pylint: disable=toggle-missing-annotation
            namespaced_name, __name__
        )._cached_switches[
            namespaced_name
        ] = value


class LegacyWaffleSwitch(WaffleSwitch):
    """
    Represents a single waffle switch, enhanced with request level caching.
    """

    def __init__(self, waffle_namespace, switch_name, module_name=None):
        if not isinstance(waffle_namespace, str):
            waffle_namespace = waffle_namespace.name

        self._switch_name = switch_name
        name = f"{waffle_namespace}.{switch_name}"
        super().__init__(name, module_name=module_name)
        set_custom_attribute(
            "deprecated_legacy_waffle_class",
            "{}.{}[{}]".format(
                self.__class__.__module__, self.__class__.__name__, self.name
            ),
        )


class LegacyWaffleFlagNamespace(BaseNamespace):
    """
    Legacy namespace class preserved for backward compatibility.
    """

    def is_flag_active(self, flag_name):
        """
        Returns and caches whether the provided flag is active.
        """
        return WaffleFlag(  # lint-amnesty, pylint: disable=toggle-missing-annotation
            self._namespaced_name(flag_name), module_name=__name__
        ).is_enabled()

    @property
    def _cached_flags(self):
        """
        Legacy property used by CourseWaffleFlag.
        """
        return WaffleFlag.cached_flags()


class LegacyWaffleFlag(WaffleFlag):
    """
    Legacy namespaced waffle flag preserved for backward compatibility.
    """

    def __init__(self, waffle_namespace, flag_name, module_name=None):
        log_prefix = ""
        if not isinstance(waffle_namespace, str):
            log_prefix = waffle_namespace.log_prefix or log_prefix
            waffle_namespace = waffle_namespace.name

        # Non-namespaced flag_name attribute preserved for backward compatibility
        self._flag_name = flag_name
        name = f"{waffle_namespace}.{flag_name}"
        super().__init__(name, module_name=module_name, log_prefix=log_prefix)
        set_custom_attribute(
            "deprecated_legacy_waffle_class",
            "{}.{}[{}]".format(
                self.__class__.__module__, self.__class__.__name__, self.name
            ),
        )
