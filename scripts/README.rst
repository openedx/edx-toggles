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

.. code:: bash

    code_annotations static_find_annotations --config_file feature_annotations.yaml

Rename the resulting yml file `<ida_name>_annotation_data.yml`. This step is
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

    python gather_feature_toggle_state.py feature-toggle-data

This will create a new directory called `feature-toggle-data`, containing
a data dump file for each ida that makes use of waffle feature toggles.

NOTE: To run this against a real environment, you will need to set the following
environment variables (the defaults work with devstack):
* DB_USER
* DB_PASSWORD
* DB_HOST
* DB_PORT

Usage:
------

Assuming you have the two prerequisites mentioned above, install the
dependencies for the report generator, and run it, passing the following
values on the command line:

    * feature-toggle-data: path to the sql dump data created above
    * annotation-data: path to the code annotation data created above
    * reports: path to write report files into

.. code:: bash

    make requirements
    python scripts/feature_toggle_report_generator.py feature-toggle-data annonation-data reports


.. _code_annotations: https://www.github.com/edx/code-annotations
.. _devstack: https://www.github.com/edx/devstack
