"""
Common classes to represent toggles withint IDAs.
"""
import collections
import re
import logging


LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Toggle:
    """
    Represents a feature toggle in an IDA, including the current state of the
    toggle in the database and any additional information defined in the
    source code (marked via `code-annotations`). To account for the case in which
    a feature toggle is not yet annotated or has been removed from the database
    but not the source code, this constructor can handle the case in which
    only one of the above components could be identified.
    """

    def __init__(self, name, state=None, annotations=None):
        self.name = name
        self.state = state
        self.annotations = annotations

    def __str__(self):
        return self.name

    @property
    def state_msg(self):
        """
        The human readable representation of whether or not this toggle is
        turned on.
        """
        if not self.state:
            return "Not found in database"
        elif self.state.state:
            return "On"
        else:
            return "Off"

    def data_for_template(self, component, data_name):
        """
        A helper function for easily accessing various data from both
        the ToggleState and ToggleAnnotations for this Toggle for
        use in templating the confluence report.
        """
        if component ==  "state":
            if self.state:
                self.state._prepare_state_data()
                return self.state._cleaned_state_data[data_name]
            else:
                return '-'
        elif component == "annotation":
            if self.annotations:
                self.annotations._prepare_annotation_data()
                return self.annotations._cleaned_annotation_data[data_name]
            else:
                return '-'

    def full_data(self):
        """
        Returns a dict with all info on toggle state and annotations
        """
        full_data = {}
        full_data["name"] = self.name
        if self.state:
            self.state._prepare_state_data()
            for key, value in self.state._cleaned_state_data.items():
                if key == "name":
                    continue
                # data that is received from state data dump is postfixed with a "_s"
                full_data["{}_s".format(key)] = value
        else:
            LOGGER.debug("{} Toggle's state is None".format(self.name))

        if self.annotations:
            self.annotations._prepare_annotation_data()
            for key, value in self.annotations._cleaned_annotation_data.items():
                if key == "name":
                    continue
                # data that is received from annotations is postfixed with a "_a"
                full_data["{}_a".format(key)] = value
        else:
            LOGGER.debug("{} Toggle's annotations is None".format(self.name))
        return full_data


class ToggleAnnotation(object):
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


class ToggleState(object):
    """
    Represents the state of a feature toggle, configured within an IDA,
    as pulled from the IDA's database.
    """

    def __init__(self, toggle_type, data):
        self.toggle_type = toggle_type
        self._raw_state_data = data
        self._cleaned_state_data = collections.defaultdict(str)

    def get_datum(self, key, cleaned=True):
        """
        get data from either _raw_state_data dict or _cleaned_state_data dict

        Arguments:
            key: the key name for data
            cleaned: Whether to get datum from _raw_state_data dict or _cleaned_state_data
                By default, this will get datum to _cleaned_state_data:
        """
        if cleaned:
            self._prepare_state_data()
            return self._cleaned_state_data.get(key, str())
        else:
            return self._raw_state_data.get(key, str())

    def set_datum(self, key, value, cleaned=True):
        """
        Adding data to either _raw_state_data dict or _cleaned_state_data dict
        
        Arguments:
            key: key name for addition to dict
            value: data to add to dict
            cleaned: Whether to add data to _raw_state_data dict or _cleaned_state_data
                By default, this will add datum to _cleaned_state_data:
                    Using this functions allows you to skip the _prepare_state_data function call and put
                    datum directly in _cleaned_state_data dict(which is used to out data)
        """
        if cleaned:
            self._cleaned_state_data[key] = value
        else:
            self._raw_state_data[key] = value

    @property
    def state(self):
        """
        Return the overall state of the toggle. In other words, is it on or off
        """

        def bool_for_null_numbers(n):
            if n == 'null':
                return False
            elif isinstance(n, int):
                return int(n) > 0
            else:
                return False

        def bool_for_null_lists(l):
            if l:
                return any(
                    map(lambda x: x not in ['null', 'Null', 'NULL', 'None'], l)
                )
            else:
                return False

        if self.toggle_type == 'WaffleSwitch':
            return self._raw_state_data['active']
        elif self.toggle_type == 'WaffleFlag':
            # the WaffleFlag option `everyone` overrides all other options.
            # However, it must be explicitly set to Yes(True) or No(False)
            # in the GUI. Otherwise, it is set to Unknown(None) and WaffleFlag
            # defers to the other options to determine the state of the flag.
            if self._raw_state_data['everyone']:
                return True
            elif self._raw_state_data['everyone'] is False:
                return False
            else:
                return (
                    bool_for_null_numbers(self._raw_state_data['percent']) or
                    self._raw_state_data['testing'] or
                    self._raw_state_data['superusers'] or
                    self._raw_state_data['staff'] or
                    self._raw_state_data['authenticated'] or
                    bool(self._raw_state_data['languages']) or
                    bool_for_null_lists(self._raw_state_data['users']) or
                    bool_for_null_lists(self._raw_state_data['groups'])
                )

    def _prepare_state_data(self):
        def _format_date(date_string):
            datetime_pattern = re.compile(
                r'(?P<date>20\d\d-\d\d-\d\d)T(?P<time>\d\d:\d\d):\d*.*'
            )
            offset_pattern = re.compile(
                r'.*T\d\d:\d\d:\d+.*(?P<offset>[Z+-].*)'
            )
            date = re.search(datetime_pattern, date_string).group('date')
            time = re.search(datetime_pattern, date_string).group('time')
            offset = re.search(offset_pattern, date_string).group('offset')

            if offset == 'Z':
                offset = 'UTC'

            return "{} {} {}".format(date, time, offset)
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
                courses_with_flag_on = [course for course, value in v.items() if value == "on"]
                courses_with_flag_off = [course for course, value in v.items() if value == "off"]
                self._cleaned_state_data["num_courses_on"] = len(courses_with_flag_on)
                self._cleaned_state_data["num_courses_off"] = len(courses_with_flag_off)
            else:
                self._cleaned_state_data[k] = v
