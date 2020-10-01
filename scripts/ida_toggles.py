"""
Code to represent an independently deployed application and its associated toggles.

"""

import collections
import io
import json
import logging
import os
import re
import yaml
from enum import Enum

from scripts.toggles import Toggle, ToggleAnnotation, ToggleState, ToggleTypes

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class IDA(object):
    """ Represents an independently deployed application. """

    def __init__(self, name, configuration=None):
        self.name = name
        self.toggles = collections.defaultdict(dict)
        self.annotation_report_path = None
        self.configuration = configuration if configuration else {}

    def get_toggles_data_summary(self):
        data = []
        for toggle_type, toggles in self.toggles.items():
            for toggle_name, toggle in toggles.items():
                data.append(toggle.get_summary_report())
        return data

    def get_full_report(self):
        data = []
        for toggle_type, toggles in self.toggles.items():
            for toggle_name, toggle in toggles.items():
                data.extend(toggle.get_full_reports())
        return data

    def add_toggle_data(self, state_data_path, env_name):
        """
        Given the path to a file containing the SQL dump for a
        feature toggle type in an IDA, parse out the information relevant
        to each toggle and add it to this IDA.
        """
        with io.open(state_data_path) as data_file:
            try:
                state_data = json.loads(data_file.read())
            except:
                LOGGER.error(
                'Loading json file at: {} failed, check toggle data in file is formatted correctly'.format(state_data_path)
                )
                raise
        self._add_toggle_data(state_data, env_name)

    def _add_toggle_data(self, state_data, env_name):
        """
        Add toggles state data to toggles
        if toggle already exists, replace its state with this content.
        else: create new toggle with this data
        Arguments:
            state_data: dict with structure: {toggle_types_1:[toggle_dicts], toggle_types_2:[toggles_dicts]}
        """
        for toggle_type, toggles_data in state_data.items():
            toggle_type = ToggleTypes.get_internally_consistent_toggle_type(toggle_type)

            for toggle_data in toggles_data:
                toggle_name = toggle_data.get('name')
                toggle = self._get_or_create_toggle_and_state(toggle_type, toggle_name, toggle_data, env_name)

        LOGGER.info(
            'Finished collecting toggle state for {}'.format(self.name)
        )
        for toggle_type in self.toggles.keys():
            LOGGER.info(
                '- Collected {}: {}'.format(
                    toggle_type, len(self.toggles[toggle_type])
                )
            )

    def _get_or_create_toggle_and_state(self, toggle_type, toggle_name, toggle_state_data=None, env_name=None):
        """
        Gets a toggle and updates its state or creates a toggle and its state,
        and returns the toggle.
        """
        toggle_type = ToggleTypes.get_internally_consistent_toggle_type(toggle_type)
        toggle = self.toggles[toggle_type].get(toggle_name, None)

        if toggle:
            if toggle_state_data:
                toggle_state = ToggleState(toggle_type, toggle_state_data, env_name=env_name)
                toggle.add_state(toggle_state)
        else:
            if toggle_state_data is None:
                toggle_state = None
            else:
                toggle_state = ToggleState(toggle_type, toggle_state_data, env_name=env_name)
            toggle = Toggle(toggle_name, toggle_state, ida_name=self.name)
            self.toggles[toggle_type][toggle_name] = toggle

        return toggle

    def add_annotations(self):
        """
        Read the code annotation file specified at `annotation_report_path`,
        adding the annotations to the Toggles in this IDA.
        """
        if not self.annotation_report_path:
            return
        with io.open(self.annotation_report_path, 'r') as annotation_file:
            annotation_contents = yaml.safe_load(annotation_file.read())
            self._add_annotation_data_to_toggle_state(annotation_contents)
        LOGGER.info(
            'Finished collecting annotations for {}'.format(self.name)
        )
        for toggle_type in self.toggles.keys():
            # count number of toggles that have annotations
            annotation_count = len(
                [value.annotations for _, value in self.toggles[toggle_type].items() if value.annotations]
                )

            LOGGER.info(
                '- Collected annotated {}: {}'.format(
                    toggle_type, annotation_count
                )
            )

    def _add_annotation_data_to_toggle_state(self, annotation_file_contents):
        """
        Given the contents of a code annotations report file for this IDA,
        parse through it, adding annotation data to the toggles in this IDA.
        If a toggle has already been added, add the annotation data. If not,
        create a new Toggle for this IDA and add the annotation data.
        """
        def _get_annotation_data(annotation_token, annotations):
            """
            Given a list of annotations (dictionaries), get the
            `annotation_data` associated with a specified `annotation_token`.
            """
            token = '.. toggle_{}:'.format(annotation_token)
            data = None
            for annotation in annotations:
                if annotation['annotation_token'] == token:
                    data = annotation['annotation_data']
                    if type(data) == list:
                        data = data[0]
                    break
            return data

        def group_annotations(annotations):
            """
            Given a list of code annotations, split them into individual lists
            based on their 'report_group_id'.
            """
            groups = []
            for i in set(a['report_group_id'] for a in annotations):
                group = list(filter(
                    lambda a: a['report_group_id'] == i, annotations
                ))
                groups.append(group)
            return groups

        def clean_token(token_string):
            return re.search(r'.. toggle_(.*):', token_string).group(1)

        for source_file, annotations in annotation_file_contents.items():
            LOGGER.info(
                'Collecting annotation groups for {} in {}'.format(
                    self.name, source_file
                )
            )

            annotation_groups = group_annotations(annotations)
            LOGGER.info(
                'Collected annotation groups: {}'.format(len(annotation_groups))
            )

            for group in annotation_groups:

                group_id = group[0]['report_group_id']
                source_file = group[0]['filename']
                toggle_annotation = ToggleAnnotation(group_id, source_file)

                toggle_annotation.line_numbers = [
                    a['line_number'] for a in group
                ]

                # its useful to have a quick link to go to see the annotations in the code base
                if 'github_url' in self.configuration.keys():
                    #TODO: Replace `master` with a git hash so the links will work even if the files change.
                    url = "{github_repo_url}/blob/master/{source_file}".format(
                        github_repo_url=self.configuration['github_url'],
                        source_file= source_file,
                        )
                    if toggle_annotation.line_numbers:
                        line_num = "#L{first_line_num}-L{last_line_num}".format(
                            first_line_num=toggle_annotation.line_numbers[0],
                            last_line_num=toggle_annotation.line_numbers[-1],
                        )
                        url = url + line_num
                    toggle_annotation.github_url = url

                toggle_annotation._raw_annotation_data = {
                    clean_token(a['annotation_token']): a['annotation_data']
                    for a in group
                    if 'documented' not in a['annotation_token']
                }
                if not toggle_annotation._raw_annotation_data:
                    continue

                annotation_name = _get_annotation_data('name', group)
                annotation_type = toggle_annotation._raw_annotation_data['implementation'][0]

                toggle = self._get_or_create_toggle_and_state(annotation_type, annotation_name)
                toggle.annotations = toggle_annotation


def add_toggle_state_to_idas(idas, state_data_path, idas_configuration=None, env_name=None):
    """
    Given a dictionary of IDAs to consider, and the path to a directory
    containing the SQL dumps for feature toggles in said IDAs, read each dump
    file, parsing and linking it's data into the IDA associated with it.
    """
    ida_name_pattern = re.compile(r'(?P<ida>[a-z]*)_.*json')
    sql_dump_files = [
        f for f in os.listdir(state_data_path) if ida_name_pattern.search(f)
    ]
    for sql_dump_file in sql_dump_files:
        sql_dump_file_path = os.path.join(state_data_path, sql_dump_file)
        ida_name = ida_name_pattern.search(sql_dump_file).group('ida')
        if ida_name not in idas:
            idas[ida_name] = IDA(ida_name, idas_configuration.get(ida_name, None))
        LOGGER.info(
            'Collecting toggle_state from {} for {}'.format(
                sql_dump_file_path, ida_name
            )
        )
        idas[ida_name].add_toggle_data(sql_dump_file_path, env_name=env_name)
        LOGGER.info('=' * 100)


def add_toggle_annotations_to_idas(idas, annotation_report_files_path, idas_configuration=None):
    """
    Given a dictionary of IDAs to consider, and the path to a directory
    containing the annotation reports for feature toggles in said IDAs, read
    each file, parsing and linking the annotation data to the toggle state
    data in the IDA.
    """
    ida_name_pattern = re.compile(r'(?P<ida>[a-z]*)[-_]annotations.ya?ml')
    annotation_files = [
        f for f in os.listdir(annotation_report_files_path)
        if ida_name_pattern.search(f)
    ]
    for annotation_file in annotation_files:
        annotation_file_path = os.path.join(
            annotation_report_files_path, annotation_file
        )
        ida_name = ida_name_pattern.search(annotation_file).group('ida')
        if ida_name not in idas:
            idas[ida_name] = IDA(ida_name, idas_configuration.get(ida_name, None))
        LOGGER.info(
            'Collecting annotations from {} for {}'.format(
                annotation_file, ida_name
            )
        )
        idas[ida_name].annotation_report_path = annotation_file_path
        idas[ida_name].add_annotations()
        LOGGER.info('=' * 100)
