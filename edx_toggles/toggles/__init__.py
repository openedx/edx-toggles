"""
Expose public feature toggle API.
"""
from .internal.setting_toggle import SettingDictToggle, SettingToggle
from .internal.waffle.legacy import WaffleFlag, WaffleFlagNamespace, WaffleSwitch, WaffleSwitchNamespace


# Create waffle aliases for forward compatibility
# We create new classes instead of using `LegacyClass = Class` statements
# for better monitoring of legacy class usage.
class LegacyWaffleFlag(WaffleFlag):
    def _get_legacy_custom_attribute_name(self):
        return 'deprecated_compatible_legacy_waffle_class'


class LegacyWaffleFlagNamespace(WaffleFlagNamespace):
    def _get_legacy_custom_attribute_name(self):
        return 'deprecated_compatible_legacy_waffle_class'


class LegacyWaffleSwitch(WaffleSwitch):
    def _get_legacy_custom_attribute_name(self):
        return 'deprecated_compatible_legacy_waffle_class'


class LegacyWaffleSwitchNamespace(WaffleSwitchNamespace):
    def _get_legacy_custom_attribute_name(self):
        return 'deprecated_compatible_legacy_waffle_class'
