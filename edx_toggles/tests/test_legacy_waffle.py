"""
Unit tests for legacy waffle objects. These tests should be moved to test_waffle.py once the legacy classes are removed.
"""
from django.test import TestCase

from edx_toggles.toggles.internal.waffle.legacy import (
    LegacyWaffleFlag,
    LegacyWaffleFlagNamespace,
    LegacyWaffleSwitch,
    LegacyWaffleSwitchNamespace
)


class TestLegacyWaffleSwitch(TestCase):
    """
    Tests the LegacyWaffleSwitch.
    """

    def test_default_value(self):
        namespace = LegacyWaffleSwitchNamespace("test_namespace")
        switch = LegacyWaffleSwitch(  # lint-amnesty, pylint: disable=toggle-missing-annotation
            namespace, "test_switch_name", module_name="module1"
        )
        self.assertFalse(switch.is_enabled())
        self.assertFalse(namespace.is_enabled("test_switch_name"))

    # pylint: disable=protected-access
    def test_set_request_cache_with_short_name(self):
        namespace = LegacyWaffleSwitchNamespace("test_namespace")
        switch = LegacyWaffleSwitch(  # lint-amnesty, pylint: disable=toggle-missing-annotation
            namespace, "test_switch_name", module_name="module1"
        )
        self.assertFalse(switch._cached_switches.get("test_namespace.test_switch_name"))
        namespace.set_request_cache_with_short_name("test_switch_name", True)
        self.assertTrue(switch._cached_switches.get("test_namespace.test_switch_name"))
        self.assertTrue(switch.is_enabled())
        namespace.set_request_cache_with_short_name("test_switch_name", False)
        self.assertFalse(switch._cached_switches.get("test_namespace.test_switch_name"))
        self.assertFalse(switch.is_enabled())


class TestLegacyWaffleFlag(TestCase):
    """
    Legacy waffle flag tests.
    """

    def test_default_value(self):
        namespace = LegacyWaffleFlagNamespace("namespace")
        flag = LegacyWaffleFlag(namespace, "flag")  # lint-amnesty, pylint: disable=toggle-missing-annotation
        self.assertFalse(flag.is_enabled())
        self.assertFalse(namespace.is_flag_active("flag"))
