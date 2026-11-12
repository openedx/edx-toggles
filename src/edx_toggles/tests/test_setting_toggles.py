#!/usr/bin/env python
"""
Unit tests that cover feature toggle functionalities.
"""

from django.test import TestCase

from edx_toggles import toggles


class SettingToggleTests(TestCase):
    """
    SettingToggle tests
    """

    def test_toggle_for_absent_setting(self):
        toggle1 = toggles.SettingToggle("NAME1", True)
        toggle2 = toggles.SettingToggle("NAME1", False)

        self.assertTrue(toggle1.is_enabled())
        self.assertFalse(toggle2.is_enabled())

    def test_toggle_for_present_setting(self):
        toggle1 = toggles.SettingToggle("NAME1", True)
        toggle2 = toggles.SettingToggle("NAME1", False)

        with self.settings(NAME1=42):
            self.assertTrue(toggle1.is_enabled())
            self.assertTrue(toggle2.is_enabled())

    def test_is_enabled_is_bool(self):
        toggle1 = toggles.SettingToggle("NAME1", 42)
        self.assertIs(True, toggle1.is_enabled())


class SettingDictToggleTests(TestCase):
    """
    SettingDictToggle tests
    """

    def test_toggle_for_absent_setting(self):
        toggle1 = toggles.SettingDictToggle(
            "NAME1", "key1", True, module_name="module1"
        )
        toggle2 = toggles.SettingDictToggle(
            "NAME2", "key2", False, module_name="module1"
        )
        self.assertTrue(toggle1.is_enabled())
        self.assertFalse(toggle2.is_enabled())

    def test_toggle_for_present_setting(self):
        toggle1 = toggles.SettingDictToggle("NAME1", "key1", True)

        with self.settings(NAME1={"key1": False}):
            self.assertFalse(toggle1.is_enabled())

    def test_toggle_for_present_setting_without_key(self):
        toggle1 = toggles.SettingDictToggle("NAME1", "key2", False)

        with self.settings(NAME1={"key1": True}):
            self.assertFalse(toggle1.is_enabled())


class ToggleInstancesTests(TestCase):
    """
    Class instance-tracking tests
    """

    def test_created_instances(self):
        toggle1 = toggles.SettingToggle("NAME1", default=False, module_name="module1")
        toggle2 = toggles.SettingToggle("NAME2", default=False, module_name="module2")
        instances = toggles.SettingToggle.get_instances()
        self.assertEqual(2, len(instances))
        self.assertEqual(toggle1.module_name, instances[0].module_name)
        self.assertEqual(toggle2.module_name, instances[1].module_name)

    def test_deleted_instances_are_not_listed(self):
        toggles.SettingToggle("NAME1", default=False, module_name="module1")
        instances = toggles.SettingToggle.get_instances()
        self.assertEqual([], instances)
