=====================================
Enabling Toggles Report for a new IDA
=====================================

.. contents:: Steps

Gathering Data
==============

Annotation Data
---------------
The toggles are should be annotated in code following edX code annotation:`writing annotations`_. The `code_annotations`_ tool is used to collect annotations into a report.

The steps to collect annotations is automated through a jenkins job
  - `groovy job specification`_ in "generate-code-annotation-report"
  - `Jenkins Job folder`_
  - once the job is done, its data is pushed to s3 bucket: `script to push data to s3 bucket`_


.. _writing anntations: https://code-annotations.readthedocs.io/en/latest/writing_annotations.html
.. _code_annotations: https://www.github.com/edx/code-annotations

steps
~~~~~
* add a `generate-feature-toggle-annotation-report.sh`_ to repository, used linked file as example
* checkout your IDA code repository in groovy using git block
.. code:: java

    git {
            remote {
                url(Link to IDA code)
            }
            branch('*/master')
            extensions {
                cleanAfterCheckout()
                pruneBranches()
                relativeTargetDirectory(${target_directory})
            }
        }


* add virtualenv step to run annotation generation

.. code:: java

        virtualenv {
            pythonName('System-CPython-3.5')
            clear(true)
            systemSitePackages(false)
            nature('shell')
            ignoreExitCode(false)
            command(
                "cd ${target_directory}\nbash scripts/generate-feature-toggle-annotation-report.sh"
            )
        }
.. _generate-feature-toggle-annotation-report.sh: https://github.com/edx/edx-platform/blob/master/scripts/generate-feature-toggle-annotation-report.sh



problems with current approach
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* if job fails
    - it will block collection of annotation in other repositories
    - archbom is alway notified on faliure
    - fix: Use to same approach as the upgrade jobs, create multiple jobs based on list which contains repository link, and contact email. One job per IDA/repository
* need to add custom script to every IDA that needs to be in IDA repository
    - fix: create shell script in job to do the job instead. code_annotations should be able to work accorss repositories and any custom commands should not be necessary



State Data from Database
------------------------
Toggles states are stored in the database for each production environment. The database is queried using `gather_feature-toggle_state.py`_.

.. _gather_feature-toggle_state.py: https://github.com/edx/edx-toggles/blob/master/scripts/gather_feature_toggle_state.py

The steps to collect annotations is automated through a jenkins job
  - `groovy job specification`_  in "gather-${environment}-feature-toggle-state" job
  - `Jenkins Job folder`_
  - The specifications for each database is located at: `edx-internal/*/feature-toggle-report-generator.yml`_
  - once the job is done, its data is pushed to s3 bucket: `script to push data to s3 bucket`_

steps
~~~~~
  - add IDA specification in main function in `gather_feature_toggle_state.py`_
  - add specification for your database to `edx-internal/*/feature-toggle-report-generator.yml`_

problems with current approach
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* the code to gather database info has somethings that are very specific to lms
    - fix: make things more general
        + this should not be too difficult


.. _edx-internal/*/feature-toggle-report-generator.yml: https://github.com/edx/edx-internal/blob/master/tools-edx-jenkins/feature-toggle-report-generator.yml
.. _gather_feature_toggle_state.py: https://github.com/edx/edx-toggles/blob/master/scripts/gather_feature_toggle_state.py


Processing Data
===============

`feature_toggle_report_generator.py`_


The annotation data and Toggle state data dump should be stored in s3 buckets. The automated publish-feature-toggle-report job(in `groovy job specification`_) pulls the data from s3 buckets and calls `feature_toggle_report_generator.py`_ to process  the data and output it as a csv file. 

As long as the data is structured correctly(specified in `README`_), nothing should be necessary

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
