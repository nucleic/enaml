RefactorDoc: Docstring refactor shpinx extension
================================================

The RefactorDoc extension parses the function and class docstrings as
they are retrieved by the autodoc extension and refactors the section
blocks into sphinx friendly rst. The extension shares similarities with
alternatives (such as numpydoc) but aims at reflacting the original form
of the docstring.

Key aims of RefactorDoc are:

    - Do not change the order of sections.
    - Allow sphinx directives between (and inside) section blocks.
    - Easier to debug (native support for debugging) and extend.

Repository
----------

The RefactorDoc extension lives at Github. You can clone the repository
using::

    git clone ...

Installation
------------

Please copy the ``refactor_doc.py`` in the source directory
(or a sub_directory) of your documentation and update your ``conf.py``
as follows:

    - Add the path where the extension exists in the python path::

        sys.path.insert(0, os.path.abspath('/extension'))

    - Add refactor-doc to the extensions variable::

        extensions = [...,
              'refactor_doc',
              ...,
             ]
