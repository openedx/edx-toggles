"""
Unit tests for waffle classes.
"""

from django.test import TestCase

from edx_toggles.toggles import NonNamespacedWaffleFlag, NonNamespacedWaffleSwitch, WaffleFlag, WaffleSwitch
from edx_toggles.toggles.internal.waffle.base import BaseWaffle


class NaiveWaffle(BaseWaffle):
    """
    Simple waffle class that implements a basic instance-tracking mechanism
    """
    _class_instances = set()

    def is_enabled(self):
        return True


class BaseWaffleTest(TestCase):
    """
    Test features of base waffle class.
    """

    def test_constructor(self):
        waffle = NaiveWaffle("namespaced.name", "module1")
        self.assertEqual("namespaced.name", waffle.name)
        self.assertEqual("module1", waffle.module_name)
        self.assertEqual(1, len(NaiveWaffle.get_instances()))


class WaffleFlagTests(TestCase):
    """
    WaffleFlag tests.
    """

    def test_name_validation(self):
        WaffleFlag(  # lint-amnesty, pylint: disable=toggle-missing-annotation
            "namespaced.name", module_name="module1"
        )
        with self.assertRaises(ValueError):
            WaffleFlag(  # lint-amnesty, pylint: disable=toggle-missing-annotation
                "non_namespaced", module_name="module1"
            )

    def test_non_namespaced(self):
        NonNamespacedWaffleFlag(  # lint-amnesty, pylint: disable=toggle-missing-annotation
            "non_namespaced", module_name="module1"
        )


class WaffleSwitchTest(TestCase):
    """
    WaffleSwitch tests.
    """

    def test_name_validation(self):
        WaffleSwitch(  # lint-amnesty, pylint: disable=toggle-missing-annotation
            "namespaced.name", module_name="module1"
        )
        with self.assertRaises(ValueError):
            WaffleSwitch(  # lint-amnesty, pylint: disable=toggle-missing-annotation
                "non_namespaced", module_name="module1"
            )

    def test_non_namespaced(self):
        NonNamespacedWaffleSwitch(  # lint-amnesty, pylint: disable=toggle-missing-annotation
            "non_namespaced", module_name="module1"
        )
