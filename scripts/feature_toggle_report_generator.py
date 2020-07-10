# -*- coding: utf-8 -*-

import datetime
import io
import os
import re

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
    '--show-state', is_flag=True,
)
def main(data_path, output_path, show_state):
    data_dirs = [path for path in os.listdir(data_path) if os.path.join(data_path, path) and "_env" in path]
    annotation_dir = os.path.join(data_path, "annotations")
    data_paths = []
    # if there are dirs in data_path, each dir is assumed to hold data for a different env
    if data_dirs:
        data_paths.extend([os.path.join(data_path, dir_name) for dir_name in data_dirs])
    else:
        # if no dirs in data_path, this run in for single env
        data_paths.append(data_path)

    total_info = {}
    env_name_pattern = re.compile(r'(?P<env>[a-z0-9]*)_env')
    for env_data_path in data_paths:
        env_name = re.search(env_name_pattern, env_data_path).group('env')
        # TODO(jinder): this should not be hardcoded, can get this name from file name convention
        ida_names = ['lms']
        total_info[env_name] = {}
        if show_state:
            add_toggle_state_to_idas(total_info[env_name], env_data_path)
        add_toggle_annotations_to_idas(total_info[env_name], annotation_dir)
    renderer = CsvRenderer()
    renderer.render_csv_report(total_info, os.path.join(output_path, "report.csv"))


if __name__ == '__main__':
    main()
