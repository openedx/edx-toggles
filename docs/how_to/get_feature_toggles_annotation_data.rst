.. _get_toggle_annotations:

How to: Get feature toggle annotation data
==========================================

Feature toggles are first defined in the code of an application. We make use of the `code_annotations`_ tool, to annotate and summarize the definitions of these components with information regarding their purpose, default values and planned expiration dates.

See the `How To with annotation format of feature toggles <https://edx-toggles.readthedocs.io/en/latest/how_to/documenting_new_feature_toggles.html>`__.

To run the code-annotations tool to collect annotations into a report, run the command (in the codebase of your choice):

.. code:: bash

    code_annotations static_find_annotations --config_file $VIRTUAL_ENV/lib/python3.11/site-packages/code_annotations/contrib/config/feature_toggle_annotations.yaml

.. _code_annotations: https://www.github.com/openedx/code-annotations
