"""
Expose public feature toggle API.
"""
from .internal.base import BaseNamespace  # TODO remove this
from .internal.setting_toggle import SettingDictToggle, SettingToggle
from .internal.waffle import WaffleSwitch, WaffleSwitchNamespace
