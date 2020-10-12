"""
This module includes all code related to feature toggles. Remember to import publicly available classes and functions
in __init__.py.
"""

from abc import ABC
from weakref import WeakSet

from django.conf import settings


class BaseToggle(ABC):
    """
    This abstract base class exposes the basic API required by toggle classes. Toggle instances are tracked in the
    ``_class_instances`` class attribute, which is exposed via the ``get_instaaces`` class method.
    """

    _class_instances = WeakSet()

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


class SettingToggle(BaseToggle):
    """
    Feature toggle based on a Django setting value. Use as follows:

        MY_FEATURE = SettingToggle("SETTING_NAME", default=False, module_name=__name__)
    """
    def is_enabled(self):
        return bool(getattr(settings, self.name, self.default))


class SettingDictToggle(BaseToggle):
    """
    Feature toggle based on the value of a key in a Django setting ``dict``. Use as follows:

        MY_FEATURE = SettingDictToggle("SETTING_NAME", "key" default=False, module_name=__name__)
    """
    def __init__(self, name, key, default=False, module_name=""):
        super().__init__(name, default=default, module_name=module_name)
        self.key = key

    def is_enabled(self):
        setting_dict = getattr(settings, self.name, {})
        return bool(setting_dict.get(self.key, self.default))
