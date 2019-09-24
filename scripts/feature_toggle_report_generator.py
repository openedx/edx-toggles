# -*- coding: utf-8 -*-


from __future__ import print_function

import collections
import datetime
import io
import json
import os
import re
import shutil
import sys

import click
import jinja2
import yaml
from atlassian import Confluence
from slugify import slugify


class IDA(object):

    def __init__(self, name):
        self.name = name
        self.toggles = collections.defaultdict(list)
        self.annotation_report_path = None

    def add_toggle_data(self, dump_file_path):
        """
        Given the path to a file containing the SQL dump for a
        feature toggle type in an IDA, parse out the information relevant
        to each toggle and add it to this IDA.
        """
        with io.open(dump_file_path, 'r', encoding='utf-8') as dump_file:
            dump_contents = json.loads(dump_file.read())
        for row in dump_contents:
            toggle_name = row['fields']['name']
            toggle_type = row['model']
            toggle_data = row['fields']
            toggle_state = ToggleState(toggle_type, toggle_data)
            toggle = Toggle(toggle_name, toggle_state)
            self.toggles[toggle_type].append(toggle)

    def add_annotations(self):
        """
        Read the code annotation file specified at `annotation_report_path`,
        linking annotated feature toggles to the feature toggle state
        entries in this IDAs toggle_state dictionary.
        """
        if not self.annotation_report_path:
            return
        with io.open(self.annotation_report_path, 'r') as annotation_file:
            annotation_contents = yaml.safe_load(annotation_file.read())
            self._add_annotation_data_to_toggle_state(annotation_contents)

    def _add_annotation_data_to_toggle_state(self, annotation_file_contents):
        """
        Given the contents of a code annotations report file for this IDA,
        parse through it, adding annotation data to the toggle states already
        identified for this IDA
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

        def clean_value(token_string, value_string):
            if 'toggle_type' in token_string:
                return [re.sub('_', '.', v) for v in value_string]
            else:
                return value_string

        for source_file, annotations in annotation_file_contents.items():

            annotation_groups = group_annotations(annotations)

            for group in annotation_groups:

                group_id = group[0]['report_group_id']
                source_file = group[0]['filename']
                toggle_annotation = ToggleAnnotation(group_id, source_file)

                toggle_annotation.line_numbers = [
                    a['line_number'] for a in group
                ]
                toggle_annotation._raw_annotation_data = {
                    clean_token(a['annotation_token']):
                    clean_value(a['annotation_token'], a['annotation_data'])
                    for a in group
                }

                annotation_name = _get_annotation_data('name', group)
                annotation_type = toggle_annotation._raw_annotation_data[
                    'type'
                ][0]
                if self._contains(annotation_type, annotation_name):
                    i = self._get_index(annotation_type, annotation_name)
                    self.toggles[annotation_type][i].annotations = toggle_annotation
                else:
                    toggle = Toggle(annotation_name, annotations=toggle_annotation)
                    self.toggles[annotation_type].append(toggle)

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


class Toggle(object):
    """
    Represents a feature toggle in an IDA, including the current state of the
    toggle in the database and any additional information defined in the
    source code (marked via `code-annotations`). To account for the case in which
    a feature toggle is not yet annotated or has been removed from the database
    but not the source code, this constructor can handle the case in which
    only one of the above components could be identified.
    """

    def __init__(self, name, state=None, annotations=None):
        self.name = name
        self.state = state
        self.annotations = annotations

    def __str__(self):
        return self.name

    @property
    def state_msg(self):
        if not self.state:
            return "No data found"
        elif self.state.state:
            return "On"
        else:
            return "Off"

    def data_for_template(self, component, data_name):
        if component ==  "state":
            if self.state:
                self.state._prepare_state_data_for_template()
                return self.state._cleaned_state_data[data_name]
            else:
                return 'No data found'
        elif component == "annotation":
            if self.annotations:
                self.annotations._prepare_annotation_data_for_template()
                return self.annotations._cleaned_annotation_data[data_name]
            else:
                return 'No data found'


class ToggleAnnotation(object):
    """
    Represents a group of individual code annotations all referencing the same
    Toggle.
    """

    def __init__(self, report_group_id, source_file):
        self.report_group_id = report_group_id
        self.source_file = source_file
        self.line_numbers = []
        self._raw_annotation_data = {}
        self._cleaned_annotation_data = collections.defaultdict(str)

    def line_range(self):
        lines = sorted(self.line_numbers)
        return lines[0], lines[-1]

    def _prepare_annotation_data_for_template(self):
        for k, v in self._raw_annotation_data.items():
            self._cleaned_annotation_data[k] = v


class ToggleState(object):
    """
    Represents an individual feature toggle within an IDA, including all
    of its state, pulled from the IDA's database.
    """

    def __init__(self, toggle_type, data):
        self.toggle_type = toggle_type
        self._raw_state_data = data
        self._cleaned_state_data = collections.defaultdict(str)

    @property
    def state(self):
        """
        Return the overall state of the toggle. In other words, is it on or off
        """

        def bool_for_null_numbers(n):
            if n == 'null':
                return False
            elif isinstance(n, int):
                return int(n) > 0
            else:
                return False

        if self.toggle_type == 'waffle.switch':
            return self._raw_state_data['active']
        elif self.toggle_type == 'waffle.flag':
            return (
                self._raw_state_data['everyone'] or
                bool_for_null_numbers(self._raw_state_data['percent']) or
                self._raw_state_data['testing'] or
                self._raw_state_data['superusers'] or
                self._raw_state_data['staff'] or
                self._raw_state_data['authenticated'] or
                bool(self._raw_state_data['languages']) or
                self._raw_state_data['rollout']
            )

    def _prepare_state_data_for_template(self):
        def _format_date(date_string):
            datetime_pattern = re.compile(
                r'(?P<date>20\d\d-\d\d-\d\d)T(?P<time>\d\d:\d\d):\d*.*'
            )
            offset_pattern = re.compile(
                r'.*T\d\d:\d\d:\d+.*(?P<offset>[Z+-].*)'
            )
            date = re.search(datetime_pattern, date_string).group('date')
            time = re.search(datetime_pattern, date_string).group('time')
            offset = re.search(offset_pattern, date_string).group('offset')

            if offset == 'Z':
                offset = 'UTC'

            return "{} {} {}".format(date, time, offset)
        def null_or_number(n): return n if isinstance(n, int) else 0

        for k, v in self._raw_state_data.items():

            if k in ['created', 'modified']:
                self._cleaned_state_data[k] = _format_date(v)
            elif k == 'percent':
                self._cleaned_state_data[k] = null_or_number(v)
            elif k == 'languages':
                self._cleaned_state_data[k] = filter(
                    lambda x: x != '', v.split(',')
                )
            else:
                self._cleaned_state_data[k] = v


class Renderer(object):

    def __init__(self, template_dir, report_dir):
        self.jinja_environment = jinja2.Environment(
            autoescape=False,
            loader=jinja2.FileSystemLoader('templates'),
            lstrip_blocks=True,
            trim_blocks=True
        )
        self.report_dir = report_dir
        if not os.path.isdir(report_dir):
            os.mkdir(report_dir)

    def render_file(self, output_file_name, template_name, variables={}):
        file_path = os.path.join(self.report_dir, output_file_name)
        template = self.jinja_environment.get_template(template_name)
        with io.open(file_path, 'w') as output:
            output.write(
                template.render(**variables)
            )

    def render_html_report(self, idas, environment_name):
        report_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.render_file(
            'feature_toggle_report.html', 'report.tpl',
            variables={
                'idas': idas, 'environment': environment_name,
                'report_date': report_date
            }
        )


def add_toggle_state_to_idas(idas, dump_file_path):
    """
    Given a dictionary of IDAs to consider, and the path to a directory
    containing the SQL dumps for feature toggles in said IDAs, read each dump
    file, parsing and linking it's data into the IDA associated with it.
    """
    ida_name_pattern = re.compile(r'(?P<ida>[a-z]*)_.*json')
    sql_dump_files = [
        f for f in os.listdir(dump_file_path) if re.search(ida_name_pattern, f)
    ]
    for sql_dump_file in sql_dump_files:
        sql_dump_file_path = os.path.join(dump_file_path, sql_dump_file)
        ida_name = re.search(ida_name_pattern, sql_dump_file).group('ida')
        idas[ida_name].add_toggle_data(sql_dump_file_path)


def add_toggle_annotations_to_idas(idas, annotation_report_files_path):
    """
    Given a dictionary of IDAs to consider, and the path to a directory
    containing the annotation reports for feature toggles in said IDAs, read
    each file, parsing and linking the annotation data to the toggle state
    data in the IDA.
    """
    ida_name_pattern = re.compile(r'(?P<ida>[a-z]*)-annotations.yml')
    annotation_files = [
        f for f in os.listdir(annotation_report_files_path)
        if re.search(ida_name_pattern, f)
    ]
    for annotation_file in annotation_files:
        annotation_file_path = os.path.join(
            annotation_report_files_path, annotation_file
        )
        ida_name = re.search(ida_name_pattern, annotation_file).group('ida')
        idas[ida_name].annotation_report_path = annotation_file_path
        idas[ida_name].add_annotations()


def create_confluence_connection():
    """
    Make sure the required environment variables are set and return a
    Confluence object, which is used for accessing the Confluence API
    """
    confluence_base_url = _get_env_var('CONFLUENCE_BASE_URL')
    confluence_user_email = _get_env_var('CONFLUENCE_USER_EMAIL')
    confluence_api_token = _get_env_var('CONFLUENCE_API_TOKEN')
    confluence = Confluence(
        confluence_base_url, confluence_user_email, confluence_api_token
    )
    return confluence


def _get_env_var(env_var_name):
    value = os.getenv(env_var_name, None)
    if not value:
        raise NameError(
            'Environment variable {} is not set. This is required to '
            'publish the feature toggle report to Confluence'.format(
                env_var_name
            )
        )
    return value


def publish_to_confluence(confluence, report_path, confluence_space_id,
                          confluence_page_name):
    """
    Publish the HTML report found at `report_path` to confluence space
    `confluence_space_id` and name it `report_name`
    """
    with io.open(report_path, 'r') as report_file:
        feature_toggle_report_html = report_file.read()

    try:
        publish_result = confluence.update_page(
            confluence_space_id, confluence_page_name,
            feature_toggle_report_html
        )
    except TypeError:
        print(
            "Unable to find a space in Confluence with the following "
            "id {}".format(confluence_space_id)
        )
        sys.exit(1)

    if 'statusCode' in publish_result.keys():
        print(
            "Encountered the following error when publishing to Confluence: "
            "{}.".format(publish_result['message'])
        )
        sys.exit(1)



@click.command()
@click.argument(
    'sql_dump_path',
    type=click.Path(exists=True),
)
@click.argument(
    'annotation_report_path',
    type=click.Path(exists=True),
)
@click.argument(
    'output_path', default="feature_toggle_report",
)
@click.argument(
    'environment_name', required=True
)
def main(sql_dump_path, annotation_report_path, output_path, environment_name):
    ida_names = ['credentials', 'ecommerce', 'discovery', 'lms']
    idas = {name: IDA(name) for name in ida_names}
    add_toggle_state_to_idas(idas, sql_dump_path)
    add_toggle_annotations_to_idas(idas, annotation_report_path)
    renderer = Renderer('templates', output_path)
    renderer.render_html_report(idas, environment_name)
    confluence = create_confluence_connection()
    confluence_space_id = _get_env_var('CONFLUENCE_SPACE_ID')
    confluence_page_name = _get_env_var('CONFLUENCE_PAGE_NAME')
    publish_to_confluence(
        confluence, 'reports/feature_toggle_report.html', confluence_space_id,
        confluence_page_name
    )


if __name__ == '__main__':
    main()
