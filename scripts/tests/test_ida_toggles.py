import pytest

from scripts.ida_toggles import IDA
from scripts.toggles import Toggle, ToggleState


def test_adding_annotation_data():
    ida = IDA('my-ida')
    switch_1 = Toggle('the-first-waffle-switch', ToggleState("WaffleSwitch", {}))
    switch_2 = Toggle('my-sample-switch', ToggleState("WaffleSwitch", {}))
    switch_3 = Toggle('another-sample-switch', ToggleState("WaffleSwitch", {}))
    flag_1 = Toggle('sample-flag', ToggleState("WaffleFlag", {}))
    flag_2 = Toggle('sample-course-waffle-flag', ToggleState("WaffleFlag", {}))
    ida.toggles["WaffleSwitch"] = {switch_1.name:switch_1, switch_2.name:switch_2, switch_3.name:switch_3}
    ida.toggles["WaffleFlag"] = {flag_1.name:flag_1, flag_2.name:flag_2}
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
            }, {
                'annotation_data': 'sample-course-waffle-flag',
                'annotation_token': '.. toggle_name:',
                'filename': ' path/to/other/source/code.py',
                'found_by': 'python',
                'line_number': 28,
                'report_group_id': 3,
            }, {
                'annotation_data': ['CourseWaffleFlag'],
                'annotation_token': '.. toggle_implementation:',
                'filename': 'path/to/other/source/code.py',
                'found_by': 'python',
                'line_number': 29,
                'report_group_id': 3,
            },
        ]
    }

    expected_data = {
        'name': 'my-sample-switch',
        'implementation': ['WaffleSwitch'],
        'default': True,
    }

    ida._add_annotation_data_to_toggle_state(annotation_groups)

    annotation = ida.toggles["WaffleSwitch"][switch_2.name].annotations
    assert annotation.report_group_id == 2
    assert annotation.line_range() == (561, 563)
    assert annotation._raw_annotation_data == expected_data

    expected_data = {
        'name': 'not-in-db',
        'implementation': ['WaffleSwitch'],
        'default': True,
    }

    annotation = ida.toggles["WaffleSwitch"][expected_data['name']].annotations
    assert annotation.report_group_id == 2
    assert annotation.line_range() == (761, 763)
    assert annotation._raw_annotation_data == expected_data
