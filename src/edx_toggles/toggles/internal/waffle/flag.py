"""
Waffle flag classes.
"""
import logging
from weakref import WeakSet

import crum
from waffle import flag_is_active  # lint-amnesty, pylint: disable=invalid-django-waffle-import

from .base import BaseWaffle
from .cache import _get_waffle_request_cache

log = logging.getLogger(__name__)


class WaffleFlag(BaseWaffle):
    """
    Represents a single waffle flag, enhanced with request-level caching.
    """

    _class_instances = WeakSet()

    def __init__(self, name, module_name, log_prefix=""):
        """
        Waffle flag constructor
        """
        self.log_prefix = log_prefix
        super().__init__(name, module_name)

    def is_enabled(self):
        """
        Returns whether or not the flag is enabled.
        """
        return self._get_flag_active()

    @staticmethod
    def cached_flags():
        """
        Returns a dictionary of all flags in the request cache. This method should only ever be used by child classes.
        """
        return _get_waffle_request_cache().setdefault("flags", {})

    def _get_flag_active(self):
        """
        Return and cache the value of the flag activation. This does not handle monitoring.
        """
        # Check global cache
        value = self.cached_flags().get(self.name)
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
            self.cached_flags()[self.name] = value
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
            "%sFlag '%s' accessed without a request, which is likely in the context of a celery task.",
            self.log_prefix,
            self.name,
        )
        value = _is_flag_active_for_everyone(self.name)
        return value


class NonNamespacedWaffleFlag(WaffleFlag):
    """
    Same as the WaffleFlag class, but does not require that the instance name be namespaced. This class is useful for
    migrating existing Flag objects; new instances should always be namespaced.
    """

    @classmethod
    def validate_name(cls, name):
        pass


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
