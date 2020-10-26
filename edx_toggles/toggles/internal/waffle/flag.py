"""
New-style waffle classes: these classes no longer depend on namespaces to be created.
"""
import logging
from weakref import WeakSet

import crum
from django.conf import settings
from edx_django_utils.monitoring import set_custom_attribute
from waffle import flag_is_active

from .base import BaseWaffle
from .cache import _get_waffle_request_cache

log = logging.getLogger(__name__)


class WaffleFlag(BaseWaffle):
    """
    Represents a single waffle flag, using both a global and a request cache.
    """

    _class_instances = WeakSet()

    def __init__(self, name, module_name=None, log_prefix=""):
        """
        Waffle flag constructor
        """
        self.log_prefix = log_prefix
        super().__init__(name, module_name=module_name)

    def is_enabled(self):
        """
        Returns whether or not the flag is enabled.
        """
        value = self._get_flag_active()
        self._monitor_value(value)
        return value

    @property
    def _cached_flags(self):
        """
        Returns a dictionary of all flags in the request cache.
        """
        return _get_waffle_request_cache().setdefault("flags", {})

    def _get_flag_active(self):
        """
        Return and cache the value of the flag activation. This does not handle monitoring.
        """
        # Check global cache
        value = self._cached_flags.get(self.name)
        if value is not None:
            return value

        # Check in context of request
        request = crum.get_current_request()
        value = self._get_flag_active_request(request)
        if value is not None:
            return value

        # Return default value
        return self._get_flag_active_no_request()

    def _get_flag_active_request(self, request):
        """
        Get flag value in the context of the current request.
        """
        if request:
            value = flag_is_active(request, self.name)
            self._cached_flags[self.name] = value
            return value
        return None

    def _get_flag_active_no_request(self):
        """
        Return default value in the absence of any other, more specific flag value. This triggers warnings, as waffle
        flag values are not supposed to be accessed in the absence of any request context.

        Note: this skips the cache as the value might be different in a normal request context. This case seems to
        occur when a page redirects to a 404, or for celery workers.
        """
        log.warning(
            "%sFlag '%s' accessed without a request",
            self.log_prefix,
            self.name,
        )
        value = _is_flag_active_for_everyone(self.name)
        set_custom_attribute("warn_flag_no_request_return_value", value)
        return value

    def _monitor_value(self, value):
        """
        Send waffle flag value to monitoring. We keep this method such that it can be called by child classes (such as
        edx-platform's waffle_utils.CourseWaffleFlag), but it should not be considered a stable API.
        """
        _set_waffle_flag_attribute(self.name, value)


def _is_flag_active_for_everyone(flag_name):
    """
    Returns True if the waffle flag is configured as active for Everyone,
    False otherwise.
    """
    # Import is placed here to avoid model import at project startup.
    # pylint: disable=import-outside-toplevel
    from waffle.models import Flag

    try:
        waffle_flag = Flag.objects.get(name=flag_name)
        return waffle_flag.everyone is True
    except Flag.DoesNotExist:
        return False


def _set_waffle_flag_attribute(name, value):
    """
    For any flag name in settings.WAFFLE_FLAG_CUSTOM_ATTRIBUTES, add name/value
    to cached values and set custom attribute if the value changed.

    Important: Remember to configure ``WAFFLE_FLAG_CUSTOM_ATTRIBUTES`` for
    LMS, Studio and Workers in order to see waffle flag usage in all
    edx-platform environments.

    .. setting_name: WAFFLE_FLAG_CUSTOM_ATTRIBUTES
    .. setting_default: False
    .. setting_description: A set of waffle flags to track with custom attributes having
      values of (True, False, or Both). The name of the custom attribute will have the prefix ``flag_`` and the suffix
      will match the name of the flag. The value of the custom attribute could be False, True, or Both.

      The value Both would mean that the flag had both a True and False value at different times during the
      transaction. This is most likely due to happen in WaffleFlag child classes, such as edx-platform's
      waffle_utils.CourseWaffleFlag.

      An example NewRelic query to see the values of a flag in different environments, if your waffle flag was named
      ``my.waffle.flag`` might look like::

        SELECT count(*) FROM Transaction
        WHERE flag_my.waffle.flag IS NOT NULL
        FACET appName, flag_my.waffle.flag

    .. setting_warning: This will work if it is a list, but it might be less performant.
    """
    custom_attributes = getattr(settings, "WAFFLE_FLAG_CUSTOM_ATTRIBUTES", None) or []
    if name not in custom_attributes:
        return

    flag_attribute_data = _get_waffle_request_cache().setdefault("flag_attribute", {})
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
