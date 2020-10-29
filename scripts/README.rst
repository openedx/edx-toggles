Feature Toggle Reporter
-----------------------

We make extensive use of a variety of feature toggles at edX. However, it has the downside of making the state of a deployed application somewhat opaque. This tool analyzes data from the codebases of deployed applications, as well as their databases, to provide a summary of the feature toggles in use in a given deployment. For more information, please see:

https://open-edx-proposals.readthedocs.io/en/latest/oep-0017-bp-feature-toggles.html

In order to create a feature toggle report for a given deployment, you need two types of data: feature toggle annotation data and feature toggle state data from an application's database.

Feature Toggle Annotation Data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any toggles that are annotated according to the instructions in `get feature toggles annotation data document <docs/how_to/documenting_new_feature_toggles.html>`_ will be included in the report.


Feature Toggle State Data
~~~~~~~~~~~~~~~~~~~~~~~~~

The current state of certain feature toggles (i.e. django-waffle, waffle-utils) is not captured in the codebase, as it is decoupled from the deployment of code. Rather, it must read from the deployed application.

Each IDA exposes an HTTP endpoint provided by the [TODO: pending] edx-toggles Django app. A scheduled job can use an OAuth client associated with a staff user to get a JWT, and then use the JWT against each configured IDA's toggle state endpoint.

Creating a Feature Toggle Report
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Assuming you have already run the two prerequisites mentioned above, install the dependencies for the report generator, and run it, passing the following values on the command line:


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
        - lms_annotations.yml
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
