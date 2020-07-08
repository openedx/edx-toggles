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
    'data_path',
    type=click.Path(exists=True),
)
@click.argument(
    'output_path', default="feature_toggle_report",
)
@click.option(
    '--show_state', is_flag=True,
)
def main(data_path, output_path, show_state):
    data_dirs = [dir_path for path in os.listdir(data_path) if os.path.isdir(path) and "_env" in path]
    annotation_dir = os.path.joint(data_path, "annotations")
    data_paths = []
    # if there are dirs in data_path, each dir is assumed to hold data for a different env
    if data_dirs:
        data_paths.extend([os.path.join(data_path, dir_name) for dir_name in data_dirs])
    else:
        # if no dirs in data_path, this run in for single env
        data_paths.append(data_path)

    total_info = {}
    for env_data_path in data_paths:
        # TODO(jinder): this should not be hardcoded, can get this name from file name convention
        ida_names = ['lms']
        total_info[env_data_path] = {name: IDA(name) for name in ida_names}
        if show_state:
            add_toggle_state_to_idas(total_info[env_data_path], os.path.join(env_data_path, "sql_dump"))
        add_toggle_annotations_to_idas(total_info[env_data_path], annotation_dir)
    renderer = CsvRenderer()
    renderer.render_flag_csv_report(total_info, os.path.dirname(env_data_path))
    renderer.render_switch_csv_report(total_info, os.path.dirname(env_data_path))


if __name__ == '__main__':
    main()
