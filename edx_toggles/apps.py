"""
edx_toggles Django application initialization.
"""
from django.apps import AppConfig


class TogglesConfig(AppConfig):
    """
    Configuration for the edx_toggles Django application.
    """

    name = 'edx_toggles'

    # Class attribute that configures and enables this app as a Plugin App.
    plugin_app = {
        'url_config': {
            'lms.djangoapp': {
                'namespace': 'toggles',
            },
        },
    }
