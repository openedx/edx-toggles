
from ..feature_toggle_report_generator import (
    Ida, ToggleState
)


def test_waffle_flag_state():
    null_percent_flag = ToggleState(
        'my_flag', 'waffle.flag',
        {
            'everyone': False,
            'percent': 'null',
            'testing': False,
            'superusers': False,
            'staff': False,
            'authenticated': False,
            'languages': '',
            'rollout': False,
            'note': 'blah',
            'created': None,
            'modified': None,
            'groups': [],
            'users': []
        }
    )
    language_flag = ToggleState(
        'my_flag', 'waffle.flag',
        {
            'everyone': False,
            'percent': 'null',
            'testing': False,
            'superusers': False,
            'staff': False,
            'authenticated': False,
            'languages': 'en-US',
            'rollout': False,
            'note': 'blah',
            'created': None,
            'modified': None,
            'groups': [],
            'users': []
        }
    )
    assert not null_percent_flag.state
    assert language_flag.state


def test_template_data():
    null_percent_flag = ToggleState(
        'my_flag', 'waffle.flag',
        {
            'everyone': False,
            'percent': 'null',
            'testing': False,
            'superusers': False,
            'staff': False,
            'authenticated': False,
            'languages': 'en-US,es-ES',
            'rollout': False,
            'note': 'blah',
            'created': '2019-04-23 14:21:44.765727+00:00',
            'modified': '2019-04-23 14:21:44.765738+00:00',
            'groups': [],
            'users': []
        }
    )
    toggle_data = null_percent_flag.data_for_template
    assert toggle_data['percent'] == 0
    assert toggle_data['languages'] == ['en-US', 'es-ES']
    assert toggle['created'] == '2019-04-23 14:21'
