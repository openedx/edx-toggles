.. _report_for_devstack_or_sandbox:

=====================================================
How to: Create toggles report for devstack or sandbox
=====================================================

.. contents:: Steps to generate a toggle report for devstack


Grab toggles state data from endpoint
-------------------------------------

Use instructions found in `get feature toggles state data document <https://edx-toggles.readthedocs.io/en/latest/how_to/documenting_new_feature_toggles.html>`__ to collect state data from an ida.

The resulting file should be named following this pattern: `<ida_name>_.*json`.

The <ida_name> will be used to link this data with annotations data.

Structure state data directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To generate report, you will pass path to a directory containing state data to feature_toggle_report.py script. The script can handle 2 structures of this directory.

First create this empty directory. Now populate it with data based on either of these two use cases:


When creating report to compare multiple environments
+++++++++++++++++++++++++++++++++++++++++++++++++++++

For each env, create a directory named following this name pattern: `<env_name>_env`. Populate these env directories with their state value files (json).

Example:
    - toggle_data_dir/
        - prod_env/
            - lms_waffle.json
            - discovery_waffle.json
        - stage_env/
            - lms_waffle.json
            - discovery_waffle.json

When creating report for just one environment
+++++++++++++++++++++++++++++++++++++++++++++

For this use case, you can either follow the directory structure listed above, or do the following:

Create an empty directory following this name pattern: `<env_name>_env`. Populate it with state data json files.

Example:
    - prod_env/ (name of toggle_data_dir)
        - lms_waffle.json
        - discovery_waffle.json


Grab annotations data
---------------------

Use instructions found in `get feature toggles annotation data document <https://edx-toggles.readthedocs.io/en/latest/how_to/documenting_new_feature_toggles.html>`__ to collect annotations data.

Rename the resulting yml file `<ida_name>-annotations.yml`. This step is necessary, as the feature toggle report generator will key off the `ida_name` in the filename in order to be able to link this data to the toggle state data collected in the next step. Create a directory called `annotation-data`, and place the resulting annotation report from each IDA into this directory.

Structure annotations data files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Place all resulting annotations yml files in a single directory. The name of annotations directory does not matter.

Create Report
-------------

Use instructions found in `"Creating a Feature Toggle Report" section of Readme <https://github.com/edx/edx-toggles/blob/master/scripts/README.rst#creating-a-feature-toggle-report>`__ to generate report.
