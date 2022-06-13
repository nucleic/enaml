.. _installation:

============
Installation
============

Installing Enaml is a straight-forward process. There are three approaches to
choose from.

Anaconda
--------

If you use the `Anaconda`_ Python distribution platform (or `Miniconda`_,
its lighter-weight companion), the latest release of Enaml can be installed
using conda from the conda-forge channel::

    $ conda install enaml -c conda-forge

.. _Anaconda: https://store.continuum.io/cshop/anaconda
.. _Miniconda: https://conda.io/miniconda.html

Wheels
------

If you don't use Anaconda, you can install Enaml and its dependencies,
pre-compiled, through PIP, for most common platforms.

You will need three things:

* `Python`_
* Enaml (and its dependencies)
* a toolkit rendering library

Python
~~~~~~

Enaml is a Python framework and requires a supported Python runtime. Enaml
currently supports **Python 3.8**, **Python 3.9** and **Python 3.10**.

.. note::

    Currently Enaml does support the match syntax introduced in Python 3.10 in
    .enaml files

The most recent Python releases are available on the `Python Downloads`_ pages.
Installers are available for Windows and OSX. Linux users should install Python
using their OS package manager.

.. _Python: http://python.org
.. _Python Downloads: http://python.org/download


Enaml and Dependencies
~~~~~~~~~~~~~~~~~~~~~~

You can install enaml and (almost) all of its dependencies through the pip
command line.::

    $ pip install enaml

Toolkit Rendering Library
~~~~~~~~~~~~~~~~~~~~~~~~~

Enaml's declarative widgets provide a layer of abstraction on top of the
widgets of a toolkit rendering library. Enaml ships with a backend based on Qt5/6
and third-party projects such as `enaml-web`_ and `enaml-native`_ provides
alternative backends.

Enaml uses the `QtPy`_ library as compatibility layer to support transparently both
Qt 5 and Qt 6 through either PyQt or PySide. PyQt5 has been supported for a longer
time and has been more heavily tested.

Starting with Enaml 0.13.0, you can specify a rendering library using extra_requires,
ie::

    $ pip install enaml[qt5-pyqt]

    Currently, you can use either [qt5-pyqt] to use PyQt5, [qt5-pyside] to
    use Pyside2, or [qt6-pyqt] and [qt6-pyside] if you want to use Qt6.

Starting with Enaml 0.15.1, you can also specify additional extras needed for specific
widgets:

- Scintila widget: [scintilla-qt5-pyqt] or [scintilla-qt6-pyqt]
- Matplotlib canvas: [matplotlib-qt]
- IPython console: [ipython-qt]
- WebView (extra are needed only for PyQt): [webview-qt5-pyqt] or [webview-qt6-pyqt]
- VTK canvas: [vtk-qt]

.. note::
    One can specify multiple extras separated by ``,``::
        $ pip install enaml[qt5-pyqt,ipython-qt]

.. note::
    There is no pyqt5 wheel available for 32-bit Linux.

.. _enaml-web: https://github.com/codelv/enaml-web
.. _enaml-native: https://github.com/codelv/enaml-native

Compiling it yourself: The Hard Way
-----------------------------------

Building Enaml from scratch requires a few external dependencies. The
sections below describe how to install Enaml and all of its dependencies from
scratch. The instructions assume that the user's system has a C++ compiler and
the `Git`_ command line tools installed and available on the system path.

.. _Git: http://git-scm.com

`Pip`_
~~~~~~

Pip is the default package manager for Python. The installation instructions
below assume that Pip has been installed in the target Python environment
(see `Pip install`_).

.. _Pip: https://pip.pypa.io/en/stable/
.. _Pip Install: https://pip.pypa.io/en/stable/installing/

`Ply`_
~~~~~~

The Enaml framework extends the grammar Python language with new declarative
syntax constructs. To accomplish this, Enaml has a fully compliant Python
3.7/3.8/3.9 lexer and parser with added support for the new syntax. These
components are built using the PLY parsing tools, which contain Python
implementations of lex and yacc.

Ply can be installed with the ``pip install`` command of `Pip`_::

    $ pip install ply

.. _Ply: http://www.dabeaz.com/ply

`QtPy`_
~~~~~~~

The Enaml framework uses the `QtPy`_ library as a compatibility shim between
the various toolkit rendering libraries.

QtPy can be installed with the ``pip install`` command of `Pip`_::

    $ pip install QtPy

And you also need a toolkit rendering library either `PyQt5`_, `PyQt6`_, `Pyside2`_,
or `PySide6`_ which all be installed through pip.

.. _QtPy: https://pypi.python.org/pypi/QtPy/
.. _PyQt5: https://pypi.org/project/PyQt5/
.. _PyQt6: https://pypi.org/project/PyQt6/
.. _Pyside2: http://wiki.qt.io/Qt_for_Python
.. _PySide6: https://doc.qt.io/qtforpython/contents.html

`Kiwisolver`_
~~~~~~~~~~~~~

Enaml's layout engine is built on top of the `Cassowary`_ linear constraint
optimizer. This is the same algorithm used by the Cocoa Autolayout engine in
OSX. Kiwisolver provides Python bindings to a C++ implementation of the
Cassowary algorithm.

Kiwisolver can be installed with the ``pip install`` command of `Pip`_::

    $ pip install kiwisolver

.. _Kiwisolver: https://github.com/nucleic/kiwi
.. _Cassowary: http://www.cs.washington.edu/research/constraints/cassowary

`Bytecode`_
~~~~~~~~~~~

The Enaml compiler depends on the ``bytecode`` module, which is a Python
library used to generate and modify bytecode.

Bytecode can be installed with the ``pip install`` command of `Pip`_::

    $ pip install bytecode

.. _Bytecode: https://github.com/vstinner/bytecode

`Atom`_
~~~~~~~

Atom is the Python framework which provides the foundational object model for
Enaml. Atom objects are extremely lightweight, fast, and support a robust
implementation of the `Observer Pattern`_. If these traits seem all too ideal
for a project like Enaml, it's because Enaml was the primary motivation behind
the development of Atom.

Atom can be installed with the ``pip install`` command of `Pip`_::

    $ pip install atom

Alternatively, cloning and building the latest (unstable dev) version of Atom from source is simple::

    $ git clone https://github.com/nucleic/atom.git
    $ cd atom
    $ pip install .

.. _Atom: https://github.com/nucleic/atom
.. _Observer Pattern: http://en.wikipedia.org/wiki/Observer_pattern

`Enaml`_
~~~~~~~~

The last item on the list is Enaml itself. The latest (unstable dev) version
can be installed with just a few commands::

    $ git clone https://github.com/nucleic/enaml.git
    $ cd enaml
    $ pip install .

.. _Enaml: https://github.com/nucleic/enaml

Supported Platforms
-------------------

Enaml is known to run on Windows, OSX, and Linux; and compiles cleanly
with MSVC, Clang, GCC, and MinGW. However, primary development of the
framework occurs on Windows (7, 8 and 10), so some quirks and bugs may be
present on the other platforms. If you encounter a bug, please report
it on the `Issue Tracker`_.

.. _Issue Tracker: http://github.com/nucleic/enaml/issues
