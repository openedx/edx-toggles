# -*- coding: utf-8 -*-

import datetime
import io
import logging
import os

import click
import jinja2

from .ida import IDA

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


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

    def render_html_report(self, idas, environment_name, show_state=True):
        report_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        report_path = 'feature_toggle_report.html'
        LOGGER.info('Attempting to render HTML report')
        self.render_file(
            report_path, 'report.tpl',
            variables={
                'idas': idas, 'environment': environment_name,
                'report_date': report_date,
                'show_state': show_state,

            }
        )
        LOGGER.info(
            'Succesfully rendered HTML report to {}'.format(report_path)
        )


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
@click.option(
    '--show_state', is_flag=True,
)
@click.option('--publish', is_flag=True)
def main(sql_dump_path, annotation_report_path, output_path, environment_name, show_state, publish):
    ida_names = ['lms']
    idas = {name: IDA(name) for name in ida_names}
    if show_state:
        add_toggle_state_to_idas(idas, sql_dump_path)
    add_toggle_annotations_to_idas(idas, annotation_report_path)
    renderer = Renderer('templates', output_path)
    renderer.render_html_report(idas, environment_name, show_state)
    if publish:
        confluence = create_confluence_connection()
        confluence_space_id = _get_env_var('CONFLUENCE_SPACE_ID')
        confluence_page_name = _get_env_var('CONFLUENCE_PAGE_NAME')
        publish_to_confluence(
            confluence, 'reports/feature_toggle_report.html', confluence_space_id,
            confluence_page_name
        )


if __name__ == '__main__':
    main()
