"""
Toggle state report API.
"""
from collections import OrderedDict

from django.conf import settings
from edx_django_utils.monitoring import get_code_owner_from_module
from waffle.models import Flag, Switch

from edx_toggles.toggles import SettingDictToggle, SettingToggle, WaffleFlag, WaffleSwitch


class ToggleStateReport:
    """
    Convenient class to collect toggle objects across a codebase and expose them via a REST API.

    Many methods are overridable to expose custom toggle objects in different IDAs.

    Use as follows:

        report = ToggleStateReport().as_dict()
    """

    def as_dict(self):
        """
        Produce a JSON-convertible report dict.

        Return:
            report (OrderedDict): this contains following keys: "waffle_flags", "waffle_switches", "django_settings".
        """
        report = OrderedDict()
        report["waffle_flags"] = sorted_values_by_name(self.get_waffle_flags())
        report["waffle_switches"] = sorted_values_by_name(self.get_waffle_switches())
        report["django_settings"] = sorted_values_by_name(self.get_django_settings())
        return report

    def get_waffle_flags(self):
        """
        Get all waffle flags and their state, indexed by name.
        """
        flags_dict = {}
        self.add_waffle_flag_instances(flags_dict)
        self.add_waffle_flag_state(flags_dict)
        self.add_waffle_flag_computed_status(flags_dict)
        return flags_dict

    def add_waffle_flag_instances(self, flags_dict):
        """
        Add waffle flag instances, indexed by name.
        """
        _add_waffle_flag_instances(flags_dict)

    def add_waffle_flag_state(self, flags_dict):
        """
        Add extra fields to some flag.
        """
        _add_waffle_flag_state(flags_dict)

    def add_waffle_flag_computed_status(self, flags_dict):
        """
        Add "computed_status" key to each waffle flag.
        """
        for flag in flags_dict.values():
            flag["computed_status"] = self.get_waffle_flag_computed_status(flag)

    def get_waffle_flag_computed_status(self, flag):
        """
        Return the computed status of a flag.
        """
        return _get_waffle_flag_computed_status(flag)

    def get_waffle_switches(self):
        """
        Get all waffle switches, indexed by name.
        """
        return _get_all_waffle_switches()

    def get_django_settings(self):
        """
        Get all Django settins, indexed by name.
        """
        return _get_settings_state()


def sorted_values_by_name(entries):
    """
    Return the dict values sorted by their "name" key.
    """
    return sorted(entries.values(), key=lambda entry: entry["name"])


def get_or_create_toggle_response(toggles_dict, toggle_name):
    """
    Gets or creates a toggle response dict and adds it to the toggles_dict.

    Return:
        Either the pre-existing toggle response, or a new toggle dict with the "name" key.
    """
    if toggle_name in toggles_dict:
        return toggles_dict[toggle_name]
    toggle = OrderedDict()
    toggle["name"] = toggle_name
    toggles_dict[toggle_name] = toggle
    return toggle


def _get_all_waffle_switches():
    """
    Gets all waffle switches and their state.
    """
    switches_dict = {}
    _add_waffle_switch_instances(switches_dict)
    _add_waffle_switch_state(switches_dict)
    _add_waffle_switch_computed_status(switches_dict)
    return switches_dict


def _add_waffle_switch_instances(switches_dict):
    """
    Add details from waffle switch instances, like code_owner.
    """
    waffle_switch_instances = WaffleSwitch.get_instances()
    for switch_instance in waffle_switch_instances:
        switch = get_or_create_toggle_response(switches_dict, switch_instance.name)
        _add_toggle_instance_details(switch, switch_instance)


def _add_waffle_switch_state(switches_dict):
    """
    Add waffle switch state from the waffle Switch model.
    """
    waffle_switches = Switch.objects.all()
    for switch_data in waffle_switches:
        switch = get_or_create_toggle_response(switches_dict, switch_data.name)
        switch["is_active"] = "true" if switch_data.active else "false"
        if switch_data.note:
            switch["note"] = switch_data.note
        switch["created"] = str(switch_data.created)
        switch["modified"] = str(switch_data.modified)


def _add_waffle_switch_computed_status(switch_dict):
    """
    Add computed status to each waffle switch.
    """
    for switch in switch_dict.values():
        computed_status = "on" if switch.get("is_active") == "true" else "off"
        switch["computed_status"] = computed_status


def _add_waffle_flag_instances(flags_dict):
    """
    Add details from waffle flag instances, like code_owner.
    """
    waffle_flag_instances = WaffleFlag.get_instances()
    for flag_instance in waffle_flag_instances:
        flag = get_or_create_toggle_response(flags_dict, flag_instance.name)
        _add_toggle_instance_details(flag, flag_instance)


def _add_waffle_flag_state(flags_dict):
    """
    Add waffle flag state from the waffle Flag model.

    This sets the following keys: "everyone", "created", "modified".
    """
    for flag_data in Flag.objects.all():
        if flag_data.everyone is True:
            everyone = "yes"
        elif flag_data.everyone is False:
            everyone = "no"
        else:
            everyone = "unknown"
        flag = get_or_create_toggle_response(flags_dict, flag_data.name)
        flag["everyone"] = everyone
        if flag_data.note:
            flag["note"] = flag_data.note
        flag["created"] = str(flag_data.created)
        flag["modified"] = str(flag_data.modified)


def _get_waffle_flag_computed_status(flag):
    """
    Return the computed status of a flag.

    This status depends on the value of the "everyone" entry:

        everyone == "yes"     -> computed = "on"
        everyone == "no"      -> computed = "off"
        everyone == "unknown" -> computed = "both"
    """
    everyone = flag.get("everyone")
    if everyone == "yes":
        return "on"
    if everyone == "unknown":
        return "both"
    return "off"


def _get_settings_state():
    """
    Return a list of setting-based toggles: Django settings, SettingToggle and SettingDictToggle instances.
    SettingToggle and SettingDictToggle override the settings with identical names (if any).
    """
    settings_dict = {}
    _add_settings(settings_dict)
    _add_setting_toggles(settings_dict)
    _add_setting_dict_toggles(settings_dict)
    return settings_dict


def _add_settings(settings_dict):
    """
    Fill the `settings_dict`: will only include values that are set to true or false.
    """
    for setting_name, setting_value in vars(settings).items():
        if isinstance(setting_value, dict):
            for dict_name, dict_value in setting_value.items():
                if isinstance(dict_value, bool):
                    name = setting_dict_name(setting_name, dict_name)
                    toggle_response = get_or_create_toggle_response(settings_dict, name)
                    toggle_response["is_active"] = dict_value
        elif isinstance(setting_value, bool):
            toggle_response = get_or_create_toggle_response(settings_dict, setting_name)
            toggle_response["is_active"] = setting_value


def _add_setting_toggles(settings_dict):
    """
    Fill the `settings_dict` with values from the list of SettingToggle instances.
    """
    for toggle in SettingToggle.get_instances():
        toggle_response = get_or_create_toggle_response(settings_dict, toggle.name)
        toggle_response["is_active"] = toggle.is_enabled()
        _add_toggle_instance_details(toggle_response, toggle)


def _add_toggle_instance_details(toggle, toggle_instance):
    """
    Add details (class, module, code_owner) from a specific toggle instance.
    """
    toggle["class"] = toggle_instance.__class__.__name__
    toggle["module"] = toggle_instance.module_name
    if toggle_instance.module_name:
        code_owner = get_code_owner_from_module(toggle_instance.module_name)
        if code_owner:
            toggle["code_owner"] = code_owner


def _add_setting_dict_toggles(settings_dict):
    """
    Fill the `settings_dict` with values from the list of SettingDictToggle instances.
    """
    for toggle in SettingDictToggle.get_instances():
        name = setting_dict_name(toggle.name, toggle.key)
        toggle_response = get_or_create_toggle_response(settings_dict, name)
        toggle_response["is_active"] = toggle.is_enabled()
        _add_toggle_instance_details(toggle_response, toggle)


def setting_dict_name(dict_name, key):
    """
    Return the name associated to a `dict_name[key]` setting.
    """
    return "{dict_name}['{key}']".format(dict_name=dict_name, key=key)
