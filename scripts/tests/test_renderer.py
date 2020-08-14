import random
import pytest
from unittest import mock, TestCase

from scripts.renderers import CsvRenderer
from scripts.ida_toggles import IDA
from scripts.toggles import Toggle, ToggleState, ToggleAnnotation

csv_renderer = CsvRenderer()
tc = TestCase()

@mock.patch('scripts.toggles.Toggle')
def test_transform_toggle_data_for_csv(mocked_toggle):
    """Test to make sure data is flattened correctly"""

    env1 = {'lms':IDA('lms', {"rename": "edxapp"}), 'cms':IDA('cms')}
    env2 = {'lms':IDA('lms', {"rename": "edxapp"}), 'cms':IDA('cms')}
    envs_data = {'env1':env1, 'env2':env2}
    total_num_of_loops = 0
    for env_name, env in envs_data.items():
        for ida_name, ida in env.items():
            ida.toggles = {}
            ida.toggles['WaffleFlag'] = {}
            ida.toggles['WaffleFlag']["n1"] = Toggle("n1")
            ida.toggles['WaffleFlag']['n2'] = Toggle("n2")
            ida.toggles['WaffleSwitch'] = {}
            ida.toggles['WaffleSwitch']['n3'] = Toggle("n3")
            ida.toggles['WaffleSwitch']['n4'] = Toggle("n4")
            ida.toggles['WaffleSwitch']['n5'] = Toggle("n5")
            total_num_of_loops += 1
    mocked_toggle.full_data = lambda: {'d1':1, 'd2':2, 'd3':3}
    output_data = csv_renderer.transform_toggle_data_for_csv(envs_data)

    # test to make sure renaming happened correctly
    assert 'lms' not in [datum['ida_name'] for datum in output_data]
    assert "edxapp" in [datum['ida_name'] for datum in output_data]
    # test to make sure everything is collected
    assert total_num_of_loops*2 == [datum['toggle_type'] for datum in output_data].count('WaffleFlag')
    assert total_num_of_loops*3 == [datum['toggle_type'] for datum in output_data].count('WaffleSwitch')


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
    assert sorted_header[3] == "not_s"
    assert sorted_header[5] == "bbbbb"

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

def test_get_keys_that_are_always_same():
    toggles_data={
    "n1":[{"s1":1,"s2":True, "d1":1, "d2":True},{"s1":1,"s2":True, "d1":2, "d2":False},{"s1":1,"s2":True, "d1":3, "d2":True}],
    "n2":[{"s1":2,"s2":False, "d1":1, "d2":True},{"s1":2,"s2":False, "d1":5, "d2":False},{"s1":2,"s2":False, "d1":3, "d2":False}],
    "n3":[{"s3":2,"s4":False, "d1":1, "d2":True},{"s3":2,"s4":False, "d1":7, "d2":False},{"s3":2,"s4":False, "d1":20, "d2":True}],
    "n4":[{"s3":1,"s4":True, "d1":1, "d2":False},{"s3":1,"s4":True, "d1":8, "d2":False},{"s3":1,"s4":True, "d1":6, "d2":True}],
    }
    same_keys = csv_renderer.get_keys_that_are_always_same(toggles_data)
    assert "s1" in same_keys
    assert "s2" in same_keys
    assert "s3" in same_keys
    assert "s4" in same_keys
    assert "d1" not in same_keys
    assert "d2" not in same_keys


def test_summarize_data():
    """
    Make sure data is summarized correctly
    """
    pass
