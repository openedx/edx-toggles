# -*- coding: utf-8 -*-

import datetime
import io
import os

import click
import jinja2

from scripts.ida import IDA, add_toggle_state_to_idas, add_toggle_annotations_to_idas
from scripts.renderers import CsvRenderer


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
    renderer = CsvRenderer()
    renderer.render_flag_csv_report(idas)
    renderer.render_switch_csv_report(idas)


if __name__ == '__main__':
    main()
