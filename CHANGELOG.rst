Change Log
----------

..
   All enhancements and patches to edx_toggles will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

[NOTE: None of these versions have actually been released to PyPI, even though
the version number has been bumped.]

[0.3.0] - 2020-09-23
~~~~~~~~~~~~~~~~~~~~

* Implement ``SettingToggle`` and ``SettingDictToggle``.

[0.2.2] - 2020-09-11
~~~~~~~~~~~~~~~~~~~~

* Document the writing of feature toggles annotations.

[0.2.1] - 2020-08-03
~~~~~~~~~~~~~~~~~~~~

* Add ADR for the purpose of this repository.
* Add ADR for implementing a Toggle State endpoint.
* Add toggles report with CSV output using new CsvRenderer.
* Add CourseWaffleFlag and course override data to toggle report.
* Add output for waffle flag course overrides to data gatherer
* Add additional options to scripts/feature_toggle_report_generator

    * filter toggle types and envs, add github_url, and change name of ida in report

* Modified scripts/feature_toggle_report_generator to work based on envs
* Removed confluence integration
* Moved HtmlRenderer to its own file
* Add ADR for new SettingToggle. (see 0003-django-setting-toggles.rst)

[0.2.0] - 2020-05-27
~~~~~~~~~~~~~~~~~~~~

* Removed caniusepython3.

[0.2.0] - 2020-05-05
~~~~~~~~~~~~~~~~~~~~

* Added support for python 3.8 and dropped support Django versions older than 2.2

[0.1.0] - 2019-04-08
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Initial version
