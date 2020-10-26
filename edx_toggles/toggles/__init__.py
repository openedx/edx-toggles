"""
Expose public feature toggle API.
"""
from .internal.setting_toggle import SettingDictToggle, SettingToggle
from .internal.waffle.flag import WaffleFlag
from .internal.waffle.legacy import WaffleFlag as LegacyWaffleFlag
from .internal.waffle.legacy import WaffleFlagNamespace as LegacyWaffleFlagNamespace
from .internal.waffle.legacy import WaffleSwitch as LegacyWaffleSwitch
from .internal.waffle.legacy import WaffleSwitchNamespace as LegacyWaffleSwitchNamespace
from .internal.waffle.switch import WaffleSwitch
