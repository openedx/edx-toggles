"""
Unit tests for waffle classes.
"""

from unittest.mock import patch

from django.test import TestCase

from edx_toggles.toggles import NonNamespacedWaffleFlag, NonNamespacedWaffleSwitch, WaffleFlag, WaffleSwitch
from edx_toggles.toggles.internal.waffle.base import BaseWaffle
from edx_toggles.toggles.internal.waffle.base import logger as base_logger


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

    def test_no_blank_space_in_name(self):
        with patch.object(base_logger, "error") as mock_logger_error:
            NaiveWaffle("namespaced.name ", "module")
            mock_logger_error.assert_called_with(
                "NaiveWaffle instance name should not include a blank space prefix or suffix: 'namespaced.name '"
            )
        with patch.object(base_logger, "error") as mock_logger_error:
            NaiveWaffle(" namespaced.name", "module")
            mock_logger_error.assert_called_with(
                "NaiveWaffle instance name should not include a blank space prefix or suffix: ' namespaced.name'"
            )


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
