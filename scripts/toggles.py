"""
Common classes to represent toggles withint IDAs.
"""
import collections
import re
import logging
import datetime


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ToggleTypes():
    valid_toggle_types = ("django_settings", "waffle_flags", "waffle_switches")
    annotation_to_state_toggle_type_map = {
            "CourseWaffleFlag": "waffle_flags",
            "ExperimentWaffleFlag": "waffle_flags",
            "DjangoSetting": "django_settings",
            "SettingDictToggle": "django_settings",
            "SettingToggle": "django_settings",
            "WaffleFlag": "waffle_flags",
            "WaffleSwitch": "waffle_switches",
        }

    @classmethod
    def get_internally_consistent_toggle_type(cls, input_type):
        """
        Annotations report and toggles state outputs define their types slightly differently.
        This function converts from the annotation toggle type to the state toggle type.
        """
        toggle_type = cls.annotation_to_state_toggle_type_map.get(input_type, input_type)

        if toggle_type not in cls.valid_toggle_types:
            LOGGER.warning(
            f'Name of annotation toggle type not recognized: {toggle_type}'
            )
        return toggle_type


class Toggle:
    """
    Represents a feature toggle in an IDA, including the current state of the
    toggle in the database and any additional information defined in the
    source code (marked via `code-annotations`). To account for the case in which
    a feature toggle is not yet annotated or has been removed from the database
    but not the source code, this constructor can handle the case in which
    only one of the above components could be identified.
    """

    def __init__(self, name, state=None, annotations=None, ida_name=None, toggle_type=None):
        self.name = name
        self.states = [state] if state is not None else []
        self.annotations = annotations
        self.ida_name = ida_name
        self.toggle_type = toggle_type

    def __str__(self):
        return self.name

    def add_state(self, state):
        self.states.append(state)

    def basic_report(self):
        report = {}
        report["name"] = self.name
        report["ida_name"] = self.ida_name
        report["toggle_type"] = self.toggle_type
        return report

    def get_summary_report(self, summarize=True):
        report = {}
        if summarize:
            report["state"] = self.get_state_summary()
        report["annotations"] = self.get_annotations()
        report.update(self.basic_report())
        return report

    def get_full_reports(self):
        data = []
        for state in self.states:
            report = {}
            state._prepare_state_data()
            report['state'] = state._cleaned_state_data
            report["annotations"] = self.get_annotations()
            report.update(self.basic_report())
            data.append(report)
        return data


    def get_annotations(self):
        output = {}
        if self.annotations:
            self.annotations._prepare_annotation_data()
            output.update(self.annotations._cleaned_annotation_data)
        else:
            LOGGER.debug(f"{self.name} Toggle's annotations is None")
        return output

    def get_state_summary(self):
        data = []
        for state in self.states:
            state._prepare_state_data()
            data.append(state._cleaned_state_data)

        summary = {}
        summary["oldest_created"] = min([datum["created"] for datum in data if "created" in datum], default="")
        summary["newest_modified"] = max([datum["modified"] for datum in data if "modified" in datum], default="")
        summary["note"] = ", ".join([datum["note"] for datum in data if "note" in datum])
        # add info that is specific to each env
        envs_states=[]
        for datum in data:
            env_name = datum["env_name"]
            summary[f"computed_status_{env_name}"] = datum.get("computed_status", datum.get("is_active", None))
            envs_states.append(summary[f"computed_status_{env_name}"])
            if "code_owner" in datum:
                summary["code_owner"] = datum["code_owner"]
        if len(data) > 1:
            summary["all_envs_match"] = True if len(envs_states) == len(data) and len(set(envs_states)) == 1 and envs_states[0] is not None else False

        return summary


class ToggleAnnotation:
    """
    Represents a group of individual code annotations all referencing the same
    Toggle.
    """

    def __init__(self, report_group_id, source_file):
        self.report_group_id = report_group_id
        self.source_file = source_file
        self.line_numbers = []
        self.github_url = None
        self._raw_annotation_data = {}
        self._cleaned_annotation_data = collections.defaultdict(str)

    def line_range(self):
        lines = sorted(self.line_numbers)
        return lines[0], lines[-1]

    def _prepare_annotation_data(self):
        self._cleaned_annotation_data["source_file"] = self.source_file
        self._cleaned_annotation_data["line_number"] = self.line_numbers
        self._cleaned_annotation_data["url"] = self.github_url
        for k, v in self._raw_annotation_data.items():
            if k == 'implementation':
                self._cleaned_annotation_data[k] = v[0]
            else:
                self._cleaned_annotation_data[k] = v


class ToggleState:
    """
    Represents the state of a feature toggle, configured within an IDA,
    as pulled from the IDA's database.
    """

    def __init__(self, toggle_type, data, env_name):
        self.toggle_type = toggle_type
        self._raw_state_data = collections.defaultdict(str, data)
        self._cleaned_state_data = collections.defaultdict(str)
        self.env_name = env_name

    def update_data(self, data):
        """
        Updates the state data.
        """
        self._raw_state_data.update(data)

    def get_datum(self, key, cleaned=True):
        """
        Get data from either _raw_state_data dict or _cleaned_state_data dict

        Arguments:
            key: the key name for data
            cleaned: Whether to get datum from _raw_state_data dict or _cleaned_state_data
                By default, this will get datum from _cleaned_state_data:
        """
        if cleaned:
            self._prepare_state_data()
            return self._cleaned_state_data.get(key)
        else:
            return self._raw_state_data.get(key)

    def set_datum(self, key, value, cleaned=True):
        """
        Adding data to either _raw_state_data dict or _cleaned_state_data dict

        Arguments:
            key: key name for addition to dict
            value: data to add to dict
            cleaned: Whether to add data to _raw_state_data dict or _cleaned_state_data
                By default, this will add datum to _cleaned_state_data:
                    Using this functions allows you to skip the _prepare_state_data function call and put
                    datum directly in _cleaned_state_data dict (which is used by renderer to output data)
        """
        if cleaned:
            self._cleaned_state_data[key] = value
        else:
            self._raw_state_data[key] = value

    def _prepare_state_data(self):
        def _format_date(date_string):
            pattern = re.compile(r"(\.[0-9]*)?\+[0-9]*\:[0-9]*$")
            pattern_match = pattern.search(date_string)
            if pattern_match:
                date_string = date_string.replace(pattern_match.group(0), "")
            date_time_obj = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')

            date = date_time_obj.date()
            time = date_time_obj.time()

            return f"{date} {time}"
        def null_or_number(n): return n if isinstance(n, int) else 0

        for k, v in self._raw_state_data.items():

            if k in ['created', 'modified']:
                self._cleaned_state_data[k] = _format_date(v)
            elif k == 'percent':
                self._cleaned_state_data[k] = null_or_number(v)
            elif k == 'languages':
                self._cleaned_state_data[k] = filter(
                    lambda x: x != '', v.split(',')
                )
            elif k == 'everyone':
                if self._raw_state_data['everyone']:
                    everyone_string = "Yes"
                elif self._raw_state_data['everyone'] is False:
                    everyone_string = "No"
                else:
                    everyone_string = "Unknown"
                self._cleaned_state_data[k] = everyone_string
            elif k in ['users', 'groups']:
                self._cleaned_state_data[k] = len(list(filter(
                    lambda x: x not in ['null', 'Null', 'NULL', 'None'], v
                )))
            elif k == "course_overrides":
                courses_forced_on = [course for course in v if course["force"] == "on"]
                courses_forced_off = [course for course in v if course["force"] == "off"]
                self._cleaned_state_data["num_courses_forced_on"] = len(courses_forced_on)
                self._cleaned_state_data["num_courses_forced_off"] = len(courses_forced_off)
            else:
                self._cleaned_state_data[k] = v
        self._cleaned_state_data["env_name"] = self.env_name
        self._cleaned_state_data["toggle_type"] = self.toggle_type
