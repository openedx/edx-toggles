"""
Feature toggle base classes
"""

from abc import ABC


class BaseToggle(ABC):
    """
    This abstract base class exposes the basic API required by toggle classes. Toggle instances are tracked in the
    ``_class_instances`` class method, which is exposed via the ``get_instances`` class method.
    """

    # Each child class should implement its own cache of class instances, for instance via WeakSet objects.
    _class_instances = None

    def __init__(self, name, default=False, module_name=""):
        self.validate_name(name)
        self.name = name
        self.default = default
        self.module_name = module_name
        self._class_instances.add(self)

    @classmethod
    def validate_name(cls, name):
        """
        Validate the format of the instance name. This should raise a ValueError in case of incorrect format.
        This method should only be used by child classes, mostly for overriding purposes.
        """

    def is_enabled(self):
        raise NotImplementedError

    @classmethod
    def get_instances(cls):
        """
        Return the list of class instances sorted by name.
        """
        return sorted(cls._class_instances, key=lambda instance: instance.name)
