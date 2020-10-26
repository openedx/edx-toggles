"""
This module had been created to expose new-style waffle classes. These are now available from edx_toggles.toggles.
"""
import warnings

from . import *  # pylint: disable=unused-import,wildcard-import

warnings.warn(
    (
        "Importing from edx_toggles.toggles.__future__ is now deprecated."
        " You should import from edx_toggles.toggles instead."
    ),
    DeprecationWarning,
    stacklevel=2,
)
