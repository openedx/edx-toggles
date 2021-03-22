"""
Tests for waffle utils views.
"""
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from waffle.testutils import override_switch

from edx_toggles.toggles import SettingDictToggle, SettingToggle, WaffleFlag
from edx_toggles.toggles.state import ToggleStateReport
from edx_toggles.toggles.testutils import override_waffle_flag

TEST_WAFFLE_FLAG = WaffleFlag("test.flag", __name__)  # lint-amnesty, pylint: disable=toggle-missing-annotation


class ToggleStateTests(TestCase):
    """
    Unit tests for the toggle state report.
    """
    @override_waffle_flag(TEST_WAFFLE_FLAG, True)
    def test_response_with_waffle_flag(self):
        report = ToggleStateReport().as_dict()
        self.assertIn("waffle_flags", report)
        self.assertTrue(report["waffle_flags"])
        waffle_names = [waffle["name"] for waffle in report["waffle_flags"]]
        self.assertIn("test.flag", waffle_names)

    @override_switch("test.switch", True)
    def test_response_with_waffle_switch(self):
        report = ToggleStateReport().as_dict()
        self.assertIn("waffle_switches", report)
        self.assertTrue(report["waffle_switches"])
        waffle_names = [waffle["name"] for waffle in report["waffle_switches"]]
        self.assertIn("test.switch", waffle_names)

    def test_response_with_setting_toggle(self):
        _toggle = SettingToggle("MYSETTING", default=False, module_name="module1")
        with override_settings(MYSETTING=True):
            report = ToggleStateReport().as_dict()

        self.assertIn(
            {
                "name": "MYSETTING",
                "is_active": True,
                "module": "module1",
                "class": "SettingToggle",
            },
            report["django_settings"],
        )

    def test_response_with_existing_setting_dict_toggle(self):
        _toggle = SettingDictToggle("FEATURES", "MYFEATURE", default=True, module_name="module1")
        report = ToggleStateReport().as_dict()
        self.assertIn(
            {
                "name": "FEATURES['MYFEATURE']",
                "is_active": True,
                "module": "module1",
                "class": "SettingDictToggle",
            },
            report["django_settings"],
        )

    def test_response_with_new_setting_dict_toggle(self):
        _toggle = SettingDictToggle(
            "CUSTOM_FEATURES", "MYSETTING", default=False, module_name="module1"
        )
        with override_settings(CUSTOM_FEATURES={"MYSETTING": True}):
            report = ToggleStateReport().as_dict()

        setting_dict = {toggle["name"]: toggle for toggle in report["django_settings"]}

        self.assertEqual(
            {
                "name": "CUSTOM_FEATURES['MYSETTING']",
                "is_active": True,
                "module": "module1",
                "class": "SettingDictToggle",
            },
            setting_dict["CUSTOM_FEATURES['MYSETTING']"],
        )

    def test_setting_overridden_by_setting_toggle(self):
        _toggle2 = SettingToggle("MYSETTING2", module_name="module1")
        _toggle3 = SettingDictToggle("MYDICT", "MYSETTING3", module_name="module1")
        with override_settings(
            MYSETTING1=True, MYSETTING2=False, MYDICT={"MYSETTING3": False}
        ):
            # Need to pre-load settings, otherwise they are not picked up by the view
            self.assertTrue(settings.MYSETTING1)
            report = ToggleStateReport().as_dict()

        setting_dict = {toggle["name"]: toggle for toggle in report["django_settings"]}

        # Check that Django settings for which a SettingToggle exists have both the correct is_active and class values
        self.assertTrue(setting_dict["MYSETTING1"]["is_active"])
        self.assertNotIn("class", setting_dict["MYSETTING1"])
        self.assertFalse(setting_dict["MYSETTING2"]["is_active"])
        self.assertEqual("SettingToggle", setting_dict["MYSETTING2"]["class"])
        self.assertFalse(setting_dict["MYDICT['MYSETTING3']"]["is_active"])
        self.assertEqual(
            "SettingDictToggle", setting_dict["MYDICT['MYSETTING3']"]["class"]
        )

    def test_no_duplicate_setting_toggle(self):
        _toggle1 = SettingToggle("MYSETTING1", module_name="module1")
        _toggle2 = SettingDictToggle("MYDICT", "MYSETTING2", module_name="module1")
        with override_settings(MYSETTING1=True, MYDICT={"MYSETTING2": False}):
            report = ToggleStateReport().as_dict()

        # Check there are no duplicate setting/toggle
        response_toggles_1 = [
            toggle
            for toggle in report["django_settings"]
            if toggle["name"] == "MYSETTING1"
        ]
        response_toggles_2 = [
            toggle
            for toggle in report["django_settings"]
            if toggle["name"] == "MYDICT['MYSETTING2']"
        ]
        self.assertEqual(1, len(response_toggles_1))
        self.assertEqual(1, len(response_toggles_2))

    def test_code_owners_without_module_information(self):
        # Create a waffle flag without any associated module_name
        waffle_flag = WaffleFlag(  # lint-amnesty, pylint: disable=toggle-missing-annotation
            "test.flag2", module_name="module1"
        )
        report = ToggleStateReport().as_dict()

        result = [
            flag for flag in report["waffle_flags"] if flag["name"] == waffle_flag.name
        ][0]
        self.assertNotIn("code_owner", result)
