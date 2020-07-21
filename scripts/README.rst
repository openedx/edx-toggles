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

Feature toggles are first defined in the code of an application. We make use of
the `code_annotations`_ tool, to annotate and summarize the definitions of
these components with information regarding their purpose, default values and
planned expiration dates.

Here is an example of a fully annotated CourseWaffleFlag:

.. code:: python

    # .. toggle_name: course_experience.show_reviews_tool
    # .. toggle_implementation: CourseWaffleFlag
    # .. toggle_default: False
    # .. toggle_description: Used with our integration with CourseTalk to display reviews for a course.
    # .. toggle_category: course_experience
    # .. toggle_use_cases: monitored_rollout
    # .. toggle_creation_date: 2017-06-19
    # .. toggle_expiration_date: ???
    # .. toggle_warnings: We are no longer integrating with CourseTalk, so this probably should be deprecated and the code for reviews should be removed.
    # .. toggle_tickets: DEPR-48
    # .. toggle_status: unsupported
    SHOW_REVIEWS_TOOL_FLAG = CourseWaffleFlag(WAFFLE_FLAG_NAMESPACE, 'show_reviews_tool')

To run the code-annotations tool to collect annotations into a report, run the
command (in the codebase of your choice):

.. code:: bash

    code_annotations static_find_annotations --config_file feature_toggle_annotations.yaml

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

Assuming you have a provisioned `devstack`_, run the following make commands to
generate the feature toggle state data files.

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

    python -m scripts.feature_toggle_report_generator --help

To generate report with everything:

.. code:: bash

    python -m scripts.feature_toggle_report_generator annotation_dir_path toggle_data_dir_path output_path --show-state

To generate report with data for specific env and toggle type:

.. code:: bash

    python -m scripts.feature_toggle_report_generator annotation_dir_path toggle_data_dir_path output_path --show-state --env devstack --env prod --toggle-type WaffleFlag --toggle-type WaffleSwitch

IMPORTANT: Example of data structure:
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
    The files shoulod follow the pattern of {ida_name}_annotations.yml or {ida_name}_*.json. ida_name is used by report generator and is included in final output. TODO(jinder): does this comment make sense


.. _code_annotations: https://www.github.com/edx/code-annotations
.. _devstack: https://www.github.com/edx/devstack
