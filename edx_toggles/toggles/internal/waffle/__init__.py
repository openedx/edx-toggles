"""
Waffle classes in the context of edx-platform and other IDAs.

Usage:

For waffle flags::

    SOME_FLAG = WaffleFlag('some_namespace_prefix.some_feature', module_name=__name__)

For waffle switches::

    SOME_SWITCH = WaffleSwitch('some_namespace_prefix.some_feature', module_name=__name__)

The namespace prefix is used to categorize waffle objects.

For both flags and switches, the waffle value can be checked in code by writing::

    SOME_WAFFLE.is_enabled()

To test these WaffleFlags, see edx_toggles.toggles.testutils.

In the above examples, you will use Django Admin "waffle" section to configure
for a flag named: my_namespace.some_course_feature
"""
