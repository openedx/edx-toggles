import random
import pytest
from unittest import mock, TestCase

from scripts.renderers import CsvRenderer
from scripts.ida_toggles import IDA
from scripts.toggles import Toggle, ToggleState, ToggleAnnotation

csv_renderer = CsvRenderer()
tc = TestCase()

def test_get_sorted_headers_from_toggles():
    """
    CSV column should be ordered by the following ordered list of rules::
    - name should be first column
    - anything with name in column title has priority
    - state data has priority, column titles with "state" in it
    - alphabetically
    """
    unsorted_headers = ["env_name", "aaaaa", "ida_name", "bbbbb", "name", "not_s"]
    flattened_data = [{key:True for key in unsorted_headers} for num in range(20)]
    sorted_header = csv_renderer.get_sorted_headers_from_toggles(flattened_data, ["name"])
    assert sorted_header[0] == "name"
    assert sorted_header[2] == "ida_name"
    assert sorted_header[3] == 'aaaaa'
    assert sorted_header[5] == 'not_s'

def test_filter_and_sort_toggles_filtering():
    """
    There are cases where we might just want a subset of data,
    """
    toggle_types = ["WaffleFlag", "WaffleSwitch", "DjangoSetting"]
    names = ["n{}".format(num) for num in range(5*len(toggle_types))]
    data = [{"name":name, "toggle_type":random.choice(list(toggle_types))} for name in names]

    # test with no filtering
    filtered_data = csv_renderer.filter_and_sort_toggles(data)
    tc.assertCountEqual(data, filtered_data)

    # filter by WaffleFlag as str input
    filtered_data = csv_renderer.filter_and_sort_toggles(data, "WaffleFlag")
    tc.assertCountEqual([datum for datum in data if datum["toggle_type"]=="WaffleFlag"], filtered_data)

    # filter by WaffleFlag as list input
    filtered_data = csv_renderer.filter_and_sort_toggles(data, ["WaffleFlag"])
    tc.assertCountEqual([datum for datum in data if datum["toggle_type"]=="WaffleFlag"], filtered_data)

    # filter by WaffleFlag and WaffleSwitch
    filtered_data = csv_renderer.filter_and_sort_toggles(data, ["WaffleFlag", "WaffleSwitch"])
    tc.assertCountEqual([datum for datum in data if datum["toggle_type"]=="WaffleFlag" or datum["toggle_type"]=="WaffleSwitch"], filtered_data)

def test_filter_and_sort_toggles_sorting():
    """
    Make sure data is sorted by name
    """
    # create a list of random names
    names = ["{}{}{}{}".format(*(random.choice(list("abcdefghijkl")) for num in range(4))) for num2 in range(30)]
    data = [{"name":name, "toggle_type":"NAN", "NAN":random.randrange(50)} for name in names]
    sorted_data = csv_renderer.filter_and_sort_toggles(data)
    sorted_names = sorted(names)
    test_sorted_names = [datum["name"] for datum in sorted_data]
    assert sorted_names == test_sorted_names
