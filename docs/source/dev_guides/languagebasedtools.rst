.. _languagebasedtools:

====================
Language-Based Tools
====================

Language-based tools are software that operate on programming languages,
including Integrated Development Environments (IDEs) and others.

Many of these tools can be configured to recognise the syntax of a .enaml file,
and thus provide syntax-colouring, indenting support and other features.

Enaml comes bundled with a number of configuration files for common IDEs and
other tools.

`BBEdit`_
----------------------------

BBEdit is a commercial MacOS IDE from `Bare Bones`_.

An Enaml language library for BBEdit is provided in the source at
``tools/barebones/``

For installation instructions, see the `BBEdit Support pages`_.

.. _BBEdit: https://www.barebones.com/products/bbedit/
.. _Bare Bones: https://www.barebones.com/
.. _BBEdit Support pages: https://www.barebones.com/support/bbedit/plugin_library.html

`GNU Emacs`_
------------

GNU Emacs is a popular, cross-platform, open-source IDE.

An Enaml mode for Emacs is provided in the source at ``tools/emacs``.

For installation instructions, see in the source at
``tools/emacs/README.rst``

.. _GNU Emacs: https://www.gnu.org/software/emacs/

`TextMate`_
-----------

TextMate is a commercial MacOS IDE.

An Enaml language definition for TextMate is provided in the source tree at
``tools/sublimetext``.


For installation instructions, see the `TextMate Manual`_.

.. _TextMate: https://macromates.com/
.. _TextMate Manual: https://macromates.com/manual/en/language_grammars#language_grammars

`Sublime Text`_
---------------

Sublime Text is a cross-platform, commercial IDE.

Sublime Text can also use the TextMate language definition at
``tools/sublimetext/Enaml.tmLanguage``.

For installation instructions, see the `Sublime Text manual`_.

.. _Sublime Text: https://www.sublimetext.com/
.. _Sublime Text manual: http://docs.sublimetext.info/en/latest/extensibility/packages.html#installing-packages


`Visual Studio`_
----------------

Visual Studio is a commercial IDE for Windows and MacOs from Microsoft.

Visual Studio can also use the TextMate language definition at
``tools/sublimetext/Enaml.tmLanguage``.

For installation instructions, see the
`Visual Studio manual`_.

Alternatively, there is a third-party Visual Studio extension, `enaml-vs`_ available
free from the Visual Studio Marketplace, which offers simpler installation of the 
same definitions.

.. _Visual Studio: https://visualstudio.microsoft.com/
.. _Visual Studio manual: https://code.visualstudio.com/docs/extensions/themes-snippets-colorizers
.. _enaml-vs: https://marketplace.visualstudio.com/items?itemName=mdartiailh.enaml-vs

.. warning::
    Third-party plugins are not supported by the Enaml team.


`PyCharm`_
----------------


PyCharm is a cross-platform, freemium Python IDE from JetBrains.

PyCharm can also use the TextMate language definition at
``tools/sublimetext/Enaml.tmLanguage``.

For installation instructions, see the `TextMate Bundles support plugin`_
manual.

Alternatively, there are two third-party PyCharm plugins to add basic syntax
support for Enaml:

* `pycharm-enaml-plugin`_
* `pycharm-enaml-keywords`_

.. warning::
    Third-party plugins are not supported by the Enaml team.

.. _PyCharm: https://www.jetbrains.com/pycharm/
.. _TextMate Bundles support plugin: https://www.jetbrains.com/help/pycharm/2018.1/tutorial-using-textmate-bundles.html
.. _pycharm-enaml-plugin: https://github.com/pberkes/pycharm-enaml-plugin
.. _pycharm-enaml-keywords: https://github.com/vahndi/pycharm-enaml-keywords

`Vim`_
------
Vim is a popular, cross-platform, charityware text editor.

Enaml syntax and indent files are available at ``tools/vim``.

For installation instructions, see in the source at
``tools/vim/README.rst``

.. _Vim: https://www.vim.org/

`Pygments`_
-----------

Pygments is an open-source generic syntax highlighter. It is used by
`Sphinx`_ to format code included in project documentation.

An Enaml lexer for Pygments is available at ``tools/pygments``.

To install, change into the ``./tools/pygments`` directory, and run
``python setup.py install``.

Alternatively, it can be installed directly from `PyPi`_: ``pip install pygments-enaml``

Once this is installed, it will be automatically used by Sphinx to format
Enaml code blocks (i.e. `code directives`_, with `enaml` as the language
argument.)

.. _Pygments: http://pygments.org/
.. _Sphinx: http://www.sphinx-doc.org/
.. _code directives: http://docutils.sourceforge.net/docs/ref/rst/directives.html#Code
..  _PyPi: https://pypi.org/project/pygments-enaml/
