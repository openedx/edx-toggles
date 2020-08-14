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
                    for toggle_name, toggle in toggles.items():
                        data_dict = toggle.full_data()
                        data_dict["toggle_type"] = toggle_type
                        # In case you want the report to call the ida by a different ida_name
                        # example: lms should be called edxapp in report
                        data_dict["ida_name"] = ida.configuration.get("rename", ida_name)
                        data_dict["env_name"] = env
                        toggles_data.append(data_dict)
        return toggles_data

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
            pattern = re.compile(".*_s$")
            sort_by.append(False if pattern.search(key) else True)
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

    def output_full_data(self, envs_ida_toggle_data):
        toggles_data = self.transform_toggle_data_for_csv(envs_ida_toggle_data)
        return toggles_data

    def combine_envs_data_under_toggle_name(self, envs_data, type_filter=None):
        """
        envs data is structured: envs->ida->toggles, this converts to (toggle, ida)->{env1_toggle_data, env2_toggle_data}
        """
        toggles_data = {}
        for env, idas in envs_data.items():
            for ida_name, ida in idas.items():
                for toggle_type, toggles in ida.toggles.items():
                    if type_filter is not None and toggle_type not in type_filter:
                        continue
                    for toggle_name, toggle in toggles.items():
                        data_dict = toggle.full_data()
                        data_dict["toggle_type"] = toggle_type
                        data_dict["env_name"] = env
                        # In case you want the report to call the ida by a different ida_name
                        # example: lms should be called edxapp in report
                        ida_name = ida.configuration.get("rename", ida_name)
                        data_dict["ida_name"] = ida_name
                        toggle_identifier = (toggle_name, ida_name)
                        # toggles are unique by its name and by the ida it belongs to
                        if toggle_identifier in toggles_data:
                            toggles_data[toggle_identifier].append(data_dict)
                        else:
                            toggles_data[toggle_identifier] = [data_dict]

        return toggles_data

    def get_keys_that_are_always_same(self, toggles_data):
        """
        Gets keys whose values are always same for each individual toggle for every env
        This is a search across toggles, so this will ignore keys whose values are same in one toggle but are different in another toggle
            - such as: everyone or is_active(which can be the same, but are not always the same)
        This will include keys like: any annotation keys, Waffle Flag class name, code_owner, etc.
        A key does not have to exist in all toggles for it to be included
        """
        def get_identical_keys_for_toggle(toggle_data):
            """
            Finds keys that have the same values for every env in data for **one** toggle
            Argument:
                toggle_data: list of dicts, [{env1_data}, {env2_data}]
            returns:
                all_keys: list of all keys that existed in data
                same_keys: list of all keys whose values were the same in each env(if a key only exists in one env, it is not included)
            """
            # reorganize data by key
            reorganized_data = {}
            for datum in data:
                for key, value in datum.items():
                    if key in reorganized_data:
                        reorganized_data[key].append(value)
                    else:
                        reorganized_data[key] = [value]
            same_keys = []
            # check if all values for a key are same
            for key, values in reorganized_data.items():
                if [True for value in values if isinstance(value, Hashable)]:
                    if len(values)== len(data) and len(set(values)) == 1:
                        same_keys.append(key)
            return reorganized_data.keys(), same_keys

        # end results: {key*:True for keys that are same, key*:False}
        is_key_same = defaultdict(bool)
        for toggle_name, data in toggles_data.items():
            all_keys, toggle_same_keys = get_identical_keys_for_toggle(data)
            for key in all_keys:
                # if a key has been seen before and it does not have the same values for this toggle, set it to false
                if key in is_key_same.keys() and key not in toggle_same_keys:
                    is_key_same[key] = False
                # only set to true the key has same values for this toggle and it has not been seen before
                if key not in is_key_same.keys() and key in toggle_same_keys:
                    is_key_same[key] = True
        return [key for key, value in is_key_same.items() if value]




    def summarize_data(self, toggles_data):
        data_to_render = []
        same_keys = self.get_keys_that_are_always_same(toggles_data)
        for toggle_identifier, data in toggles_data.items():
            summary_datum = {}
            summary_datum["oldest_created"] = min([datum["created_s"] for datum in data if "created_s" in datum], default="")
            summary_datum["newest_modified"] = max([datum["modified_s"] for datum in data if "modified_s" in datum], default="")
            summary_datum["note"] = ", ".join([datum["note_s"] for datum in data if "note_s" in datum])
            # add info for stuff that should be same for in each env
            # this includes things such as: annotation_data, ida_name, code_owner, class name ...
            common_items = {key:value for key, value in data[0].items() if key in same_keys}

            if common_items:
                summary_datum.update(common_items)

            # add info that is specific to each env
            for datum in data:
                env_name = datum["env_name"]
                # TODO(jinder): finalize name of is_active and check if its the same for all toggle types
                summary_datum["is_active_{}".format(env_name)] = datum.get("is_active_s", None)
            data_to_render.append(summary_datum)
        return data_to_render


    def output_summary(self, envs_ida_toggle_data, types_filter=None):
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
        toggles_data = self.combine_envs_data_under_toggle_name(envs_ida_toggle_data, types_filter)
        return self.summarize_data(toggles_data)


    def render_csv_report(self, envs_ida_toggle_data, file_path="report.csv", toggle_types=None, header=None, summarize=False):
        """
        takes data, processes it, and outputs it in csv form
        """
        if summarize:
            output_data_list = self.output_summary(envs_ida_toggle_data, toggle_types)
        else:
            output_data_list = self.output_full_data(envs_ida_toggle_data)

        data_to_render = self.filter_and_sort_toggles(output_data_list, toggle_types)
        header = self.get_sorted_headers_from_toggles(data_to_render, header)
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
