"""
Unit tests for legacy waffle objects.
"""
from django.test import TestCase

from edx_toggles.toggles.internal.waffle.legacy import (
    WaffleFlag,
    WaffleFlagNamespace,
    WaffleSwitch,
    WaffleSwitchNamespace
)


class TestWaffleSwitch(TestCase):
    """
    Tests the WaffleSwitch.
    """

    def test_namespaced_switch_name(self):
        """
        Verify namespaced_switch_name returns the correct namespace switch name
        """
        namespace = WaffleSwitchNamespace("test_namespace")
        switch = WaffleSwitch(namespace, "test_switch_name", __name__)
        self.assertEqual(
            "test_namespace.test_switch_name", switch.namespaced_switch_name
        )

    def test_default_value(self):
        namespace = WaffleSwitchNamespace("test_namespace")
        switch = WaffleSwitch(namespace, "test_switch_name", module_name="module1")
        self.assertFalse(switch.is_enabled())
        self.assertFalse(namespace.is_enabled("test_switch_name"))

    def test_get_set_cache_for_request(self):
        namespace = WaffleSwitchNamespace("test_namespace")
        switch = WaffleSwitch(namespace, "test_switch_name", module_name="module1")
        self.assertFalse(
            namespace.get_request_cache_with_short_name("test_switch_name")
        )
        namespace.set_request_cache_with_short_name("test_switch_name", True)
        self.assertTrue(namespace.get_request_cache_with_short_name("test_switch_name"))
        self.assertTrue(switch.is_enabled())
        namespace.set_request_cache_with_short_name("test_switch_name", False)
        self.assertFalse(
            namespace.get_request_cache_with_short_name("test_switch_name")
        )


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
