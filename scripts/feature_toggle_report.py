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
    '--verbose-report', is_flag=True,
    help="To get a more verbose version of the report. This will result in one row per state data (from each new env) for a toggle",
)
@click.option(
    '--configuration',
    default=None,
    help='alternative method to do configuration, the command-line options will have priority',
    )
def main(annotations_dir, toggle_data_dir, output_file_path, env, toggle_type, verbose_report, configuration):
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
    # commandline-option inputs overwrite configuration file data
    toggle_type_filter = [ToggleTypes.get_internally_consistent_toggle_type(t_type) for t_type in toggle_type]
    if not toggle_type and "toggle_type" in configuration.keys():
        toggle_type_filter = [ToggleTypes.get_internally_consistent_toggle_type(toggle_type) for toggle_type in configuration["toggle_type"]]

    requested_envs = env
    if not env and "env" in configuration.keys():
        requested_envs = configuration["env"]

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

    # if no env folders were found at toggle_data_dir, assume that dir contains data for one env
    if not env_data_paths:
        env_name_search = env_name_pattern.search(os.path.basename(toggle_data_dir))
        if env_name_search:
            env_data_paths.append((toggle_data_dir, env_name_search.group('env')))
        else:
            raise Exception('Directory at {} does not match required structure, see readme for more info'.format(toggle_data_dir))

    idas = {}
    for env_data_path, env_name in env_data_paths:
        # if an env is specified in requested_envs, filter out everyother env
        # if no env is specified, assume all envs are valid
        if requested_envs and env_name not in requested_envs:
            LOGGER.debug("Skip reading toggle state data for {} env".format(env_name))
            continue

        # add data for each ida
        add_toggle_state_to_idas(idas, env_data_path, configuration.get("ida", defaultdict(dict)), env_name=env_name)

        add_toggle_annotations_to_idas(idas, annotations_dir, configuration.get("ida", defaultdict(dict)))

    toggle_data = []
    if verbose_report:
        for ida in idas.values():
            toggle_data.extend(ida.get_full_report())
    else:
        for ida in idas.values():
            toggle_data.extend(ida.get_toggles_data_summary())


    renderer = CsvRenderer()
    # any keys in this header will be prioritized first by header sorting algorithm in renderer
    partial_header = ["name", "ida_name", "code_owner", "oldest_created", "newest_modified"]
    renderer.render_csv_report(toggle_data, output_file_path, toggle_type_filter, partial_header)


if __name__ == '__main__':
    main()
