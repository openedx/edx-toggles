import pytest
from scripts.toggles import ToggleState

@pytest.mark.skip(reason="TODO(jinder): figure out datetime to json conversion")
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


