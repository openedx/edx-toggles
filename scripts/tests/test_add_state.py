import pytest
import json

from scripts.ida_toggles import IDA
from scripts.toggles import Toggle, ToggleState


@pytest.fixture
def toggles_data_dict():
    with open("scripts/tests/toggle_data.json") as json_file:
        return json.load(json_file)

@pytest.fixture
def sample_ida(toggles_data_dict):
    ida = IDA('my-ida')
    ida._add_toggle_data(toggles_data_dict, "env")
    return ida

def test_correct_num_added(sample_ida):
    """
    Tests whether json input was parsed correctly and the right toggle types were recognized
    """
    # assert number of toggles types == 3
    assert len(sample_ida.toggles) == 3
    # assert number of django_settings toggles
    assert len(sample_ida.toggles["django_settings"]) == 1
    # assert number of waffle_switches toggles
    assert len(sample_ida.toggles["waffle_switches"]) == 1
    # assert number of waffle_flags toggles
    assert len(sample_ida.toggles["waffle_flags"]) == 2

def test_course_waffle_flag_handling(sample_ida):
    """
    Tests to make sure the raw data was properly processed
    """
    # retreive prepared data for each toggle
    raw_report = sample_ida.get_full_report()
    course_waffle_flag_toggle = None

    for toggle_dict in raw_report:
        if toggle_dict["state"]["name"] == "some.coursewaffleflag":
            course_waffle_flag_toggle = toggle_dict
    assert course_waffle_flag_toggle is not None
    assert "num_courses_forced_on" in course_waffle_flag_toggle["state"]
    assert "num_courses_forced_off" in course_waffle_flag_toggle["state"] 
    assert course_waffle_flag_toggle["state"]["num_courses_forced_on"] == 2
    assert course_waffle_flag_toggle["state"]["num_courses_forced_off"] == 1
