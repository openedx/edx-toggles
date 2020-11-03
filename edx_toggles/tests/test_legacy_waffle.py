"""
Unit tests for legacy waffle objects.
"""
from django.test import TestCase

from edx_toggles.toggles.internal.waffle.legacy import (
    WaffleFlag,
    WaffleFlagNamespace,
    WaffleSwitch,
    WaffleSwitchNamespace,
)


class TestWaffleSwitch(TestCase):
    """
    Tests the WaffleSwitch.
    """

    NAMESPACE_NAME = "test_namespace"
    WAFFLE_SWITCH_NAME = "test_switch_name"
    TEST_NAMESPACE = WaffleSwitchNamespace(NAMESPACE_NAME)
    WAFFLE_SWITCH = WaffleSwitch(TEST_NAMESPACE, WAFFLE_SWITCH_NAME, __name__)

    def test_namespaced_switch_name(self):
        """
        Verify namespaced_switch_name returns the correct namespace switch name
        """
        expected = self.NAMESPACE_NAME + "." + self.WAFFLE_SWITCH_NAME
        actual = self.WAFFLE_SWITCH.namespaced_switch_name
        self.assertEqual(actual, expected)


class TestWaffleFlag(TestCase):
    """
    Legacy waffle flag tests.
    """

    def test_namespaced_flag_name(self):
        namespace = WaffleFlagNamespace("namespace")
        flag = WaffleFlag(namespace, "flag")
        self.assertEqual("namespace.flag", flag.namespaced_flag_name)

    def test_default_value(self):
        namespace = WaffleFlagNamespace("namespace")
        flag = WaffleFlag(namespace, "flag")
        self.assertFalse(flag.is_enabled())
        self.assertFalse(namespace.is_flag_active("flag"))
