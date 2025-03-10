"""
Base waffle toggle classes.
"""

import logging

from ..base import BaseToggle

logger = logging.getLogger(__name__)


class BaseWaffle(BaseToggle):
    """
    Base waffle toggle class, which performs waffle name validation.
    """

    def __init__(self, name, module_name):
        """
        Base waffle constructor

        Arguments:
            name (String): The name of the switch. This name must include a dot (".") to indicate namespacing.
            module_name (String): The name of the module where the flag is created. This should be ``__name__`` in most
            cases.
        """
        self.validate_name(name)
        super().__init__(name, default=False, module_name=module_name)

    @classmethod
    def validate_name(cls, name):
        """
        Ensure that the instance name is correctly namespaced. I.e: it contains a dot (".").
        This method should only be used by child classes, mostly for overriding purposes.
        """
        if "." not in name:
            raise ValueError(
                f"Cannot create non-namespaced '{name}' {cls.__name__} instance"
            )
        if name.startswith(" ") or name.endswith(" "):
            logger.error(
                f"{cls.__name__} instance name should not include a blank space prefix or suffix: '{name}'"
            )
