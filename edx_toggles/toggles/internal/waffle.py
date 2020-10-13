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

You could also use the Django Admin "waffle_utils" section to configure a course
override for this same flag (e.g. my_namespace.some_course_feature).

For Waffle Switches, first set up the namespace, and then create the flag name.
For example::

    WAFFLE_SWITCHES = WaffleSwitchNamespace(name=WAFFLE_NAMESPACE)

    ESTIMATE_FIRST_ATTEMPTED = 'estimate_first_attempted'

You can then use the switch as follows::

    WAFFLE_SWITCHES.is_enabled(waffle.ESTIMATE_FIRST_ATTEMPTED)

For long-lived flags, you may want to change the default for devstack, sandboxes,
or new Open edX releases. For help with this, see:
openedx/core/djangoapps/waffle_utils/docs/decisions/0001-refactor-waffle-flag-default.rst

Also see ``WAFFLE_FLAG_CUSTOM_ATTRIBUTES`` and docstring for _set_waffle_flag_attribute
for temporarily instrumenting/monitoring waffle flag usage.
"""
from functools import lru_cache
import logging
from weakref import WeakSet

import crum
from django.conf import settings
from edx_django_utils.cache import RequestCache
from edx_django_utils.monitoring import set_custom_attribute
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
    Provides a single namespace for a set of waffle flags.

    All namespaced flag values are stored in a single request cache containing
    all flags for all namespaces.
    """

    @property
    def _cached_flags(self):
        """
        Returns a dictionary of all namespaced flags in the request cache.
        """
        return _get_waffle_namespace_request_cache().setdefault("flags", {})

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
        self._monitor_value(namespaced_flag_name, value)
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
        set_custom_attribute("warn_flag_no_request_return_value", value)
        return value

    @staticmethod
    def _monitor_value(namespaced_flag_name, value):
        """
        Send waffle flag value to monitoring. We keep this method such that it can be called by child classes (such as
        the CourseWaffleFlag), but it should not be considered a stable API.
        """
        _set_waffle_flag_attribute(namespaced_flag_name, value)


def _get_waffle_namespace_request_cache():
    """
    Returns a request cache shared by all Waffle namespace objects.
    """
    return RequestCache("WaffleNamespace").data


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


# .. toggle_name: WAFFLE_FLAG_CUSTOM_ATTRIBUTES
# .. toggle_implementation: DjangoSetting
# .. toggle_default: False
# .. toggle_description: A list of waffle flags to track with custom attributes having
#   values of (True, False, or Both).
# .. toggle_use_cases: opt_in
# .. toggle_creation_date: 2020-06-17
# .. toggle_warnings: Intent is for temporary research (1 day - several weeks) of a flag's usage.
@lru_cache(maxsize=None)
def _get_waffle_flag_custom_attributes_set():
    attributes = getattr(settings, "WAFFLE_FLAG_CUSTOM_ATTRIBUTES", None) or []
    return set(attributes)


def _set_waffle_flag_attribute(name, value):
    """
    For any flag name in settings.WAFFLE_FLAG_CUSTOM_ATTRIBUTES, add name/value
    to cached values and set custom attribute if the value changed.

    The name of the custom attribute will have the prefix ``flag_`` and the
    suffix will match the name of the flag.
    The value of the custom attribute could be False, True, or Both.

    The value Both would mean that the flag had both a True and False
    value at different times during the transaction. This is most
    likely due to having a course override, as is the case with
    CourseWaffleFlag.

    An example NewRelic query to see the values of a flag in different
    environments, if your waffle flag was named ``my.waffle.flag`` might
    look like::

      SELECT count(*) FROM Transaction
      WHERE flag_my.waffle.flag IS NOT NULL
      FACET appName, flag_my.waffle.flag

    Important: Remember to configure ``WAFFLE_FLAG_CUSTOM_ATTRIBUTES`` for
    LMS, Studio and Workers in order to see waffle flag usage in all
    edx-platform environments.
    """
    if name not in _get_waffle_flag_custom_attributes_set():
        return

    flag_attribute_data = _get_waffle_namespace_request_cache().setdefault(
        "flag_attribute", {}
    )
    is_value_changed = True
    if name not in flag_attribute_data:
        # New flag
        flag_attribute_data[name] = str(value)
    else:
        # Existing flag
        if flag_attribute_data[name] == str(value):
            # Same value
            is_value_changed = False
        else:
            # New value
            flag_attribute_data[name] = "Both"

    if is_value_changed:
        attribute_name = "flag_{}".format(name)
        set_custom_attribute(attribute_name, flag_attribute_data[name])
