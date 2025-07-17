"""
Test for deeply nested toggle extraction from settings.

This test validates that EVENT_BUS_PRODUCER_CONFIG toggles with deeply nested
dictionary structures are correctly extracted and reported.
"""
import unittest

from edx_toggles.toggles.state.internal.report import _add_setting, get_or_create_toggle_response


class TestDeeplyNestedToggles(unittest.TestCase):
    """
    Test that deeply nested dictionary-based toggles are properly extracted.
    """

    def test_deeply_nested_event_bus_producer_config_extraction(self):
        """
        Test that EVENT_BUS_PRODUCER_CONFIG with deeply nested structure is correctly processed.

        This validates the fix for the bug where deeply nested toggles like:
        EVENT_BUS_PRODUCER_CONFIG['org.openedx.content_authoring.xblock.deleted.v1']
        ['course-authoring-xblock-lifecycle']['enabled']
        were not appearing in the Toggle State Report.

        Based on actual EVENT_BUS_PRODUCER_CONFIG structure from common.py files.
        """        # Mock nested configuration similar to actual EVENT_BUS_PRODUCER_CONFIG from common.py
        test_config = {
            # Simple boolean toggles (common Django settings)
            'ENABLE_CORS_HEADERS': False,
            'ENABLE_THIRD_PARTY_AUTH': True,
            'ENABLE_DJANGO_ADMIN_SITE': True,
            'ENABLE_MASQUERADE': True,
            'ENABLE_TEAMS': True,
            'ENABLE_ENTERPRISE_INTEGRATION': False,
            'ENABLE_ACCOUNT_DELETION': True,
            'BADGES_ENABLED': False,
            'ENABLE_COPPA_COMPLIANCE': False,
            'TPA_AUTOMATIC_LOGOUT_ENABLED': False,

            # Complex nested FEATURES dictionary
            'FEATURES': {
                'ENABLE_COURSEWARE_SEARCH': False,
                'ENABLE_DASHBOARD_SEARCH': True,
                'ENABLE_SPECIAL_EXAMS': False,
                'LICENSING': True,
                'CERTIFICATES_HTML_VIEW': False
            },

            # Deeply nested EVENT_BUS_PRODUCER_CONFIG (based on actual structure from common.py)
            'EVENT_BUS_PRODUCER_CONFIG': {
                # CMS events (content authoring)
                'org.openedx.content_authoring.course.catalog_info.changed.v1': {
                    'course-catalog-info-changed': {
                        'enabled': False,
                        'event_key_field': 'catalog_info.course_key'
                    }
                },
                'org.openedx.content_authoring.xblock.published.v1': {
                    'course-authoring-xblock-lifecycle': {
                        'enabled': True,
                        'event_key_field': 'xblock_info.usage_key'
                    }
                },
                'org.openedx.content_authoring.xblock.deleted.v1': {
                    'course-authoring-xblock-lifecycle': {
                        'enabled': False,
                        'event_key_field': 'xblock_info.usage_key'
                    }
                },
                'org.openedx.content_authoring.xblock.duplicated.v1': {
                    'course-authoring-xblock-lifecycle': {
                        'enabled': True,
                        'event_key_field': 'xblock_info.usage_key'
                    }
                },
                # LMS events (learning)
                'org.openedx.learning.certificate.created.v1': {
                    'learning-certificate-lifecycle': {
                        'enabled': True,
                        'event_key_field': 'certificate.course.course_key'
                    }
                },
                'org.openedx.learning.certificate.revoked.v1': {
                    'learning-certificate-lifecycle': {
                        'enabled': False,
                        'event_key_field': 'certificate.course.course_key'
                    }
                },
                'org.openedx.learning.course.unenrollment.completed.v1': {
                    'course-unenrollment-lifecycle': {
                        'enabled': False,
                        'event_key_field': 'enrollment.course.course_key'
                    }
                },
                'org.openedx.learning.xblock.skill.verified.v1': {
                    'learning-xblock-skill-verified': {
                        'enabled': False,
                        'event_key_field': 'xblock_info.usage_key'
                    }
                },
                'org.openedx.learning.user.course_access_role.added.v1': {
                    'learning-course-access-role-lifecycle': {
                        'enabled': True,
                        'event_key_field': 'course_access_role_data.course_key'
                    }
                },
                'org.openedx.learning.user.course_access_role.removed.v1': {
                    'learning-course-access-role-lifecycle': {
                        'enabled': False,
                        'event_key_field': 'course_access_role_data.course_key'
                    }
                },
                'org.openedx.enterprise.learner_credit_course_enrollment.revoked.v1': {
                    'learner-credit-course-enrollment-lifecycle': {
                        'enabled': True,
                        'event_key_field': 'learner_credit_course_enrollment.uuid'
                    }
                },
                'org.openedx.learning.course.passing.status.updated.v1': {
                    'learning-badges-lifecycle': {
                        'enabled': False,
                        'event_key_field': 'course_passing_status.course.course_key'
                    }
                },
                'org.openedx.learning.ccx.course.passing.status.updated.v1': {
                    'learning-badges-lifecycle': {
                        'enabled': True,
                        'event_key_field': 'course_passing_status.course.ccx_course_key'
                    }
                }
            }
        }

        # Dictionary to collect processed settings
        settings_dict = {}

        # Process the test configuration using the same logic as report.py
        for setting_name, value in test_config.items():
            _add_setting(settings_dict, value, setting_name)

        # Validate that all expected toggles are extracted (25+ toggles total)
        expected_simple_toggles = [
            ('ENABLE_CORS_HEADERS', False),
            ('ENABLE_THIRD_PARTY_AUTH', True),
            ('ENABLE_DJANGO_ADMIN_SITE', True),
            ('ENABLE_MASQUERADE', True),
            ('ENABLE_TEAMS', True),
            ('ENABLE_ENTERPRISE_INTEGRATION', False),
            ('ENABLE_ACCOUNT_DELETION', True),
            ('BADGES_ENABLED', False),
            ('ENABLE_COPPA_COMPLIANCE', False),
            ('TPA_AUTOMATIC_LOGOUT_ENABLED', False),
        ]

        expected_features_toggles = [
            ("FEATURES['ENABLE_COURSEWARE_SEARCH']", False),
            ("FEATURES['ENABLE_DASHBOARD_SEARCH']", True),
            ("FEATURES['ENABLE_SPECIAL_EXAMS']", False),
            ("FEATURES['LICENSING']", True),
            ("FEATURES['CERTIFICATES_HTML_VIEW']", False),
        ]

        expected_event_bus_toggles = [
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.content_authoring.course.catalog_info.changed.v1']"
             "['course-catalog-info-changed']['enabled']", False),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.content_authoring.xblock.published.v1']"
             "['course-authoring-xblock-lifecycle']['enabled']", True),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.content_authoring.xblock.deleted.v1']"
             "['course-authoring-xblock-lifecycle']['enabled']", False),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.content_authoring.xblock.duplicated.v1']"
             "['course-authoring-xblock-lifecycle']['enabled']", True),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.learning.certificate.created.v1']"
             "['learning-certificate-lifecycle']['enabled']", True),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.learning.certificate.revoked.v1']"
             "['learning-certificate-lifecycle']['enabled']", False),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.learning.course.unenrollment.completed.v1']"
             "['course-unenrollment-lifecycle']['enabled']", False),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.learning.xblock.skill.verified.v1']"
             "['learning-xblock-skill-verified']['enabled']", False),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.learning.user.course_access_role.added.v1']"
             "['learning-course-access-role-lifecycle']['enabled']", True),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.learning.user.course_access_role.removed.v1']"
             "['learning-course-access-role-lifecycle']['enabled']", False),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.enterprise.learner_credit_course_enrollment.revoked.v1']"
             "['learner-credit-course-enrollment-lifecycle']['enabled']", True),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.learning.course.passing.status.updated.v1']"
             "['learning-badges-lifecycle']['enabled']", False),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.learning.ccx.course.passing.status.updated.v1']"
             "['learning-badges-lifecycle']['enabled']", True),
        ]

        # Also check for nested non-boolean values (should be ignored)
        expected_non_boolean_keys = [
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.content_authoring.course.catalog_info.changed.v1']"
             "['course-catalog-info-changed']['event_key_field']"),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.content_authoring.xblock.published.v1']"
             "['course-authoring-xblock-lifecycle']['event_key_field']"),
        ]

        # Combine all expected toggles
        all_expected_toggles = expected_simple_toggles + expected_features_toggles + expected_event_bus_toggles

        # Verify each expected toggle is present with correct is_active status
        for toggle_name, expected_status in all_expected_toggles:
            with self.subTest(toggle_name=toggle_name):
                self.assertIn(toggle_name, settings_dict,
                              f"Toggle '{toggle_name}' should be present in settings_dict")

                toggle_data = settings_dict[toggle_name]
                self.assertIn("is_active", toggle_data,
                              f"Toggle '{toggle_name}' should have 'is_active' key")

                self.assertEqual(toggle_data["is_active"], expected_status,
                                 f"Toggle '{toggle_name}' should have is_active={expected_status}")

                # Verify the toggle has the correct name
                self.assertEqual(toggle_data["name"], toggle_name,
                                 f"Toggle should have correct name: {toggle_name}")

        # Verify that non-boolean nested values are NOT extracted
        for non_boolean_key in expected_non_boolean_keys:
            with self.subTest(non_boolean_key=non_boolean_key):
                self.assertNotIn(non_boolean_key, settings_dict,
                                 f"Non-boolean key '{non_boolean_key}' should not be extracted")

        # Verify total number of extracted toggles (should be exactly the boolean ones)
        self.assertEqual(len(settings_dict), len(all_expected_toggles),
                         f"Should extract exactly {len(all_expected_toggles)} boolean toggles")

    def test_mixed_nested_and_simple_toggles(self):
        """
        Test that both simple and deeply nested toggles coexist correctly.
        Validates complex mixed scenarios with various nesting levels.
        """
        test_config = {
            'SIMPLE_BOOLEAN_TOGGLE': True,
            'ANOTHER_SIMPLE_TOGGLE': False,
            'FEATURES': {
                'ENABLE_CORS_HEADERS': False,
                'ENABLE_THIRD_PARTY_AUTH': True,
                'LICENSING': True,
                'NESTED_FEATURE': {
                    'DEEP_SETTING': True,
                    'ANOTHER_DEEP_SETTING': False
                }
            },
            'EVENT_BUS_PRODUCER_CONFIG': {
                'org.openedx.content_authoring.course.catalog_info.changed.v1': {
                    'course-catalog-info-changed': {
                        'enabled': True,
                        'event_key_field': 'catalog_info.course_key'  # This should be ignored (not boolean)
                    }
                },
                'org.openedx.learning.certificate.created.v1': {
                    'learning-certificate-lifecycle': {
                        'enabled': False,
                        'event_key_field': 'certificate.course.course_key'  # This should be ignored (not boolean)
                    }
                }
            },
            'OAUTH2_PROVIDER': {
                'SCOPES': {
                    'read': 'Read access',  # This should be ignored (not boolean)
                    'write': 'Write access'  # This should be ignored (not boolean)
                }
            }
        }

        settings_dict = {}

        # Process the test configuration
        for setting_name, value in test_config.items():
            _add_setting(settings_dict, value, setting_name)

        # Expected boolean toggles that should be extracted
        expected_boolean_toggles = [
            ('SIMPLE_BOOLEAN_TOGGLE', True),
            ('ANOTHER_SIMPLE_TOGGLE', False),
            ("FEATURES['ENABLE_CORS_HEADERS']", False),
            ("FEATURES['ENABLE_THIRD_PARTY_AUTH']", True),
            ("FEATURES['LICENSING']", True),
            ("FEATURES['NESTED_FEATURE']['DEEP_SETTING']", True),
            ("FEATURES['NESTED_FEATURE']['ANOTHER_DEEP_SETTING']", False),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.content_authoring.course.catalog_info.changed.v1']"
             "['course-catalog-info-changed']['enabled']", True),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.learning.certificate.created.v1']"
             "['learning-certificate-lifecycle']['enabled']", False),
        ]

        # Verify all expected boolean toggles
        for toggle_name, expected_status in expected_boolean_toggles:
            with self.subTest(toggle_name=toggle_name):
                self.assertIn(toggle_name, settings_dict,
                              f"Toggle '{toggle_name}' should be present in settings_dict")

                if expected_status:
                    self.assertTrue(settings_dict[toggle_name]['is_active'],
                                    f"Toggle '{toggle_name}' should be active (True)")
                else:
                    self.assertFalse(settings_dict[toggle_name]['is_active'],
                                     f"Toggle '{toggle_name}' should be inactive (False)")

        # Verify that non-boolean values are NOT extracted
        non_boolean_keys = [
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.content_authoring.course.catalog_info.changed.v1']"
             "['course-catalog-info-changed']['event_key_field']"),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.learning.certificate.created.v1']"
             "['learning-certificate-lifecycle']['event_key_field']"),
            "OAUTH2_PROVIDER['SCOPES']['read']",
            "OAUTH2_PROVIDER['SCOPES']['write']",
        ]

        for non_boolean_key in non_boolean_keys:
            with self.subTest(non_boolean_key=non_boolean_key):
                self.assertNotIn(non_boolean_key, settings_dict,
                                 f"Non-boolean key '{non_boolean_key}' should not be extracted")

        # Verify we have exactly the expected number of boolean toggles
        self.assertEqual(len(settings_dict), len(expected_boolean_toggles),
                         f"Should extract exactly {len(expected_boolean_toggles)} boolean toggles")

    def test_get_or_create_toggle_response_functionality(self):
        """
        Test the get_or_create_toggle_response helper function.
        """
        toggles_dict = {}

        # Test creating a new toggle
        toggle_name = "EVENT_BUS_PRODUCER_CONFIG['test.event']['test-topic']['enabled']"
        toggle_response = get_or_create_toggle_response(toggles_dict, toggle_name)

        self.assertIn(toggle_name, toggles_dict)
        self.assertEqual(toggle_response['name'], toggle_name)

        # Test getting existing toggle
        existing_toggle = get_or_create_toggle_response(toggles_dict, toggle_name)
        self.assertIs(existing_toggle, toggle_response)

        # Verify only one toggle exists
        self.assertEqual(len(toggles_dict), 1)

    def test_specific_event_bus_producer_config_toggles(self):
        """
        Test specific EVENT_BUS_PRODUCER_CONFIG toggles with deeply nested structure.

        This test focuses on extracting deeply nested toggles from complex configuration
        structures similar to those found in production environments.
        """
        # Configuration based on typical EVENT_BUS_PRODUCER_CONFIG structure
        test_config = {
            'EVENT_BUS_PRODUCER_CONFIG': {
                'org.openedx.content_authoring.xblock.deleted.v1': {
                    'course-authoring-xblock-lifecycle': {
                        'enabled': False,
                        'event_key_field': 'xblock_info.usage_key'
                    }
                },
                'org.openedx.content_authoring.xblock.duplicated.v1': {
                    'course-authoring-xblock-lifecycle': {
                        'enabled': False,
                        'event_key_field': 'xblock_info.usage_key'
                    }
                },
                'org.openedx.content_authoring.xblock.published.v1': {
                    'course-authoring-xblock-lifecycle': {
                        'enabled': False,
                        'event_key_field': 'xblock_info.usage_key'
                    }
                }
            }
        }

        settings_dict = {}

        # Process the test configuration
        for setting_name, value in test_config.items():
            _add_setting(settings_dict, value, setting_name)

        # Verify a specific deeply nested toggle
        specific_toggle = ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.content_authoring.xblock.deleted.v1']"
                           "['course-authoring-xblock-lifecycle']['enabled']")
        self.assertIn(specific_toggle, settings_dict)
        self.assertFalse(settings_dict[specific_toggle]['is_active'])

        # Verify other related toggles
        expected_toggles = [
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.content_authoring.xblock.deleted.v1']"
             "['course-authoring-xblock-lifecycle']['enabled']", False),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.content_authoring.xblock.duplicated.v1']"
             "['course-authoring-xblock-lifecycle']['enabled']", False),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.content_authoring.xblock.published.v1']"
             "['course-authoring-xblock-lifecycle']['enabled']", False),
        ]

        for toggle_name, expected_status in expected_toggles:
            with self.subTest(toggle_name=toggle_name):
                self.assertIn(toggle_name, settings_dict)
                self.assertEqual(settings_dict[toggle_name]['is_active'], expected_status)

        # Verify non-boolean fields are ignored
        non_boolean_keys = [
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.content_authoring.xblock.deleted.v1']"
             "['course-authoring-xblock-lifecycle']['event_key_field']"),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.content_authoring.xblock.duplicated.v1']"
             "['course-authoring-xblock-lifecycle']['event_key_field']"),
            ("EVENT_BUS_PRODUCER_CONFIG['org.openedx.content_authoring.xblock.published.v1']"
             "['course-authoring-xblock-lifecycle']['event_key_field']"),
        ]

        for non_boolean_key in non_boolean_keys:
            self.assertNotIn(non_boolean_key, settings_dict)


if __name__ == '__main__':
    unittest.main()
