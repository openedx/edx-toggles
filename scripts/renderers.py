"""
    Creates classes that render toggles data into either html or csv
"""
import datetime
import io
import os
import csv
import logging
from collections import OrderedDict

import click
import jinja2


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class CsvRenderer():
    """
    Used to output toggles+annotations data as CSS
    """

    def transform_toggle_data_for_csv(self, envs_data):
        """
        Retrieve list of individual toggle datums from envs_data

        envs_data is a dict with a complex structure of environments, idas and toggles by toggle type.
        Return a flattened list for each toggle in a specific environment in preparation for csv output.
        """
        toggles_data = []
        for env, idas in envs_data.items():
            for ida_name, ida in idas.items():
                for toggle_type, toggles in ida.toggles.items():
                    for toggle in toggles:
                        data_dict = toggle.full_data()
                        data_dict["toggle_type"] = toggle_type
                        data_dict["ida_name"] = ida_name
                        data_dict["env_name"] = env
                        toggles_data.append(data_dict)
        return toggles_data

    def filter_and_sort_toggles(self, toggles_data, toggle_type_filter=None):
        """
        Arguments:
            - toggles_data: list[dict] dicts should have all relevant data relating to one toggle
            - toggle_type_filter: list of type names: there are multiple toggle types, so which would you like to output
                     if set to None, everything will be outputed
        Returns:
            - list: sorted list of filtered toggle data.
        """

        # filter toggles by toggle_types
        data_to_render = []
        if toggle_types is None:
            data_to_render = toggles_data
        else:
            if isinstance(toggle_types, str):
                toggle_types = [toggle_types]
            for toggle_dict in toggles_data:
                if toggle_dict["toggle_type"] in toggle_types:
                    data_to_render.append(toggle_dict)

        # sort data by either annotation_name or state_name
        sorting_key = lambda datum: (datum.get("annotation_name", ""), datum.get("state_name", ""))
        data_to_render = sorted(data_to_render, key=sorting_key)

    def get_sorted_headers_from_toggles(flattened_toggles_data)
        # get header from data
        header = set()
        for datum in flattened_toggles_data:
            header = header.union(set(datum.keys()))

        def sorting_header(key):
            """
            there are multiple criterions by which we should sort header keys
            """
            sort_by=[]
            # setting key for keys with name to False causes them to appear first in header
            sort_by.append(False if "name" in key else True)
            # show states first
            sort_by.append(False if "state" in key else True)
            # finally sort by alphebetical order
            sort_by.append(key)
            return tuple(sort_by)

        header = sorted(list(header), key=sorting_header)
        return header

    def render_csv_report(self, envs_ida_toggle_data, file_path="report.csv", toggle_types=None):
        """
        takes data, processes it, and outputs it in csv form
        """
        toggles_data = self.transform_toggle_data_for_csv(envs_ida_toggle_data)
        data_to_render = self.filter_and_sort_toggles(toggles_data, toggle_types)
        header = self.get_sorted_headers_from_toggles(data_to_render)
        self.write_csv(file_path, data_to_render, header)

    def write_csv(self, file_name, data, fieldnames):
        """
        writes data_dict in file with name file_name
        """
        with open(file_name, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for datum in data:
                writer.writerow(datum)


class HtmlRenderer():

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
