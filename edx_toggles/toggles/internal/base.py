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
        self.name = name
        self.default = default
        self.module_name = module_name
        self._class_instances.add(self)

    def is_enabled(self):
        raise NotImplementedError

    @classmethod
    def get_instances(cls):
        """
        Return the list of class instances sorted by name.
        """
        return sorted(cls._class_instances, key=lambda instance: instance.name)


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

    def _namespaced_name(self, setting_name):
        """
        Returns the namespaced name of the waffle switch/flag.

        For example, the namespaced name of a waffle switch/flag would be:
            my_namespace.my_setting_name

        Arguments:
            setting_name (String): The name of the flag or switch.
        """
        return "{}.{}".format(self.name, setting_name)
