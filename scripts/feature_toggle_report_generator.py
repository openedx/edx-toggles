# -*- coding: utf-8 -*-

import collections
import datetime
import io
import itertools
import json
import os
import re
import shutil

import click
import jinja2
import yaml
from slugify import slugify

from code_annotations.cli import generate_docs


class IDA(object):

    def __init__(self, name):
        self.name = name
        self.toggle_states = collections.defaultdict(list)
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
            toggle = ToggleState(toggle_name, toggle_type, toggle_data)
            self.toggle_states[toggle_type].append(toggle)

    def link_toggles_to_annotations(self):
        """
        Read the code annotation file specified at `annotation_report_path`,
        linking annotated feature toggles to the feature toggle state
        entries in this IDAs toggle_state dictionary.
        """
        if not self.annotation_report_path:
            return
        with io.open(self.annotation_report_path, 'r') as annotation_file:
            annotation_contents = yaml.safe_load(annotation_file.read())
            self._add_annotation_links_to_toggle_state(annotation_contents)

    def _add_annotation_links_to_toggle_state(self, annotation_file_contents):
        """
        Given the contents of a code annotations report file for this IDA,
        parse through it, adding the slufigied rst anchor link to the
        annotated definition of each toggle it finds to the toggles
        configured for this IDA.
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
            for i in itertools.count(1):
                group = list(filter(
                    lambda a: a['report_group_id'] == i, annotations
                ))
                if len(group) == 0:
                    break
                groups.append(group)
            return groups

        for source_file, annotations in annotation_file_contents.items():
            annotation_groups = group_annotations(annotations)

            for group in annotation_groups:
                annotation_name = _get_annotation_data('name', group)
                annotation_group_id = group[0]['report_group_id']
                annotation_type = _get_annotation_data('type', group)
                annotation_type = re.sub('_', '.', annotation_type)

                if self._contains(annotation_type, annotation_name):
                    i = self._get_index(annotation_type, annotation_name)
                    self.toggle_states[annotation_type][i].set_annotation_link(
                        self.name, source_file, annotation_group_id
                    )

    def _contains(self, toggle_type, toggle_name):
        """
        helper function for determining if a feature toggle is configured
        in an IDA, searching by toggle type and toggle name
        """
        try:
            present = any(
                map(
                    lambda t: t.name == toggle_name,
                    self.toggle_states[toggle_type]
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
        names = [t.name for t in self.toggle_states[toggle_type]]
        for index, name in enumerate(names):
            if name == toggle_name:
                return index


class ToggleState(object):
    """
    Represents an individual feature toggle within an IDA, including all
    of its state, pulled from the IDA's database.
    """

    def __init__(self, name, toggle_type, data):
        self.name = name
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
            else:
                return int(n) > 0

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
                r'(?P<date>20\d\d-\d\d-\d\d)T(?P<time>\d\d:\d\d):\d*\.\d*.*'
            )
            offset_pattern = re.compile(
                r'.*T\d\d:\d\d:\d\d.\d+(?P<offset>[Z+-].*)'
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
        slug = slugify('{}-{}'.format(source_file, group_id))
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


def link_annotation_reports_to_idas(idas, annotation_report_files_path):
    """
    Given a dictionary of IDAs to consider, and the path to a directory
    containing the annotation reporst for feature toggles in said IDAs, read
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
    link_annotation_reports_to_idas(idas, annotation_report_path)
    renderer = Renderer('templates', 'reports')
    renderer.render_report(idas)


if __name__ == '__main__':
    main()
