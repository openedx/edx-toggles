.. _adding_new_ida:

************************************************
How-to: Enabling toggles reporting for a new IDA
************************************************

There are three ways to report on feature toggles in an Independently Deployable Application (IDA).

.. list-table::

    - - `IDA Toggles List on Readthedocs`_
      - Generated documentation based on annotated feature toggles.
    - - `Toggles State Endpoint`_
      - REST endpoint providing the current state of feature toggles at a given time from a given environment.
    - - `Toggles State Reports Spreadsheet`_
      - A generated spreadsheet combining data from the static feature toggle annotations and the toggle state data from the Toggles State Endpoint.

IDA Toggles List on Readthedocs
===============================

You can extract your toggle annotations from code in order to create documentation on Readthedocs for your IDA.

Here are some helpful examples and resources:

* Sample `readthedocs documention for edx-platform feature toggles`_.
* Based on `annotated toggles in the edx-platform codebase`_.
* See :doc:`documenting_new_feature_toggles`

Steps required (2-4 hours):

- Copy ``featurestoggles.rst`` and configuration for the ``featuretoggles`` Sphinx extension from edx-platform.

    - Here is a `search for featuretoggles in edx-platform`_.

.. note::

    You can follow similar steps to use the settings Sphinx extension to publish non-boolean non-toggle setting annotations as well.

.. _readthedocs documention for edx-platform feature toggles: https://edx.readthedocs.io/projects/edx-platform-technical/en/latest/featuretoggles.html
.. _annotated toggles in the edx-platform codebase: https://github.com/openedx/edx-platform/search?q=toggle_name
.. _search for featuretoggles in edx-platform: https://github.com/openedx/edx-platform/search?q=featuretoggles

Toggles State Endpoint
======================

Add a REST endpoint to your IDA that provides the current state of all your toggles, including all ``waffle`` toggles and all boolean Django Settings. This endpoint will be available from all environments, including Production.

Here is an example from edx-platform:

* https://courses.edx.org/api/toggles/v0/state/ (requires Staff access)

Steps required (2-4 hours):

- Add a view wrapping ``ToggleStateReport().as_dict()`` for your new toggle state REST endpoint:

  - Include ``edx-toggles`` in the ``base.in`` requirements file (if not already there).
  - Create a view using the ToggleStateReport_ class to implement the REST endpoint.

    - Our convention is to use the path ``/api/toggles/v0/state/``.
    - Protect the view as a appropriate, potentially limiting to Staff access.
    - See an `example toggles state endpoint view`_ in edx-platform.

        - For most IDAs, just replace ``report = CourseOverrideToggleStateReport().as_dict()`` with ``report = ToggleStateReport().as_dict()`` from the example code.

    - Add the view to a ``urls.py`` like in this `example urls.py in edx-platform`_.

    - (Optional) If your IDA has custom toggle types, you can subclass and override the reporting methods as was done in the edx-platform `example toggles state endpoint view`_.

.. _ToggleStateReport: https://edx.readthedocs.io/projects/edx-toggles/en/latest/edx_toggles.toggles.state.internal.html#module-edx_toggles.toggles.state.internal.report
.. _example toggles state endpoint view: https://github.com/openedx/edx-platform/blob/650b0c1/openedx/core/djangoapps/waffle_utils/views.py#L50-L66
.. _example urls.py in edx-platform: https://github.com/openedx/edx-platform/blob/650b0c13603468d33e3e629ef1e36acc8fefd683/openedx/core/djangoapps/waffle_utils/urls.py
.. _supported toggle classes from edx-toggles: https://edx.readthedocs.io/projects/edx-toggles/en/latest/how_to/implement_the_right_toggle_type.html#implementing-the-right-toggle-class

Toggles State Reports Spreadsheet
=================================

.. note:: Much of this section is specific to edX.org, including private links, but the general approach and some of the scripts are available to the wider Open edX community.

Add an IDA to the spreadsheet which combines data from the static feature toggle annotations and the toggle state data.

See the current `Toggle State Reports Spreadsheet (private to edX.org)`_.

Prerequisites:

- Implement the `Toggles State Endpoint`_ in your IDA.

Steps required (1 hour):

- Add IDA specification to `feature-toggle-report-generator.yml`_ under ``idas`` key and each of the ``ENVIRONMENTS`` that are applicable.
- Add IDA specification in `scripts/configuration.yaml`_.

.. _Toggle State Reports Spreadsheet (private to edX.org): https://tinyurl.com/edx-toggles-state
.. _feature-toggle-report-generator.yml: https://github.com/edx/edx-internal/blob/master/tools-edx-jenkins/feature-toggle-report-generator.yml
.. _scripts/configuration.yaml: https://github.com/openedx/edx-toggles/blob/master/scripts/configuration.yaml

How the Toggle State Reports Spreadsheet is generated
=====================================================

This section describes how the Toggle State Reports Spreadsheet is generated. This information is **not** required knowledge for setting up a new IDA.

Gathering annotation data
-------------------------

See :doc:`documenting_new_feature_toggles` to understand the toggle annotations that will be gathered. The `code_annotations`_ tool is used to collect these annotations into a report.

The steps to collect annotations are automated through a Jenkins job:

- `groovy job specification`_ in ``generate-code-annotation-report``
- `Jenkins Job folder`_
- Once the job is done, the annotations data is pushed to an S3 bucket: `script to push data to s3 bucket`_

The job creates files with names like ``<ida_name>-annotations.yml``. The feature toggle report generator will key off the ``ida_name`` in the filename in order to be able to link this data to the toggle state data collected.

.. _code_annotations: https://github.com/openedx/code-annotations

Gathering state data from HTTP endpoint
---------------------------------------

Toggle state will be gathered from the new `Toggles State Endpoint`_.

Collection of state data is automated through a jenkins job.

- `groovy job specification`_  in ``gather-${ida['name']}-${environment}-feature-toggle-state`` job
- `Jenkins Job folder`_
- Once the job is done, the state data is pushed to an S3 bucket: `script to push data to s3 bucket`_

Processing annotation and state data
------------------------------------

The annotation data and toggle state data dump should be stored in s3 buckets. The automated publish-feature-toggle-report job (in `groovy job specification`_) pulls the data from s3 buckets and calls `feature_toggle_report_generator.py`_ to process  the data and output it as a csv file.

As long as the data is structured correctly (specified in `README`_), no action should be necessary for a new IDA.

Publishing data
---------------

The toggle csv reports are retained as artifacts in the Jenkins job: `publish-feature-toggle-report`_.

The csv reports are published to a private Google Sheet. See `Toggle State Reports Spreadsheet (private to edX.org)`_.

.. _Jenkins Job folder: https://tools-edx-jenkins.edx.org/job/Feature-Toggle-Report-Generator
.. _groovy job specification: https://github.com/edx/jenkins-job-dsl-internal/blob/master/jobs/tools-edx-jenkins.edx.org/createFeatureToggleReportGeneratorJobs.groovy
.. _script to push data to s3 bucket: https://github.com/edx/jenkins-job-dsl-internal/blob/master/resources/push-feature-toggle-data-to-s3.sh
.. _script to pull data from s3 bucket: https://github.com/edx/jenkins-job-dsl-internal/blob/master/resources/pull-feature-toggle-data-from-s3.sh
.. _feature_toggle_report_generator.py: https://github.com/openedx/edx-toggles/blob/master/scripts/feature_toggle_report_generator.py
.. _publish-feature-toggle-report: https://tools-edx-jenkins.edx.org/job/Feature-Toggle-Report-Generator/job/publish-feature-toggle-report/
.. _README: https://github.com/openedx/edx-toggles/blob/master/scripts/README.rst
