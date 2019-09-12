from ..feature_toggle_report_generator import (
    IDA, Toggle, ToggleState
)


def test_adding_annoation_links():
    ida = IDA('my-ida')
    switch_1 = Toggle('the-first-waflle-switch', ToggleState('waffle.switch', {}))
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
                'line_number': 461,
                'report_group_id': 2,
            }, {
                'annotation_data': ['waffle.switch'],
                'annotation_token': '.. toggle_type:',
                'filename': 'path/to/source/code.py',
                'found_by': 'python',
                'line_number': 462,
                'report_group_id': 2
            }, {
                'annotation_data': True,
                'annotation_token': '.. toggle_default:',
                'filename': 'path/to/source/code.py',
                'found_by': 'python',
                'line_number': 463,
                'report_group_id': 2
            }
        ],
        'path/to/other/source/code.py': [
            {
                'annotation_data': 'another-sample-switch',
                'annotation_token': '.. toggle_name:',
                'filename': ' path/to/other/source/code.py',
                'found_by': 'python',
                'line_number': 461,
                'report_group_id': 1,
            }, {
                'annotation_data': ['waffle.switch'],
                'annotation_token': '.. toggle_type:',
                'filename': 'path/to/other/source/code.py',
                'found_by': 'python',
                'line_number': 462,
                'report_group_id': 1
            }, {
                'annotation_data': True,
                'annotation_token': '.. toggle_default:',
                'filename': 'path/to/other/source/code.py',
                'found_by': 'python',
                'line_number': 463,
                'report_group_id': 1
            }
        ]
    }

    ida._add_annotation_links_to_toggle_state(annotation_groups)

    link = 'my-ida/index.rst#index-rst-path-to-source-code-py-2'
    assert ida.toggles['waffle.switch'][1].state.annotation_link == link


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
