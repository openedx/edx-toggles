"""
Unit tests for waffle classes.
"""

from django.test import TestCase

from edx_toggles.toggles import WaffleFlag


class WaffleFlagTests(TestCase):
    def test_name_validation(self):
        WaffleFlag("namespaced.name", module_name="module1")
        self.assertRaises(
            ValueError, WaffleFlag, "non_namespaced", module_name="module1"
        )
