# -*- coding: utf-8 -*-

import os
import re
import yaml
import logging
from collections import defaultdict

import click

from scripts.ida_toggles import IDA, add_toggle_state_to_idas, add_toggle_annotations_to_idas
from scripts.toggles import ToggleTypes
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
    '--summarize', is_flag=True,
    help="if you want a simplified version of report",
)
@click.option(
    '--configuration',
    default=None,
    help='alternative method to do configuration, the command-line options will have priority',
    )
def main(annotations_dir, toggle_data_dir, output_file_path, show_state, env, toggle_type, summarize, configuration):
    """
    Script to process annotation and state data for toggles and output it a report.

    \b
    Arguments:
        * annotations_dir: path to where toggle data is location
        * toggle_data_dir:  a path to directory containing json files with sql data dump
        * output_file_path: name of file to which to write report
    """
    # Read configuration file:
    if configuration is not None:
        with open(configuration) as yaml_file:
            configuration = yaml.safe_load(yaml_file)
    else:
        configuration = {}

    # process configuration
    # commandline-option inputs overwrite stuff in configuration file
    toggle_type_filter = toggle_type
    if not toggle_type and "toggle_type" in configuration.keys():
        toggle_type_filter = [ToggleTypes.get_internally_consistent_toggle_type(toggle_type) for toggle_type in configuration["toggle_type"]]

    requested_envs = env
    if not env and "env" in configuration.keys():
        requested_envs = configuration["env"]

    if "show_state" in configuration.keys():
        show_state = configuration["show_state"]


    toggles_data = {}
    add_toggle_state_to_idas(toggles_data, toggle_data_dir, configuration.get("ida", defaultdict(dict)))
    add_toggle_annotations_to_idas(toggles_data, annotations_dir, configuration.get("ida", defaultdict(dict)))

    renderer = CsvRenderer()
    renderer.render_toggles_report(toggles_data, output_file_path, toggle_type_filter, ["name", "ida_name", "code_owner", "oldest_created", "newest_modified"], summarize)


if __name__ == '__main__':
    main()
