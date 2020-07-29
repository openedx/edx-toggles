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

    def add_toggle_data(self, dump_file_path):
        """
        Given the path to a file containing the SQL dump for a
        feature toggle type in an IDA, parse out the information relevant
        to each toggle and add it to this IDA.
        """
        with io.open(dump_file_path) as dump_file:
            try:
                dump_contents = json.loads(dump_file.read())
            except:
                LOGGER.error(
                'Loading json file at: {} failed, check toogle data in file is formated correctly'.format(dump_file_path)
                )
                raise
        self._add_toggle_data(dump_contents)


    def _handle_course_waffle_flag_data(self, row_data):
        """
        Function to handle special case of CourseWaffleFlags.
            # - a CourseWaffleFlag can have multiple overrides (one per course)
            # - each course override is defined by its waffle flag and its course
            # - each course override will have its own row_data that needs to be added
                to its CourseWafleFlag
        """
        toggle_name = row_data['fields']['waffle_flag']
        toggle_data = row_data['fields']
        toggle_type = ToggleTypes.COURSE_WAFFLE_FLAG
        if toggle_type not in self.toggles.keys():
            self.toggles[toggle_type] = {}
        toggle = self.toggles[toggle_type].get(toggle_name, None)
        
        if toggle is None:
            # if a CourseWaffleFlag's course override data was found before its corresponding
            # waffle flag, create an empty toggle to add course override data
            toggle = Toggle(toggle_name, None)
            self.toggles[toggle_type][toggle_name] = toggle

        if toggle.state is None:
            toggle_state = ToggleState(toggle_type, {})
            toggle.state = toggle_state

        # add course override data to toggle output

        # get dict with all course_overrides and add new course to it
        course_overrides = toggle.state.get_datum(
                                "course_overrides",
                                cleaned=False,
                                )

        if not course_overrides:
            course_overrides = {}

        course_overrides[toggle_data["course_id"]] = toggle_data["override_choice"]
        toggle.state.set_datum(
            "course_overrides",
            course_overrides,
            cleaned=False,
        )

        LOGGER.info(
            'Adding override choice for course {} to waffle flag {}'.format(toggle_data["course_id"], toggle.name)
        )

    def _add_toggle_data(self, dump_contents):
        """
        Add toggles state data to toggles
        if toggle already exists, replace its state with this content.
        else: create new toggle with this data
        """
        for row in dump_contents:
            toggle_type = ToggleTypes.get_toggle_type_from_table_name(row['model'])
            if toggle_type == ToggleTypes.COURSE_WAFFLE_FLAG:
                self._handle_course_waffle_flag_data(row)
            else:
                toggle_name = row['fields'].get('name', None)
                toggle_data = row['fields']

                if toggle_type not in self.toggles.keys():
                    self.toggles[toggle_type] = {}

                toggle = self.toggles[toggle_type].get(toggle_name, None)
                if toggle is None:
                    toggle = Toggle(toggle_name, None)
                    self.toggles[toggle_type][toggle_name] = toggle

                toggle_state = ToggleState(toggle_type, toggle_data)
                toggle.state = toggle_state
        LOGGER.info(
            'Finished collecting toggle state for {}'.format(self.name)
        )
        for toggle_type in self.toggles.keys():
            LOGGER.info(
                '- Collected {}: {}'.format(
                    toggle_type, len(self.toggles[toggle_type])
                )
            )



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
                try:
                    annotation_type = ToggleTypes(toggle_annotation._raw_annotation_data['implementation'][0])
                except ValueError:
                    annotation_type = ToggleTypes.UNKNOWN
                    LOGGER.warning(
                    'Name of model not recognized: {}'.format(toggle_annotation._raw_annotation_data['implementation'][0])
                    )
                if annotation_type not in self.toggles.keys():
                    self.toggles[annotation_type] = {}

                if annotation_name in self.toggles[annotation_type].keys():
                    self.toggles[annotation_type][annotation_name].annotations = toggle_annotation
                else:
                    LOGGER.info(
                    'Could not find any matches for {}'.format(annotation_name) +
                    'in the data pulled from the database.'
                    )
                    toggle = Toggle(annotation_name, annotations=toggle_annotation)
                    self.toggles[annotation_type][toggle.name]=toggle


    def _contains(self, toggle_type, toggle_name):
        """
        helper function for determining if a feature toggle is configured
        in an IDA, searching by toggle type and toggle name
        """
        try:
            present = any(
                map(
                    lambda t: t.name == toggle_name,
                    self.toggles[toggle_type]
                )
            )
        except KeyError:
            return False
        return present

    def _get_index(self, toggle_type, toggle_name):
        """
        helper function for getting the index of a given feature toggle
        in the data structure holding all toggles for this IDA
        """
        names = [t.name for t in self.toggles[toggle_type]]
        for index, name in enumerate(names):
            if name == toggle_name:
                return index


def add_toggle_state_to_idas(idas, dump_file_path, idas_configuration=None):
    """
    Given a dictionary of IDAs to consider, and the path to a directory
    containing the SQL dumps for feature toggles in said IDAs, read each dump
    file, parsing and linking it's data into the IDA associated with it.
    """
    ida_name_pattern = re.compile(r'(?P<ida>[a-z]*)_.*json')
    sql_dump_files = [
        f for f in os.listdir(dump_file_path) if ida_name_pattern.search(f)
    ]
    for sql_dump_file in sql_dump_files:
        sql_dump_file_path = os.path.join(dump_file_path, sql_dump_file)
        ida_name = ida_name_pattern.search(sql_dump_file).group('ida')
        if ida_name not in idas:
            idas[ida_name] = IDA(ida_name, idas_configuration.get(ida_name, None))
        LOGGER.info(
            'Collecting toggle_state from {} for {}'.format(
                sql_dump_file_path, ida_name
            )
        )
        idas[ida_name].add_toggle_data(sql_dump_file_path)
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
