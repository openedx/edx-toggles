"""
Base waffle toggle classes.
"""

from edx_django_utils.monitoring import set_custom_attribute

from ..base import BaseToggle


# pylint: disable=abstract-method
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
        # Temporarily track usage of undefined module names
        if not module_name:
            set_custom_attribute(
                "deprecated_module_not_supplied",
                "{}[{}]".format(self.__class__.__name__, self.name),
            )
        # Temporarily set a custom attribute to help track usage of the legacy classes.
        # Example: edx_toggles.toggles.internal.waffle.legacy=WaffleFlag[some.flag]
        # TODO: Remove this custom attribute once internal.waffle.legacy has been removed.
        set_custom_attribute(
            self.__class__.__module__,
            "{}[{}]".format(self.__class__.__name__, self.name),
        )

    @classmethod
    def validate_name(cls, name):
        """
        Ensure that the instance name is correctly namespaced. I.e: it contains a dot (".").
        This method should only be used by child classes, mostly for overriding purposes.
        """
        if "." not in name:
            raise ValueError(
                "Cannot create non-namespaced '{}' {} instance".format(
                    name, cls.__name__
                )
            )
