Feature Toggle Reporter:
------------------------

We make extensive use of a variety of feature toggles at edX. However, it has
the downside of making the state of a deployed application somewhat opaque.
This tool anaylzes data from the codebases of deployed applications, as well
as their databases, to provide a summary of the feature toggles in use in a
given deployment. For more information, please see:

https://open-edx-proposals.readthedocs.io/en/latest/oep-0017-bp-feature-toggles.html

Prerequisites:
--------------

In order to create a feature toggle report for a given deployment, you need
two types of data: feature toggle annotation data and feature toggle data from
an application's database.

Feature Toggle Annotation Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use instructions found in `get feature toggles annotation data document <https://edx-toggles.readthedocs.io/en/latest/how_to/documenting_new_feature_toggles.html>`__ to collect annotations data.

Rename the resulting yml file `<ida_name>-annotations.yml`. This step is
necessary, as the feature toggle report generator will key off the `ida_name`
in the filename in order to be able to link this data to the toggle state data
collected in the next step. Create a directory called `annotation-data`, and
place the resulting annotation report from each IDA into this directory.

Feature Toggle State Data
~~~~~~~~~~~~~~~~~~~~~~~~~

The current state of certain feature toggles (i.e. django-waffle, waffle-utils)
is not captured in the codebase, as it is decoupled from the deployment of
code. Rather, it must read from the database of an application.

Assuming you have a provisioned `devstack`_, run the following make command
in devstack to generate the feature toggle state data files.

.. code:: bash

    make feature-toggle-state

This will create a new directory called `feature-toggle-data`, containing
a data dump file for each ida that makes use of waffle feature toggles.

NOTE: To run this against a real environment, you will need to set the following
environment variables (the defaults work with devstack):

* DB_USER
* DB_PASSWORD
* DB_HOST
* DB_PORT

Additionally, you must set an environment variable to specify the database
name for each IDA that you are querying about, in following form:
<ida_name>_DB. For example:
* LMS_DB

Creating a Feature Toggle Report
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Assuming you have the two prerequisites mentioned above, install the
dependencies for the report generator, and run it, passing the following
values on the command line:


For example:

To get help output for script:

.. code:: bash

    python -m scripts.feature_toggle_report --help

To generate default report:

.. code:: bash

    python -m scripts.feature_toggle_report annotation_dir_path toggle_data_dir_path output_path

To generate report with data for specific envs and toggle types:

.. code:: bash

    python -m scripts.feature_toggle_report annotation_dir_path toggle_data_dir_path output_path --env devstack --env prod --toggle-type WaffleFlag --toggle-type WaffleSwitch

By default, the generated report contains only essential information. To get a csv containing all information in state data and annotation data, add --verbose_report flag:

.. code:: bash

    python -m scripts.feature_toggle_report annotation_dir_path toggle_data_dir_path output_path --verbose_report

IMPORTANT: Example of annotations_dir structure:
    - annotations_dir/
        -  lms_annotations.yml
        - discovery_annotations.yml
    - toggle_data_dir
        - prod_env/
            - lms_waffle.json
            - discovery_waffle.json
        - stage_env
            - lms_waffle.json
            - discovery_waffle.json

IMPORTANT: toggles_data_dir can have two structures:
    - toggle_data_dir/
        - prod_env/
            - lms_waffle.json
            - discovery_waffle.json
        - stage_env/
            - lms_waffle.json
            - discovery_waffle.json

or
    - prod_env/ (name of toggle_data_dir)
        - lms_waffle.json
        - discovery_waffle.json

    The files should follow the pattern of {ida_name}_annotations.yml or {ida_name}_*.json.
    Note: ida_name is used by report generator and is included in final output.

Configuration file for report generator script:

The script can also take a yaml file as configuration, though command-line options will overwrite things in configuration. For example: see scripts/configuration.yaml

Valid keys in configuration file:
    - env: list the envs you want included in report
    - toggle_type: list the toggle types you want in report
    - ida: list configurations settings for each ida, following are valid keys under ida:
        - github_url: url to github repository for that ida
        - rename: a new name to replace the ida name used in the file names. example: lms => edxapp

.. _devstack: https://www.github.com/edx/devstack
