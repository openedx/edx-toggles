.. _adding_new_ida:

=============================================
How-to: Enabling toggles report for a new IDA
=============================================

The generation of toggles report for an IDA has been automated for the LMS.
This document lists what needs to be done to automate toggle report generation for other IDAs.
There are a number of references in here that are specific to edX.org's
automation infrastructure and internal configuration repos,
but there should be enough detail provided for Open edX users to set up something similar.

.. contents:: Steps

Gathering Data
==============

Annotation data
---------------
The toggles are annotated in code following edX code annotation: `writing annotations`_.
The `code_annotations`_ tool is used to collect annotations into a report.

The steps to collect annotations are automated through a jenkins job:

- `groovy job specification`_ in ``generate-code-annotation-report``
- `Jenkins Job folder`_
- Once the job is done, the annotations data is pushed to an S3 bucket: `script to push data to s3 bucket`_

The job creates files with names like `<ida_name>-annotations.yml`.
The feature toggle report generator will key off the `ida_name`
in the filename in order to be able to link this data to the toggle state data
collected in the next step.

.. _writing annotations: https://code-annotations.readthedocs.io/en/latest/writing_annotations.html
.. _code_annotations: https://github.com/edx/code-annotations

Steps
~~~~~

- Add a `generate-feature-toggle-annotation-report.sh`_ to repository, use linked file as example
- Add IDA specification in ``scripts/configuration.yaml``
- Checkout your IDA code repository in the Jenkins job using a ``git`` block:

.. code:: java

        git {
            remote {
                url(<IDA_GIT_REPO_URL>)
            }
            branch('*/master')
            extensions {
                cleanAfterCheckout()
                pruneBranches()
                relativeTargetDirectory(${target_directory})
            }
        }

- Add virtualenv step to run annotation generation

.. code:: java

    virtualenv {
        pythonName('System-CPython-3.6')
        clear(true)
        systemSitePackages(false)
        nature('shell')
        ignoreExitCode(false)
        command(
            "cd <IDA_CHECKOUT_DIR>\n scripts/generate-feature-toggle-annotation-report.sh"
        )
    }


.. _generate-feature-toggle-annotation-report.sh: https://github.com/edx/edx-platform/blob/master/scripts/generate-feature-toggle-annotation-report.sh


Problems with current approach
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* If job fails:

    - It will block collection of annotation in other repositories
    - Arch-bom is alway notified on failure
    - Fix: Use the same approach as the upgrade jobs, create multiple jobs based on list which contains repository link, and contact email. One job per IDA/repository.

* Need to add custom script to every IDA that needs to be in IDA repository

    - Fix: create shell script in job to do the job instead. ``code_annotations`` should be able to work across repositories and any custom commands should not be necessary



State data from HTTP endpoint
-----------------------------
Toggles state is stored in the database for each deployment and must be retrieved
either directly from the database or via the application.

Collection of state data is automated through a jenkins job.

- `groovy job specification`_  in ``gather-${ida['name']}-${environment}-feature-toggle-state`` job
- `Jenkins Job folder`_
- Once the job is done, the state data is pushed to an S3 bucket: `script to push data to s3 bucket`_

Steps
~~~~~
- Add the edx-toggles Django app to the IDA:

    - Include ``edx-toggles`` in the ``base.in`` requirements file.
      It provides a Django view that allows staff users to retrieve
      a JSON document containing the boolean waffle switches and settings.
      (**TODO:** Not yet possible! Functionality still in ``waffle_utils`` in edx-platform;
      will be moved into edx-toggles.)
    - Add it to your ``urls.py``: ``url(r'^api/toggles/', include('edx_toggles.views.TODO'))``
      (**TODO:** As above, and names have yet to be decided.)

- Add environment specification for your database to `edx-internal/*/feature-toggle-report-generator.yml`_


Problems with current approach
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- The toggle state Django app hasn't been moved into edx-toggles yet,
  so this only works for the LMS so far

.. _edx-internal/*/feature-toggle-report-generator.yml: https://github.com/edx/edx-internal/blob/master/tools-edx-jenkins/feature-toggle-report-generator.yml


Processing Data
===============

`feature_toggle_report_generator.py`_


The annotation data and Toggle state data dump should be stored in s3 buckets. The automated publish-feature-toggle-report job (in `groovy job specification`_) pulls the data from s3 buckets and calls `feature_toggle_report_generator.py`_ to process  the data and output it as a csv file.

As long as the data is structured correctly (specified in `README`_), nothing should be necessary

possible improvements
---------------------

* Add ability to filter idas in report



Publishing Data
===============

As of now, the toggle csv reports are retained as artifacts in Jenkins job: `publish-feature-toggle-report`_.

The plan is to eventually find a different home for it (possibly in google sheets).


.. _Jenkins Job folder: https://tools-edx-jenkins.edx.org/job/Feature-Toggle-Report-Generator
.. _groovy job specification: https://github.com/edx/jenkins-job-dsl-internal/blob/master/jobs/tools-edx-jenkins.edx.org/createFeatureToggleReportGeneratorJobs.groovy
.. _script to push data to s3 bucket: https://github.com/edx/jenkins-job-dsl-internal/blob/master/resources/push-feature-toggle-data-to-s3.sh
.. _script to pull data from s3 bucket: https://github.com/edx/jenkins-job-dsl-internal/blob/master/resources/pull-feature-toggle-data-from-s3.sh
.. _feature_toggle_report_generator.py: https://github.com/edx/edx-toggles/blob/master/scripts/feature_toggle_report_generator.py
.. _publish-feature-toggle-report: https://tools-edx-jenkins.edx.org/job/Feature-Toggle-Report-Generator/job/publish-feature-toggle-report/

.. _README: https://github.com/edx/edx-toggles/blob/master/scripts/README.rst
