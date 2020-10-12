"""
Setting-derived feature toggles
"""
from weakref import WeakSet

from django.conf import settings

from .base import BaseToggle


class SettingToggle(BaseToggle):
    """
    Feature toggle based on a Django setting value. Use as follows:

        MY_FEATURE = SettingToggle("SETTING_NAME", default=False, module_name=__name__)
    """

    _class_instances = WeakSet()

    def is_enabled(self):
        return bool(getattr(settings, self.name, self.default))


class SettingDictToggle(BaseToggle):
    """
    Feature toggle based on the value of a key in a Django setting ``dict``. Use as follows:

        MY_FEATURE = SettingDictToggle("SETTING_NAME", "key" default=False, module_name=__name__)
    """

    _class_instances = WeakSet()

    def __init__(self, name, key, default=False, module_name=""):
        super().__init__(name, default=default, module_name=module_name)
        self.key = key

    def is_enabled(self):
        setting_dict = getattr(settings, self.name, {})
        return bool(setting_dict.get(self.key, self.default))
