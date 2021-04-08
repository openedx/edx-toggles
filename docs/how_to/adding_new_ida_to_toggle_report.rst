.. _adding_new_ida:

=============================================
How-to: Enabling toggles report for a new IDA
=============================================

.. note:: Some of this document is specific to edX.org, but the general approach and some of the scripts are available to the wider Open edX community.

The generation of toggles report for an IDA has been automated for the LMS. This document lists what needs to be done to automate toggle report generation for other IDAs. There are a number of references in here that are specific to edX.org's automation infrastructure and internal configuration repos, but there should be enough detail provided for Open edX users to set up something similar.

.. contents:: Steps

Gathering Data
==============

Annotation data
---------------
The toggles are annotated in code following edX code annotation: `writing annotations`_. The `code_annotations`_ tool is used to collect annotations into a report.

The steps to collect annotations are automated through a jenkins job:

- `groovy job specification`_ in ``generate-code-annotation-report``
- `Jenkins Job folder`_
- Once the job is done, the annotations data is pushed to an S3 bucket: `script to push data to s3 bucket`_

The job creates files with names like `<ida_name>-annotations.yml`. The feature toggle report generator will key off the `ida_name` in the filename in order to be able to link this data to the toggle state data collected in the next step.

.. _writing annotations: https://github.com/edx/edx-toggles/blob/master/docs/how_to/documenting_new_feature_toggles.rst
.. _code_annotations: https://github.com/edx/code-annotations

Steps
~~~~~

- Add IDA specification to `feature-toggle-report-generator.yml`_ under ``idas`` key.
- Add IDA specification in `scripts/configuration.yaml`_.


Problems with current approach
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- If job fails, arch-bom is always notified, rather than the owning team.


State data from HTTP endpoint
-----------------------------

Toggles state is stored in the database for each deployment and must be retrieved either directly from the database or via the application.

Collection of state data is automated through a jenkins job.

- `groovy job specification`_  in ``gather-${ida['name']}-${environment}-feature-toggle-state`` job
- `Jenkins Job folder`_
- Once the job is done, the state data is pushed to an S3 bucket: `script to push data to s3 bucket`_

Steps
~~~~~

- Add a view for a toggle state REST endpoint:

  - Include ``edx-toggles`` in the ``base.in`` requirements file if not already there.
  - Create a view using the ToggleStateReport_ class to implement a REST endpoint.

    - Our convention is to use the path `/api/toggles/v0/state/`.
    - See an `example toggles state endpoint view`_ in edx-platform.

        - edx-platform sublasses the report to add in CourseOverrides.
        - For the default report, replace `report = CourseOverrideToggleStateReport().as_dict()` with `report = ToggleStateReport().as_dict()`.

    - Add the view to a ``urls.py`` like in this `example urls.py in edx-platform`_.

- Finally, add the IDA and environment details to the shared `feature-toggle-report-generator.yml`_.

.. _ToggleStateReport: https://edx.readthedocs.io/projects/edx-toggles/en/latest/edx_toggles.toggles.state.internal.html#module-edx_toggles.toggles.state.internal.report
.. _example toggles state endpoint view: https://github.com/edx/edx-platform/blob/650b0c1/openedx/core/djangoapps/waffle_utils/views.py#L50-L66
.. _example urls.py in edx-platform: https://github.com/edx/edx-platform/blob/650b0c13603468d33e3e629ef1e36acc8fefd683/openedx/core/djangoapps/waffle_utils/urls.py
.. _feature-toggle-report-generator.yml: https://github.com/edx/edx-internal/blob/master/tools-edx-jenkins/feature-toggle-report-generator.yml

Processing data
===============

The annotation data and Toggle state data dump should be stored in s3 buckets. The automated publish-feature-toggle-report job (in `groovy job specification`_) pulls the data from s3 buckets and calls `feature_toggle_report_generator.py`_ to process  the data and output it as a csv file.

As long as the data is structured correctly (specified in `README`_), no action should be necessary for a new IDA.

Publishing data
===============

As of now, the toggle csv reports are retained as artifacts in Jenkins job: `publish-feature-toggle-report`_.

The csv reports are published to a private google sheet. See the `Toggle State Reports spreadsheet link`_ from this private page.

.. _Jenkins Job folder: https://tools-edx-jenkins.edx.org/job/Feature-Toggle-Report-Generator
.. _groovy job specification: https://github.com/edx/jenkins-job-dsl-internal/blob/master/jobs/tools-edx-jenkins.edx.org/createFeatureToggleReportGeneratorJobs.groovy
.. _script to push data to s3 bucket: https://github.com/edx/jenkins-job-dsl-internal/blob/master/resources/push-feature-toggle-data-to-s3.sh
.. _script to pull data from s3 bucket: https://github.com/edx/jenkins-job-dsl-internal/blob/master/resources/pull-feature-toggle-data-from-s3.sh
.. _feature_toggle_report_generator.py: https://github.com/edx/edx-toggles/blob/master/scripts/feature_toggle_report_generator.py
.. _scripts/configuration.yaml: https://github.com/edx/edx-toggles/blob/master/scripts/configuration.yaml
.. _publish-feature-toggle-report: https://tools-edx-jenkins.edx.org/job/Feature-Toggle-Report-Generator/job/publish-feature-toggle-report/
.. _README: https://github.com/edx/edx-toggles/blob/master/scripts/README.rst
.. _Toggle State Reports spreadsheet link: https://openedx.atlassian.net/wiki/spaces/AT/pages/1398211515/Shared+links
