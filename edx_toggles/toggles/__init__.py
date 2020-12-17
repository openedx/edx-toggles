"""
Expose public feature toggle API.
"""
from .internal.setting_toggle import SettingDictToggle, SettingToggle
from .internal.waffle.legacy import WaffleFlag, WaffleFlagNamespace, WaffleSwitch, WaffleSwitchNamespace


# Create waffle aliases for forward compatibility
# We create new classes instead of using `LegacyClass = Class` statements
# for better monitoring of legacy class usage.
class LegacyWaffleFlag(WaffleFlag):
    pass


class LegacyWaffleFlagNamespace(WaffleFlagNamespace):
    pass


class LegacyWaffleSwitch(WaffleSwitch):
    pass


class LegacyWaffleSwitchNamespace(WaffleSwitchNamespace):
    pass
