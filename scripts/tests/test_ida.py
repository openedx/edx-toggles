from scripts.ida import IDA
from scripts.toggles import Toggle, ToggleState


def test_adding_toggle_data():
    ida = IDA('my-ida')
    flag_data =[{'fields': {
                'authenticated': False,
                'created': '2017-06-21T16:06:20.833Z',
                'everyone': True,
                'groups': [],
                'languages': '',
                'modified': '2020-04-01T18:31:24.930Z',
                'name': 'enable_client_side_checkout',
                'note': 'This flag determines if the integrated/client-side checkout flow should be enabled.',
                'percent': None,
                'rollout': False,
                'staff': False,
                'superusers': True,
                'testing': False,
                'users': []
                },
            'model': 'waffle.flag',
            'pk': 1
            },
            {'fields': {
                'authenticated': False,
                'created': '2020-04-01T18:28:47.829Z',
                'everyone': None,
                'groups': [],
                'languages': '',
                'modified': '2020-04-01T18:28:47.829Z',
                'name': 'disable_microfrontend_for_basket_page',
                'note': '',
                'percent': None,
                'rollout': False,
                'staff': False,
                'superusers': False,
                'testing': False,
                'users': []
                },
          'model': 'waffle.flag',
          'pk': 2
          }
          ]
    ida._add_toggle_data(flag_data)
    assert len(ida.toggles["WaffleFlag"]) == 2


def test_adding_annotation_data():
    ida = IDA('my-ida')
    switch_1 = Toggle('the-first-waffle-switch', ToggleState('WaffleSwitch', {}))
    switch_2 = Toggle('my-sample-switch', ToggleState('WaffleSwitch', {}))
    switch_3 = Toggle('another-sample-switch', ToggleState('WaffleSwitch', {}))
    flag_1 = Toggle('sample-flag', ToggleState('WaffleFlag', {}))
    ida.toggles['WaffleSwitch'] = [switch_1, switch_2, switch_3]
    ida.toggles['WaffleFlag'] = [flag_1]
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
                'annotation_token': '.. toggle_implementation:',
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
                'annotation_data': ['WaffleSwitch'],
                'annotation_token': '.. toggle_implementation:',
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
                'annotation_data': ['WaffleSwitch'],
                'annotation_token': '.. toggle_implementation:',
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
                'annotation_data': ['WaffleSwitch'],
                'annotation_token': '.. toggle_implementation:',
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
        'name': 'my-sample-switch',
        'implementation': ['WaffleSwitch'],
        'default': True,
    }

    ida._add_annotation_data_to_toggle_state(annotation_groups)

    annotation = ida.toggles['WaffleSwitch'][1].annotations
    assert annotation.report_group_id == 2
    assert annotation.line_range() == (561, 563)
    assert annotation._raw_annotation_data == expected_data

    expected_data = {
        'name': 'not-in-db',
        'implementation': ['WaffleSwitch'],
        'default': True,
    }

    annotation = ida.toggles['WaffleSwitch'][3].annotations
    assert annotation.report_group_id == 2
    assert annotation.line_range() == (761, 763)
    assert annotation._raw_annotation_data == expected_data


