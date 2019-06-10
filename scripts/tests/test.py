from ..feature_toggle_report_generator import (
    IDA, ToggleState
)


def test_adding_annoation_links():
    ida = IDA('my-ida')
    switch_1 = ToggleState('the-first-waflle-switch', 'waffle.switch', {})
    switch_2 = ToggleState('my-sample-switch', 'waffle.switch', {})
    switch_3 = ToggleState('another-sample-switch', 'waffle.switch', {})
    flag_1 = ToggleState('sample-flag', 'waffle.flag', {})
    ida.toggle_states['waffle.switch'] = [switch_1, switch_2, switch_3]
    ida.toggle_states['waffle.flag'] = [flag_1]

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

    link = 'my-ida/index.rst#path-to-source-code-py-2'
    assert ida.toggle_states['waffle.switch'][1].annotation_link == link
