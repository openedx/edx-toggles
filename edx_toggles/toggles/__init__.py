"""
Expose public feature toggle API.
"""
from .internal.setting_toggle import SettingDictToggle, SettingToggle
from .internal.waffle.flag import NonNamespacedWaffleFlag, WaffleFlag
from .internal.waffle.switch import NonNamespacedWaffleSwitch, WaffleSwitch
