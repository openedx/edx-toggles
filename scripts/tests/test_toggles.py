from scripts.ida_toggles import IDA
from scripts.toggles import Toggle, ToggleState

def test_toggle_date_format():
    switch = ToggleState(
        'WaffleSwitch',
        {
            'note': 'blank',
            'created': '2019-04-23T14:21:44.765727+00:30',
            'modified': '2019-04-23T14:21:44.765738Z'
        }
    )
    creation_timestamp = '2019-04-23 14:21 +00:30'
    modified_timestamp = '2019-04-23 14:21 UTC'
    switch._prepare_state_data()
    assert switch._cleaned_state_data['created'] == creation_timestamp
    assert switch._cleaned_state_data['modified'] == modified_timestamp


def test_toggle_state():
    flag = ToggleState(
        'WaffleFlag',
        {
            'note': 'blank',
            'created': '2019-04-23 14:21:44.765727+00:00',
            'modified': '2019-04-23 14:21:44.765738+00:00',
            'everyone': False,
            'percent': 'null',
            'testing': False,
            'superusers': False,
            'staff': False,
            'authenticated': False,
            'languages': False,
            'users': ['NULL'],
            'groups': []
        }
    )
    assert not flag.state
