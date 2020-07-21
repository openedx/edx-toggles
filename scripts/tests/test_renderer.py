from scripts.renderers import CsvRenderer
import random
import unittest


csv_renderer = CsvRenderer()
tc = unittest.TestCase()

def test_get_sorted_headers_from_toggles():
    """
    CSV column should be order by these rules by order:
    - name should be first column
    - anything with name in column title has priority
    - state data has priority, column titles with "state" in it
    - alphabetically
    """
    unsorted_headers = ["env_name", "aaaaa", "ida_name", "bbbbb", "name", "state_not"]
    flattened_data = [{key:True for key in unsorted_headers} for num in range(20)]
    sorted_header = csv_renderer.get_sorted_headers_from_toggles(flattened_data)
    assert sorted_header[0] == "name"
    assert sorted_header[2] == "ida_name"
    assert sorted_header[3] == "state_not"
    assert sorted_header[5] == "bbbbb"

def test_filter_and_sort_toggles_filtering():
    """
    There are cases where we might just want a subset of data,
    """
    toggle_types = ["WaffleFlag", "WaffleSwitch", "DjangoSettings", "Random1", "Random2"]
    names = ["n{}".format(num) for num in range(5*len(toggle_types))]
    data = [{"name":name, "toggle_type":random.choice(toggle_types)} for name in names]

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
