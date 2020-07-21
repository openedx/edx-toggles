# -*- coding: utf-8 -*-

import datetime
import io
import os
import re
import yaml
import logging
from collections import defaultdict

import click
import jinja2

from scripts.ida import IDA, add_toggle_state_to_idas, add_toggle_annotations_to_idas
from scripts.renderers import CsvRenderer


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
    'output_file_path', default="feature_toggle_report",
)
@click.option(
    '--show-state', is_flag=True,
    help="if this is present, the report will include toggle state",
)
@click.option(
    '--env',
    multiple=True,  # allows user to get union of multiple envs
    default=None,
    help='specify env names if you want data from certain envs',
    )
@click.option(
    '--toggle-type',
    multiple=True,    # allows user to get union of multiple toggle-types
    default=None,
    help='specify toggle types if you only want data on certain toggle type',
    )
@click.option(
    '--configuration',
    default=None,
    help='alternative method to do configuration, the flags will have priority',
    )
def main(annotations_dir, toggle_data_dir, output_file_path, show_state, env, toggle_type, configuration):
    """
    Script to process annotation and state data for toggles and output it a report.

    \b
    Arguments:
        * annotations_dir: path to where toggle data is location
        * toggle_data_dir:  a path to directory containing directories containing json files with sql data dump
        * output_file_path: name of file to which to write report
    """

    # Read configuration file:
    if configuration is not None:
        with open(configuration) as yaml_file:
            configuration = yaml.safe_load(yaml_file)
    else:
        configuration = {}

    # process configuration
    # flag inputs overwrite stuff in configuration file
    toggle_type_filter = toggle_type
    if not toggle_type and "toggle_type" in configuration.keys():
        toggle_type_filter = configuration["toggle_type"]

    requested_envs = env
    if not env and "env" in configuration.keys():
        requested_envs = configuration["env"]

    if "show_state" in configuration.keys():
        show_state = configuration["show_state"]

    # each env should have a folder with all its sql dump with toggle data
    # folders name as: <env_name>_env
    # example: prod_env, stage_env, devstack_env
    env_name_pattern = re.compile(r'(?P<env>[a-z0-9]*)_env')

    # find all the dirs in toggle_data_dir whose name match pattern

    env_data_paths = []
    toggle_data_dir_content = os.listdir(toggle_data_dir)
    for path in toggle_data_dir_content:
        env_name_search = env_name_pattern.search(path)
        if os.path.isdir(os.path.join(toggle_data_dir, path)) and env_name_search:
            env_data_paths.append((os.path.join(toggle_data_dir, path), env_name_search.group('env')))

    total_info = {}
    for env_data_path, env_name in env_data_paths:
        if requested_envs and env_name not in requested_envs:
            LOGGER.debug("Not reading toggle state data for {} env".format(env_name))
            continue
        total_info[env_name] = {}

        # add data for each ida
        if show_state:
            add_toggle_state_to_idas(total_info[env_name], env_data_path, configuration.get("ida", defaultdict(dict)))
            print("INFO 1 : idas in {}: {}".format(env_name, len(total_info[env_name])))
        add_toggle_annotations_to_idas(total_info[env_name], annotations_dir, configuration.get("ida", defaultdict(dict)))
        print("INFO 2: idas in {}: {}".format(env_name, len(total_info[env_name])))

    renderer = CsvRenderer()
    renderer.render_csv_report(total_info, output_file_path, toggle_type_filter)


if __name__ == '__main__':
    main()
