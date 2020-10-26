"""
Unit tests for waffle classes.
"""

from django.test import TestCase

from edx_toggles.toggles import WaffleFlag, WaffleSwitch


class WaffleFlagTests(TestCase):
    """
    WaffleFlag tests.
    """

    def test_name_validation(self):
        WaffleFlag("namespaced.name", module_name="module1")
        self.assertRaises(
            ValueError, WaffleFlag, "non_namespaced", module_name="module1"
        )


class WaffleSwitchTest(TestCase):
    """
    WaffleSwitch tests.
    """

    def test_name_validation(self):
        WaffleSwitch("namespaced.name", module_name="module1")
        self.assertRaises(
            ValueError, WaffleSwitch, "non_namespaced", module_name="module1"
        )

    def test_constructor(self):
        switch = WaffleSwitch("namespaced.name", module_name="module1")
        self.assertEqual("module1", switch.module_name)
