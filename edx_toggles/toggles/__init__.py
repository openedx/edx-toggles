"""
Expose public feature toggle API.
"""
from .internal.setting_toggle import SettingDictToggle, SettingToggle
from .internal.waffle.flag import NonNamespacedWaffleFlag, WaffleFlag
from .internal.waffle.legacy import WaffleFlag as _LegacyWaffleFlag
from .internal.waffle.legacy import WaffleFlagNamespace as _LegacyWaffleFlagNamespace
from .internal.waffle.legacy import WaffleSwitch as _LegacyWaffleSwitch
from .internal.waffle.legacy import WaffleSwitchNamespace as _LegacyWaffleSwitchNamespace
from .internal.waffle.switch import NonNamespacedWaffleSwitch, WaffleSwitch


# We create new classes instead of simply importing the legacy classes
# for better monitoring of legacy class usage.
class LegacyWaffleFlag(_LegacyWaffleFlag):
    def _get_legacy_custom_attribute_name(self):
        return "deprecated_compatible_legacy_waffle_class"


class LegacyWaffleFlagNamespace(_LegacyWaffleFlagNamespace):
    def _get_legacy_custom_attribute_name(self):
        return "deprecated_compatible_legacy_waffle_class"


class LegacyWaffleSwitch(_LegacyWaffleSwitch):
    def _get_legacy_custom_attribute_name(self):
        return "deprecated_compatible_legacy_waffle_class"


class LegacyWaffleSwitchNamespace(_LegacyWaffleSwitchNamespace):
    def _get_legacy_custom_attribute_name(self):
        return "deprecated_compatible_legacy_waffle_class"
