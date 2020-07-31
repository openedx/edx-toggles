import pytest

from scripts.ida_toggles import IDA
from scripts.toggles import Toggle, ToggleState, ToggleTypes

_WAFFLE_FLAG_DATA = [
    {
        'model': 'WaffleFlag',
        'pk': 1,
        'fields': {
            'everyone': True,
            'name': 'test_waffle_flag',
        },
    },
    {
        'model': 'WaffleFlag',
        'pk': 2,
        'fields': {
            'everyone': True,
            'name': 'test_course_waffle_flag',
        },
    },
]
_COURSE_WAFFLE_FLAG_DATA = [
    {
        'model': 'WaffleUtilsWaffleflagcourseoverridemodel',
        'pk': 1,
        'fields': {
          'waffle_flag': 'test_course_waffle_flag',
          'override_choice': 'on',
          'course_id': 'course-v1:edX+DemoX+Demo_Course'
        }
    },
    {
        'model': 'WaffleUtilsWaffleflagcourseoverridemodel',
        'pk': 2,
        'fields': {
            'waffle_flag': 'test_another_course_waffle_flag',
            'override_choice': 'on',
            'course_id': 'course-v1:edX+DemoX+Demo_Course'
        }
    },
]

@pytest.mark.parametrize('dump_data', [
    (_COURSE_WAFFLE_FLAG_DATA + _WAFFLE_FLAG_DATA),
    (_WAFFLE_FLAG_DATA + _COURSE_WAFFLE_FLAG_DATA),
])
def test_adding_course_waffle_toggle_data(dump_data):
    ida = IDA('my-ida')
    ida._add_toggle_data(dump_data)

    expected_waffle_flag_names = set(['test_waffle_flag'])
    assert len(ida.toggles[ToggleTypes.WAFFLE_FLAG]) == 1
    assert set(ida.toggles[ToggleTypes.WAFFLE_FLAG].keys()) == expected_waffle_flag_names

    expected_course_waffle_flag_names = set(['test_course_waffle_flag', 'test_another_course_waffle_flag'])
    assert len(ida.toggles[ToggleTypes.COURSE_WAFFLE_FLAG]) == 2
    assert set(ida.toggles[ToggleTypes.COURSE_WAFFLE_FLAG].keys()) == expected_course_waffle_flag_names
    course_waffle_flag = ida.toggles[ToggleTypes.COURSE_WAFFLE_FLAG]['test_course_waffle_flag']
    assert course_waffle_flag.state.get_datum('everyone') == 'Yes'
    assert course_waffle_flag.state.get_datum('num_courses_forced_on') == 1


def test_adding_annotation_data():
    ida = IDA('my-ida')
    switch_1 = Toggle('the-first-waffle-switch', ToggleState(ToggleTypes.WAFFLE_SWITCH, {}))
    switch_2 = Toggle('my-sample-switch', ToggleState(ToggleTypes.WAFFLE_SWITCH, {}))
    switch_3 = Toggle('another-sample-switch', ToggleState(ToggleTypes.WAFFLE_SWITCH, {}))
    flag_1 = Toggle('sample-flag', ToggleState(ToggleTypes.WAFFLE_FLAG, {}))
    flag_2 = Toggle('sample-course-waffle-flag', ToggleState(ToggleTypes.WAFFLE_FLAG, {}))
    ida.toggles[ToggleTypes.WAFFLE_SWITCH] = {switch_1.name:switch_1, switch_2.name:switch_2, switch_3.name:switch_3}
    ida.toggles[ToggleTypes.WAFFLE_FLAG] = {flag_1.name:flag_1, flag_2.name:flag_2}
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

    annotation = ida.toggles[ToggleTypes.WAFFLE_SWITCH][switch_2.name].annotations
    assert annotation.report_group_id == 2
    assert annotation.line_range() == (561, 563)
    assert annotation._raw_annotation_data == expected_data

    expected_data = {
        'name': 'not-in-db',
        'implementation': ['WaffleSwitch'],
        'default': True,
    }

    annotation = ida.toggles[ToggleTypes.WAFFLE_SWITCH][expected_data['name']].annotations
    assert annotation.report_group_id == 2
    assert annotation.line_range() == (761, 763)
    assert annotation._raw_annotation_data == expected_data

    # the annotation should turn the WaffleFlag into a CourseWaffleFlag
    expected_data = {
        'name': 'sample-course-waffle-flag',
        'implementation': ['CourseWaffleFlag'],
    }

    annotation = ida.toggles[ToggleTypes.COURSE_WAFFLE_FLAG][expected_data['name']].annotations
    assert annotation.report_group_id == 3
    assert annotation.line_range() == (28, 29)
    assert annotation._raw_annotation_data == expected_data
