# -*- coding: utf-8 -*-

import datetime
import io
import itertools
import os
import re

import click
import jinja2
import yaml
from slugify import slugify

from code_annotations.cli import generate_docs


class Ida(object):

    def __init__(self, name):
        self.name = name
        self.toggle_states = {}
        self.annotation_report_path = None

    def add_toggle_data(self, dump_file_path):
        """
        Given the path to a file containing the SQL dump for a
        feature toggle type in an Ida, parse out the information relevant
        to each toggle and add it to this Ida.
        """
        with io.open(dump_file_path, 'r', encoding='utf-8') as dump_file:
            dump_contents = yaml.safe_load(dump_file.read())
        for row in dump_contents:
            toggle_name = row['fields']['name']
            toggle_type = row['model']
            toggle_data = row['fields']
            toggle = ToggleState(toggle_name, toggle_type, toggle_data)
            if toggle_type in self.toggle_states.keys():
                self.toggle_states[toggle_type].append(toggle)
            else:
                self.toggle_states[toggle_type] = [toggle]

    def link_toggles_to_annotations(self):
        """
        Read the code annotation file specified at `annotation_report_path`,
        linking annotated feature toggles to the feature toggle state
        entries in this Idas toggle_state dictionary.
        """
        if not self.annotation_report_path:
            return
        with io.open(self.annotation_report_path, 'r', encoding='utf-8') as annotation_file:
            annotation_contents = yaml.safe_load(annotation_file.read())

    def toggles_by_type(self, toggle_type):
        """
        Return a list of feature toggles for this IDA, given a type
        of toggle (i.e. waffle_switch). Although you can just index
        the dictionary directly, this method will handle the case when a
        key is not present, as it will be called from Jinja templates
        """
        try:
            return self.toggle_states[toggle_type]
        except KeyError:
            return []

    def add_annotation_links_to_toggle_state(self, annotation_file_contents):
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
                annotation_type = re.sub('_', '\.', annotation_type)

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
    Represents an individual feature toggle within an Ida, including all
    of its state, pulled from the Ida's database.
    """

    def __init__(self, name, toggle_type, data):
        self.name = name
        self.toggle_type = toggle_type
        self.data = data
        self.annotation_link = None

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
    def data_for_template(self):
        """
        Return a dictionary of this Toggle's data for the report, formatted for
        readability
        """
        null_or_number = lambda n: n if isinstance(n, int) else 0
        template_data = {}
        date_template = '%Y-%m-%d %H:%M'
        if self.toggle_type == 'waffle.switch':
            template_data['note'] = self.data['note']
            template_data['creation_date'] = datetime.datetime.strftime(
                self.data['created'], date_template
            )
            template_data['last_modified_date'] = datetime.datetime.strftime(
                self.data['modified'], date_template
            )
        elif self.toggle_type == 'waffle.flag':
            template_data['note'] = self.data['note']
            template_data['creation_date'] = datetime.datetime.strftime(
                self.data['created'], date_template
            )
            template_data['last_modified_date'] = datetime.datetime.strftime(
                self.data['modified'], date_template
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
        self.annotation_link = link


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
    Given a dictionary of Idas to consider, and the path to a directory
    containing the SQL dumps for feature toggles in said Idas, read each dump
    file, parsing and linking it's data into the Ida associated with it.
    """
    ida_name_pattern = re.compile(r'(?P<ida>[a-z]*)_.*yml')
    sql_dump_files = [
        f for f in os.listdir(dump_file_path) if re.search(ida_name_pattern, f)
    ]
    for sql_dump_file in sql_dump_files:
        sql_dump_file_path = os.path.join(dump_file_path, sql_dump_file)
        ida_name = re.search(ida_name_pattern, sql_dump_file).group('ida')
        idas[ida_name].add_toggle_data(sql_dump_file_path)


def link_annotation_reports_to_idas(idas, annotation_report_files_path):
    """
    Given a dictionary of Idas to consider, and the path to a directory
    containing the annotation reporst for feature toggles in said Idas, read
    each file, parsing and linking the annotation data to the toggle state
    data in the Ida.
    """
    ida_name_pattern = re.compile(r'(?P<ida>[a-z]*)_annotations.yml')
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
    idas = {name: Ida(name) for name in ida_names}
    add_toggle_state_to_idas(idas, sql_dump_path)
    link_annotation_reports_to_idas(idas, annotation_report_path)
    renderer = Renderer('templates', 'reports')
    renderer.render_report(idas)


if __name__ == '__main__':
    main()
