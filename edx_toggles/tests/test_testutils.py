"""
Tests for waffle utils test utilities.
"""


import crum
from django.test import TestCase
from django.test.client import RequestFactory
from edx_django_utils.cache import RequestCache

from edx_toggles.toggles import WaffleFlag, WaffleFlagNamespace
from edx_toggles.toggles.testutils import override_waffle_flag


class OverrideWaffleFlagTests(TestCase):
    """
    Tests for the override_waffle_flag decorator/context manager.
    """

    def setUp(self):
        super(OverrideWaffleFlagTests, self).setUp()
        namespace_name = "test_namespace"
        flag_name = "test_flag"
        self.namespaced_flag_name = namespace_name + "." + flag_name
        self.namespace = WaffleFlagNamespace(namespace_name)
        self.waffle_flag = WaffleFlag(self.namespace, flag_name)

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
        # pylint: disable=protected-access
        flag_cache = self.namespace._cached_flags
        self.assertIn(self.namespaced_flag_name, flag_cache)

        self.temporarily_enable_flag()

        # test cached flag is restored
        self.assertIn(self.namespaced_flag_name, flag_cache)
        self.assertFalse(self.waffle_flag.is_enabled())

    def test_override_waffle_flag_not_pre_cached(self):
        # check that the flag is not yet cached
        # pylint: disable=protected-access
        flag_cache = self.namespace._cached_flags
        self.assertNotIn(self.namespaced_flag_name, flag_cache)

        self.temporarily_enable_flag()

        # test cache is removed when no longer using decorator/context manager
        self.assertNotIn(self.namespaced_flag_name, flag_cache)

    def test_override_waffle_flag_as_context_manager(self):
        self.assertFalse(self.waffle_flag.is_enabled())

        with override_waffle_flag(self.waffle_flag, True):
            self.assertTrue(self.waffle_flag.is_enabled())

        self.assertFalse(self.waffle_flag.is_enabled())

    def test_interlocked_overrides(self):
        waffle_flag1 = self.waffle_flag
        waffle_flag2 = WaffleFlag(self.namespace, waffle_flag1.flag_name + "2")
        # pylint: disable=protected-access
        self.namespace._cached_flags[waffle_flag2.namespaced_flag_name] = True

        self.assertFalse(waffle_flag1.is_enabled())
        self.assertTrue(waffle_flag2.is_enabled())

        with override_waffle_flag(waffle_flag1, True):
            with override_waffle_flag(waffle_flag2, False):
                self.assertTrue(waffle_flag1.is_enabled())
                self.assertFalse(waffle_flag2.is_enabled())

        self.assertFalse(waffle_flag1.is_enabled())
        self.assertTrue(waffle_flag2.is_enabled())
