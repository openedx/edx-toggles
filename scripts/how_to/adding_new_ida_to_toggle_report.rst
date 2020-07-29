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
  - `gather annotation job groovy specification`_
  - `Jenkins Job folder`_


.. _writing anntations: https://code-annotations.readthedocs.io/en/latest/writing_annotations.html
.. _code_annotations: https://www.github.com/edx/code-annotations
.. _gather annotation job groovy specification: https://github.com/edx/jenkins-job-dsl-internal/blob/master/jobs/tools-edx-jenkins.edx.org/createFeatureToggleReportGeneratorJobs.groovy
.. _Jenkins Job folder: https://tools-edx-jenkins.edx.org/job/Feature-Toggle-Report-Generator/

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

Improvements
~~~~~~~~~~~~

State Data from Database
------------------------


Processing Data
===============

Publishing Data
===============