"""
    Creates classes that render toggles data into either html or csv
"""
import datetime
import io
import os
import re
import csv
import logging
from collections import OrderedDict, defaultdict, Hashable

import click
import jinja2

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class CsvRenderer():
    """
    Used to output toggles+annotations data as CSS
    """

    def render_csv_report(self, ida_toggle_data, file_path="report.csv", toggle_types=None, header=None, summarize=False):
        """
        takes data, processes it, and outputs it in csv form
        """
        if summarize:
            output_data_list = self.output_summary(ida_toggle_data, toggle_types)
        else:
            output_data_list = self.output_full_data(ida_toggle_data)

        temp_data = []
        for data in output_data_list:
            toggle_dict_info = {}
            for key in data["state"].keys():
                toggle_dict_info["{}_s".format(key)] = data["state"][key]
            for key in data["annotations"].keys():
                toggle_dict_info["{}_a".format(key)] = data["annotations"][key]
            temp_data.append(toggle_dict_info)

        data_to_render = self.filter_and_sort_toggles(temp_data, toggle_types)
        header = self.get_sorted_headers_from_toggles(data_to_render, header)
        self.write_csv(file_path, data_to_render, header)

    def output_summary(self, toggles_data, types_filter=None):
        """
        Experiment with an additional CSV format (to enhance, not replace, the original format)

        One line per toggle.
        is_active (contains calculated_status for waffle flag) column per environment
            - toggle_active_stage? toggle_active_prod
        column for oldest_created, newest_modified (nice to have, or prototype can just take any value here and not compare)
        Combine waffle notes from each environment into a single column
        Other data to include would be anything that is always the same for all environments:
            - Annotation data
            - Waffle Flag class name
            - code_owner
            - etc.
        """
        return self.summarize_data(toggles_data)

    def output_full_data(self, toggles_data):
        data_to_render = []
        for ida_name, ida in toggles_data.items():
            data_to_render.extend(ida.get_full_report())
        return data_to_render

    def filter_and_sort_toggles(self, toggles_data, toggle_type_filter=None):
        """
        Arguments:
            - toggles_data: list[dict] dicts should have all relevant data relating to one toggle
            - toggle_type_filter: list of type names: there are multiple toggle types, so which would you like to output
                     if set to None, everything will be outputted
        Returns:
            - list: sorted list of filtered toggle data.
        """

        # filter toggles by toggle_types
        data_to_render = []
        if not toggle_type_filter:
            data_to_render = toggles_data
        else:
            if isinstance(toggle_type_filter, str):
                toggle_type_filter = [toggle_type_filter]
            for toggle_dict in toggles_data:
                if toggle_dict["toggle_type"] in toggle_type_filter:
                    data_to_render.append(toggle_dict)

        # sort data by either annotation_name or state_name
        sorting_key = lambda datum: datum.get("name", "")
        return sorted(data_to_render, key=sorting_key)

    def get_sorted_headers_from_toggles(self, flattened_toggles_data, initial_header=None):
        # get header from data
        header = set()
        for datum in flattened_toggles_data:
            header = header.union(set(datum.keys()))

        def sorting_header(key):
            """
            there are multiple criterion by which we should sort header keys
            """
            sort_by=[]
            # setting key for keys with name to False causes them to appear first in header
            sort_by.append(False if "name" in key else True)
            # show states first
            state_pattern = re.compile(".*_s$")
            annotation_pattern = re.compile(".*_a$")
            sort_by.append(True if annotation_pattern.search(key) or state_pattern.search(key) else False)
            sort_by.append(False if state_pattern.search(key) else True)
            sort_by.append(True if annotation_pattern.search(key) else False)
            # finally sort by alphabetical order
            sort_by.append(key)
            return tuple(sort_by)


        output = []
        if initial_header is not None:
            # put columns in initial header at the beginning of the output
            # - though only if there is data on it
            for column in initial_header:
                if column in header:
                    output.append(column)
                    header.remove(column)
        header = sorted(list(header), key=sorting_header)
        output.extend(header)
        return output

    def summarize_data(self, toggles_data):
        """
        Returns only subset containing the essential information
        """
        data_to_render = []
        for ida_name, ida in toggles_data.items():
            data_to_render.extend(ida.get_toggles_data_summary())
        return data_to_render

    def write_csv(self, file_name, data, fieldnames):
        """
        writes data_dict in file with name file_name
        """
        with open(file_name, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for datum in data:
                writer.writerow(datum)
