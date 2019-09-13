from ..feature_toggle_report_generator import (
    IDA, Toggle, ToggleState
)


def test_adding_annotation_data():
    ida = IDA('my-ida')
    switch_1 = Toggle('the-first-waffle-switch', ToggleState('waffle.switch', {}))
    switch_2 = Toggle('my-sample-switch', ToggleState('waffle.switch', {}))
    switch_3 = Toggle('another-sample-switch', ToggleState('waffle.switch', {}))
    flag_1 = Toggle('sample-flag', ToggleState('waffle.flag', {}))
    ida.toggles['waffle.switch'] = [switch_1, switch_2, switch_3]
    ida.toggles['waffle.flag'] = [flag_1]
    annotation_groups = {
        'path/to/source/code.py': [
            # A feature toggle annotation, but not one we care about linking
            {
                'annotation_data': 'my-sample-config-model',
                'annotation_token': '.. toggle_name:',
                'filename': ' path/to/source/code.py',
                'found_by': 'python',
                'line_number': 461,
                'report_group_id': 1,
            }, {
                'annotation_data': ['ConfigurationModel'],
                'annotation_token': '.. toggle_type:',
                'filename': 'path/to/source/code.py',
                'found_by': 'python',
                'line_number': 462,
                'report_group_id': 1
            }, {
                'annotation_data': True,
                'annotation_token': '.. toggle_default:',
                'filename': 'path/to/source/code.py',
                'found_by': 'python',
                'line_number': 463,
                'report_group_id': 1
            },
            # A waffle switch to be indexed
            {
                'annotation_data': 'my-sample-switch',
                'annotation_token': '.. toggle_name:',
                'filename': ' path/to/source/code.py',
                'found_by': 'python',
                'line_number': 561,
                'report_group_id': 2,
            }, {
                'annotation_data': ['waffle.switch'],
                'annotation_token': '.. toggle_type:',
                'filename': 'path/to/source/code.py',
                'found_by': 'python',
                'line_number': 562,
                'report_group_id': 2
            }, {
                'annotation_data': True,
                'annotation_token': '.. toggle_default:',
                'filename': 'path/to/source/code.py',
                'found_by': 'python',
                'line_number': 563,
                'report_group_id': 2
            }
        ],
        'path/to/other/source/code.py': [
            {
                'annotation_data': 'another-sample-switch',
                'annotation_token': '.. toggle_name:',
                'filename': ' path/to/other/source/code.py',
                'found_by': 'python',
                'line_number': 661,
                'report_group_id': 1,
            }, {
                'annotation_data': ['waffle.switch'],
                'annotation_token': '.. toggle_type:',
                'filename': 'path/to/other/source/code.py',
                'found_by': 'python',
                'line_number': 662,
                'report_group_id': 1
            }, {
                'annotation_data': True,
                'annotation_token': '.. toggle_default:',
                'filename': 'path/to/other/source/code.py',
                'found_by': 'python',
                'line_number': 663,
                'report_group_id': 1
            }, {
                'annotation_data': 'not-in-db',
                'annotation_token': '.. toggle_name:',
                'filename': ' path/to/other/source/code.py',
                'found_by': 'python',
                'line_number': 761,
                'report_group_id': 2,
            }, {
                'annotation_data': ['waffle.switch'],
                'annotation_token': '.. toggle_type:',
                'filename': 'path/to/other/source/code.py',
                'found_by': 'python',
                'line_number': 762,
                'report_group_id': 2
            }, {
                'annotation_data': True,
                'annotation_token': '.. toggle_default:',
                'filename': 'path/to/other/source/code.py',
                'found_by': 'python',
                'line_number': 763,
                'report_group_id': 2
            }
        ]
    }

    expected_data = {
        'toggle_name': 'my-sample-switch',
        'toggle_type': ['waffle.switch'],
        'toggle_default': True,
    }

    ida._add_annotation_data_to_toggle_state(annotation_groups)

    annotation = ida.toggles['waffle.switch'][1].annotations
    assert annotation.report_group_id == 2
    assert annotation.line_range() == (561, 563)
    assert annotation.data == expected_data

    expected_data = {
        'toggle_name': 'not-in-db',
        'toggle_type': ['waffle.switch'],
        'toggle_default': True,
    }

    annotation = ida.toggles['waffle.switch'][3].annotations
    assert annotation.report_group_id == 2
    assert annotation.line_range() == (761, 763)
    assert annotation.data == expected_data


def test_toggle_date_format():
    switch = ToggleState(
        'waffle.switch',
        {
            'note': 'blank',
            'created': '2019-04-23T14:21:44.765727+00:30',
            'modified': '2019-04-23T14:21:44.765738Z'
        }
    )
    creation_timestamp = '2019-04-23 14:21 +00:30'
    modified_timestamp = '2019-04-23 14:21 UTC'
    assert switch.data_for_template['creation_date'] == creation_timestamp
    assert switch.data_for_template['last_modified_date'] == modified_timestamp


def test_toggle_state():
    flag = ToggleState(
        'waffle.flag',
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
            'rollout': False
        }
    )
    assert not flag.state
