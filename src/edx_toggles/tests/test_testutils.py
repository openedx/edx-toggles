"""
Tests for waffle utils test utilities.
"""


import crum
from django.test import TestCase
from django.test.client import RequestFactory
from edx_django_utils.cache import RequestCache

from edx_toggles.toggles import WaffleFlag, WaffleSwitch
from edx_toggles.toggles.testutils import override_waffle_flag, override_waffle_switch


class OverrideWaffleFlagTests(TestCase):
    """
    Tests for the override_waffle_flag decorator/context manager.
    """

    def setUp(self):
        super().setUp()
        flag_name = "test_namespace.test_flag"
        self.waffle_flag = WaffleFlag(  # lint-amnesty, pylint: disable=toggle-missing-annotation
            flag_name, __name__
        )

        request = RequestFactory().request()
        crum.set_current_request(request)
        RequestCache.clear_all_namespaces()

        self.addCleanup(crum.set_current_request, None)
        self.addCleanup(RequestCache.clear_all_namespaces)

    def temporarily_enable_flag(self):
        """
        Temporarily override flag.
        """

        @override_waffle_flag(self.waffle_flag, True)
        def test_func():
            """
            Decorated test function.
            """
            self.assertTrue(self.waffle_flag.is_enabled())

        test_func()

    def test_override_waffle_flag_pre_cached(self):
        # checks and caches the is_enabled value
        self.assertFalse(self.waffle_flag.is_enabled())
        flag_cache = self.waffle_flag.cached_flags()
        self.assertIn(self.waffle_flag.name, flag_cache)

        self.temporarily_enable_flag()

        # test cached flag is restored
        self.assertIn(self.waffle_flag.name, flag_cache)
        self.assertFalse(self.waffle_flag.is_enabled())

    def test_override_waffle_flag_not_pre_cached(self):
        # check that the flag is not yet cached
        flag_cache = self.waffle_flag.cached_flags()
        self.assertNotIn(self.waffle_flag.name, flag_cache)

        self.temporarily_enable_flag()

        # test cache is removed when no longer using decorator/context manager
        self.assertNotIn(self.waffle_flag.name, flag_cache)

    def test_override_waffle_flag_as_context_manager(self):
        self.assertFalse(self.waffle_flag.is_enabled())

        with override_waffle_flag(self.waffle_flag, True):
            self.assertTrue(self.waffle_flag.is_enabled())

        self.assertFalse(self.waffle_flag.is_enabled())

    def test_interlocked_overrides(self):
        waffle_flag1 = self.waffle_flag
        waffle_flag2 = WaffleFlag(  # lint-amnesty, pylint: disable=toggle-missing-annotation
            waffle_flag1.name + "2", __name__
        )
        waffle_flag2.cached_flags()[waffle_flag2.name] = True

        self.assertFalse(waffle_flag1.is_enabled())
        self.assertTrue(waffle_flag2.is_enabled())

        with override_waffle_flag(waffle_flag1, True):
            with override_waffle_flag(waffle_flag2, False):
                self.assertTrue(waffle_flag1.is_enabled())
                self.assertFalse(waffle_flag2.is_enabled())

        self.assertFalse(waffle_flag1.is_enabled())
        self.assertTrue(waffle_flag2.is_enabled())


class OverrideWaffleSwitchTests(TestCase):
    """
    Testt override capabilities for waffle switches.
    """

    def test_override(self):
        switch = WaffleSwitch(  # lint-amnesty, pylint: disable=toggle-missing-annotation
            "test_namespace.test_switch", module_name="testmodule"
        )

        self.assertFalse(switch.is_enabled())
        with override_waffle_switch(switch, active=True):
            self.assertTrue(switch.is_enabled())
        self.assertFalse(switch.is_enabled())
