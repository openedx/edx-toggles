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
    'annotations_dir',
    type=click.Path(exists=True),
)
@click.argument(
    'toggle_data_dir',
    type=click.Path(exists=True),
)
@click.argument(
    'output_path', default="feature_toggle_report",
)
@click.option(
    '--show-state', is_flag=True,
)
@click.option(
    '--env', default=None, help="specify env name ifyou want data for only one env",
    )
@click.option(
    '--toggle-type', default=None, help="specify toggle type if you only want data on one toggle type",
    )
def main(annotations_dir, toggle_data_dir, output_path, show_state, env, toggle_type):
    # each env should have a folder with all its sql dump with toggle data
    # folders name as: <env_name>_env
    # example: prod_env, stage_env, devstack_env
    env_name_pattern = re.compile(r'(?P<env>[a-z0-9]*)_env')

    # find all the dirs in toggle_data_dir whose name match pattern
    data_paths = []
    toggle_data_dir_content = os.listdir(toggle_data_dir)
    for path in toggle_data_dir_content:
        env_name = env_name_pattern.search(path).group('env')
        if os.path.is_dir(os.path.join(toggle_data_dir, path)) and env_name:
            data_paths.append((path, env_name))

    total_info = {}
    for env_data_path, env_name in env_data_paths:
        if env is not None and env_name != env:
            continue
        total_info[env_name] = {}
        if show_state:
            add_toggle_state_to_idas(total_info[env_name], env_data_path)
        add_toggle_annotations_to_idas(total_info[env_name], annotations_dir)
    renderer = CsvRenderer()
    renderer.render_csv_report(total_info, os.path.join(output_path, "report.csv"), toggle_type)


if __name__ == '__main__':
    main()
