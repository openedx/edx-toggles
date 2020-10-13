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

    def render_csv_report(self, toggle_info_structured_dicts, file_path="report.csv", toggle_types=None, header=None, summarize=False):
        """
        takes data, processes it, and outputs it in csv form
        """

        toggles_info_flattened_dicts = self.add_info_source_to_dict_keys(toggle_info_structured_dicts)

        sorted_toggles_dicts = self.filter_and_sort_toggles(toggles_info_flattened_dicts, toggle_types)
        header = self.get_sorted_headers_from_toggles(sorted_toggles_dicts, header)
        self.write_csv(file_path, sorted_toggles_dicts, header)

    def add_info_source_to_dict_keys(self, toggle_info_structured_dicts):
        """
        This function flattens the dicts in toggle_info_structured_dicts list

        toggle_info_structured_dicts is a list of dicts with two keys: state, annotations
        These keys are the location of where the info came from
        (state: toggles endpoint, annotations: from code annotations)

        This function flattens dict by adding source info to keys
        """
        temp_data = []
        for datum in toggle_info_structured_dicts:
            toggle_dict_info = {}
            for key in datum["state"].keys():
                toggle_dict_info["{}_s".format(key)] = datum["state"][key]
            for key in datum["annotations"].keys():
                toggle_dict_info["{}_a".format(key)] = datum["annotations"][key]
            temp_data.append(toggle_dict_info)
        return temp_data

    def filter_and_sort_toggles(self, toggles_info_flattened_dicts, toggle_type_filter=None):
        """
        Arguments:
            - toggles_info_flattened_dicts: list[dict] dicts should have all relevant data relating to one toggle
            - toggle_type_filter: list of type names: there are multiple toggle types, so which would you like to output
                     if set to None, everything will be outputted
        Returns:
            - list: sorted list of filtered toggle data.
        """

        # filter toggles by toggle_types
        data_to_render = []
        if not toggle_type_filter:
            data_to_render = toggles_info_flattened_dicts
        else:
            if isinstance(toggle_type_filter, str):
                toggle_type_filter = [toggle_type_filter]
            for toggle_dict in toggles_info_flattened_dicts:
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

            Sorting algorithm:
            order first by keys that have the word "name" in it
            Order second by keys that originate from state data (postfixed by "_s")
            Order Third alphabetically
            """
            sort_by=[]
            # setting key for keys with name to False causes them to appear first in header
            sort_by.append(False if "name" in key else True)
            # show states first
            state_pattern = re.compile(".*_s$")
            annotation_pattern = re.compile(".*_a$")
            sort_by.append(bool(annotation_pattern.search(key) or state_pattern.search(key)))
            sort_by.append(not bool(state_pattern.search(key)))
            sort_by.append(bool(annotation_pattern.search(key)))
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

    def write_csv(self, file_name, data, fieldnames):
        """
        writes data_dict in file with name file_name
        """
        with open(file_name, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for datum in data:
                writer.writerow(datum)
