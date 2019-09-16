# -*- coding: utf-8 -*-

import collections
import datetime
import io
import json
import os
import re
import shutil

import click
import jinja2
import yaml
from slugify import slugify

from code_annotations.base import AnnotationConfig
from code_annotations.generate_docs import ReportRenderer


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
            return re.search(r'.. (.*):', token_string).group(1)

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
                toggle_annotation.data = {
                    clean_token(a['annotation_token']):
                    clean_value(a['annotation_token'], a['annotation_data'])
                    for a in group
                }

                annotation_name = toggle_annotation.data['toggle_name']
                annotation_type = toggle_annotation.data['toggle_type'][0]

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


class ToggleAnnotation(object):
    """
    Represents a group of individual code annotations all referencing the same
    Toggle.
    """

    def __init__(self, report_group_id, source_file):
        self.report_group_id = report_group_id
        self.source_file = source_file
        self.line_numbers = []
        self.annotation_data = {}

    def line_range(self):
        lines = sorted(self.line_numbers)
        return lines[0], lines[-1]


class ToggleState(object):
    """
    Represents an individual feature toggle within an IDA, including all
    of its state, pulled from the IDA's database.
    """

    def __init__(self, toggle_type, data):
        self.toggle_type = toggle_type
        self.data = data
        self._annotation_link = None

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
            return self.data['active']
        elif self.toggle_type == 'waffle.flag':
            return (
                self.data['everyone'] or
                bool_for_null_numbers(self.data['percent']) or
                self.data['testing'] or
                self.data['superusers'] or
                self.data['staff'] or
                self.data['authenticated'] or
                bool(self.data['languages']) or
                self.data['rollout']
            )

    @property
    def state_msg(self):
        if self.state:
            return "On"
        else:
            return "Off"

    @property
    def annotation_link(self):
        if self._annotation_link:
            return self._annotation_link
        else:
            return "No source definition found in annotation report"

    @property
    def data_for_template(self):
        """
        Return a dictionary of this Toggle's data for the report, formatted for
        readability
        """

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

        template_data = {}
        if self.toggle_type == 'waffle.switch':
            template_data['note'] = self.data['note']
            template_data['creation_date'] = _format_date(self.data['created'])
            template_data['last_modified_date'] = _format_date(
                self.data['modified']
            )
        elif self.toggle_type == 'waffle.flag':
            template_data['note'] = self.data['note']
            template_data['creation_date'] = _format_date(self.data['created'])
            template_data['last_modified_date'] = _format_date(
                self.data['modified']
            )
            template_data['everyone'] = self.data['everyone']
            template_data['percent'] = null_or_number(self.data['percent'])
            template_data['testing'] = self.data['testing']
            template_data['superusers'] = self.data['superusers']
            template_data['staff'] = self.data['staff']
            template_data['authenticated'] = self.data['authenticated']
            template_data['languages'] = filter(
                lambda x: x != '', self.data['languages'].split(',')
            )
            template_data['rollout'] = self.data['rollout']

        return template_data

    def set_annotation_link(self, ida_name, source_file, group_id):
        slug = slugify('index-rst-{}-{}'.format(source_file, group_id))
        link = '{}/index.rst#{}'.format(ida_name, slug)
        self._annotation_link = link


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

    def render_report(self, report_data):
        """
        Generate the entire feature toggle report
        """
        self.render_file(
            'index.rst', 'index.tpl',
            variables={'idas': report_data.keys()}
        )
        for ida_name, ida_data in report_data.items():
            self.render_file(
                '{}.rst'.format(ida_name), 'ida_base.tpl',
                variables={'ida': ida_data}
            )
            self.render_file(
                '{}-feature-toggle-state.rst'.format(ida_name), 'ida.tpl',
                variables={'ida': ida_data}
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


def generate_code_annotation_docs(idas, output_path):
    """
    For each IDA, copy its annotation report into the `output_path` directory
    and generate code annotation docs. Finally, move this set of docs into
    its own subdirectory
    """
    if os.path.isdir(output_path):
        shutil.rmtree(output_path)
    os.mkdir(output_path)
    for ida_name, ida in idas.items():
        if not ida.annotation_report_path:
            continue
        temp_annotation_report = os.path.join(
            'reports', os.path.basename(ida.annotation_report_path)
        )
        shutil.copyfile(ida.annotation_report_path, temp_annotation_report)
        annotation_config = AnnotationConfig('feature_annotations.yml', 0)
        with io.open(temp_annotation_report, 'r') as annotation_report:
            report_files = (annotation_report, )
            annotation_renderer = ReportRenderer(annotation_config, report_files)
            annotation_renderer.render()
        ida_doc_path = os.path.join(output_path, ida_name)
        os.mkdir(ida_doc_path)
        for rst in [f for f in os.listdir(output_path) if f.endswith('rst')]:
            src = os.path.join(output_path, rst)
            target = os.path.join(ida_doc_path, rst)
            shutil.copyfile(src, target)
            os.remove(src)
        os.remove(temp_annotation_report)


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
def main(sql_dump_path, annotation_report_path, output_path):
    ida_names = ['credentials', 'ecommerce', 'discovery', 'lms']
    idas = {name: IDA(name) for name in ida_names}
    add_toggle_state_to_idas(idas, sql_dump_path)
    add_toggle_annotations_to_idas(idas, annotation_report_path)
    # generate_code_annotation_docs(idas, output_path)
    renderer = Renderer('templates', output_path)
    renderer.render_report(idas)


if __name__ == '__main__':
    main()
