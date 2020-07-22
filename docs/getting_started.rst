Getting Started
===============

If you have not already done so, create or activate a `virtualenv`_. Unless otherwise stated, assume all terminal code
below is executed within the virtualenv.

.. _virtualenv: https://virtualenvwrapper.readthedocs.org/en/latest/


Install dependencies
--------------------
Dependencies can be installed via the command below.

.. code-block:: bash

    $ make requirements

Using the ``featuretoggles`` Sphinx extension
---------------------------------------------

This package can be used to document the feature toggles in your code base. To do so,
add the following to your ``conf.py``::

    extensions = ["edx_toggles.sphinx.extensions.featuretoggles"]
    featuretoggles_source_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
    featuretoggles_repo_url = "https://github.com/edx/yourrepo"
    try:
        featuretoggles_repo_version = git.Repo(search_parent_directories=True).head.object.hexsha
    except git.InvalidGitRepositoryError:
        pass

Then, in a ``.rst`` file::

    .. featuretoggles::

