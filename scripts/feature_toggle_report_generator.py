# -*- coding: utf-8 -*-

import datetime
import io
import os

import click
import jinja2

from scripts.ida import IDA, add_toggle_state_to_idas, add_toggle_annotations_to_idas
from scripts.renderers import HtmlRenderer



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
    renderer = HtmlRenderer('templates', output_path)
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
