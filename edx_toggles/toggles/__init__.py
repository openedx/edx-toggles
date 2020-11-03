"""
Expose public feature toggle API.
"""
from .internal.setting_toggle import SettingDictToggle, SettingToggle
from .internal.waffle.legacy import WaffleFlag, WaffleFlagNamespace, WaffleSwitch, WaffleSwitchNamespace

# Create waffle aliases for forward compatibility
LegacyWaffleFlag = WaffleFlag
LegacyWaffleFlagNamespace = WaffleFlagNamespace
LegacyWaffleSwitch = WaffleSwitch
LegacyWaffleSwitchNamespace = WaffleSwitchNamespace
