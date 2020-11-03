"""
Expose new-style waffle classes. In the future, these imports will be moved to edx_toggles.toggles. Applications that
want to migrate to the new-style API can do so right now by importing from this module.
"""
# pylint: disable=unused-import
from .internal.setting_toggle import SettingDictToggle, SettingToggle
from .internal.waffle.flag import NonNamespacedWaffleFlag, WaffleFlag
from .internal.waffle.switch import NonNamespacedWaffleSwitch, WaffleSwitch
