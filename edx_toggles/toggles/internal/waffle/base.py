"""
Base waffle toggle classes.
"""

from ..base import BaseToggle


# pylint: disable=abstract-method
class BaseWaffle(BaseToggle):
    """
    Base waffle toggle class, which performs waffle name validation.
    """

    def __init__(self, name, module_name=None):
        """
        Base waffle constructor

        Arguments:
            name (String): The name of the switch. This name must include a dot (".") to indicate namespacing.
            module_name (String): The name of the module where the flag is created. This should be ``__name__`` in most
            cases.
        """
        if "." not in name:
            raise ValueError(
                "Cannot create non-namespaced '{}' {} instance".format(
                    name, self.__class__.__name__
                )
            )
        super().__init__(name, default=False, module_name=module_name)
