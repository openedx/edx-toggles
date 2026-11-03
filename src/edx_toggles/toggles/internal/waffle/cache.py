"""
Caching utilities for waffle toggles.
"""
from edx_django_utils.cache import RequestCache


def _get_waffle_request_cache():
    """
    Returns a request cache shared by all Waffle objects.
    """
    return RequestCache("WaffleNamespace").data
