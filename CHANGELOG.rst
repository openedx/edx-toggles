Change Log
----------

..
   All enhancements and patches to edx_toggles will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
~~~~~~~~~~

[0.3.0] - 2020-07-27
~~~~~~~~~~~~~~~~~~~~

* Add ``featuretoggles`` Sphinx extension
* Added output for waffle flag course overrides to data gatherer
* Upgraded dependencies
* Added more options to scripts/feature_toggle_report_generator
    - filter toggle types and envs, add github_url, and change name of ida in report
* Modified scripts/feature_toggle_report_generator to work based on envs
* Added CsvRenderer
* Removed confluence integration
* Moved HtmlRenderer to its own file
    - getting files ready to add a CsvResnderer

[NOTE: None of these versions have actually been released to PyPI, even though
the version number has been bumped.]

[0.2.1] - 2020-05-27
~~~~~~~~~~~~~~~~~~~~

* Removed caniusepython3.

[0.2.0] - 2020-05-05
~~~~~~~~~~~~~~~~~~~~

* Added support for python 3.8 and dropped support Django versions older than 2.2

[0.1.0] - 2019-04-08
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Initial version
