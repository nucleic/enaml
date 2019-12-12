.. _installation:

============
Installation
============

Installing Enaml is a straight-forward process. There are three approaches to
choose from.

Anaconda: The Easiest Way
-------------------------

If you use the `Anaconda`_ Python distribution platform (or `Miniconda`_,
its lighter-weight companion), the latest release of Enaml can be installed
using conda from the conda-forge channel::

    $ conda install enaml -c conda-forge

.. _Anaconda: https://store.continuum.io/cshop/anaconda
.. _Miniconda: https://conda.io/miniconda.html

Wheels: The Pretty Easy Way
---------------------------

If you don't use Anaconda, you can install Enaml and its dependencies,
pre-compiled, through PIP, for most common platforms.

You will need three things:

* `Python`_
* Enaml (and its dependencies)
* a toolkit rendering library

Python
~~~~~~

Enaml is a Python framework and requires a supported Python runtime. Enaml
currently supports **Python 2.7**, **Python 3.4**, **Python 3.5**,
**Python 3.6** and **Python 3.7**.

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
widgets of a toolkit rendering library. You will need to install this
dependency separately.

The recommended library is `PyQt5`_,  a robust set of Python bindings to the
Qt 5 toolkit.  (It includes the necessary parts of Qt 5.)

On 32 and 64-bit Windows, 64-bit OS X and 64-bit Linux, with Python
versions >=3.5, it can be installed via pip::

    $ pip install pyqt5

.. note::
    There is no pyqt5 wheel available for 32-bit Linux.

Alternatives
++++++++++++

Enaml uses the `QtPy`_ library as compatibility layer to support some other QT-based libraries.

* `PyQt`_, which is a robust set of Python bindings to the Qt 4 toolkit. It is no longer a
  supported project, but can still be installed and used with Enaml. The
  `PyQt Downloads`_ page contains Windows installers - which also the necessary parts of Qt 4.
  OSX users can install PyQt4 via `Homebrew`_. Linux users should install via the system
  package manager.

* `PySide2`_ (a.k.a. Qt for Python) is a set of Python bindings to the Qt 5 toolkit.
  This is not recommended. These bindings are not nearly as stable as PyQt. They contain
  several bugs which can and will cause applications to crash. There are also some API
  differences between the two libraries.  While some effort is made to support the use of
  PySide2 in Enaml, it is "use at your own risk". Patches to improve support are welcomed.

  To activate PySide2 support, install `PySide2`_ separately and set the environment
  variable ``QT_API=pyside2`` before starting the Enaml application.

* `PySide`_ is a set of Python bindings to the Qt 4 toolkit which are no longer being
  maintained. These bindings are not recommended, and not supported, but you may find they
  work anyway. Use at your own risk.

  To activate PySide support, install `PySide`_ separately and set the environment
  variable ``QT_API=pyside`` before starting the Enaml application.

* While Enaml is architected to be toolkit agnostic, only Qt-based toolkit libraries are
  supported. There are third-party projects that provide support for other back-ends.

Compiling it yourself: The Hard Way
-----------------------------------

Building Enaml from scratch requires a few external dependencies. The
sections below describe how to install Enaml and all of its dependencies from
scratch, starting with the installation of a Python runtime. The instructions
assume that the user's system has a C++ compiler and the `Git`_ command line
tools installed and available on the system path.

.. _Git: http://git-scm.com

`Setuptools`_ and `Pip`_
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Setuptools is a Python package which makes installing other Python packages a
breeze. Pip is the default package manager for Python. The installation
instructions below assume that Setuptools and Pip have been installed in the
target Python environment. Follow the relevant `Setuptools Install`_
instructions for adding the package to your system.

.. note::
    Recent versions of Python (Python 2 >=2.7.9 or Python 3 >=3.4) installed
    from the official binaries install come with those tools installed.

.. _Setuptools: http://pythonhosted.org/setuptools
.. _Pip: https://pip.pypa.io/en/stable/
.. _Setuptools Install: https://pypi.python.org/pypi/setuptools/1.1.6
.. _Pip Install: https://pip.pypa.io/en/stable/installing/

`Ply`_
~~~~~~

The Enaml framework extends the grammar Python language with new declarative
syntax constructs. To accomplish this, Enaml has a fully compliant Python
2.7/3.4/3.5/3.6 lexer and parser with added support for the new syntax. These
components are built using the PLY parsing tools, which contain Python
implementations of lex and yacc.

Ply can be installed with the ``pip install`` command of `Pip`_::

    $ pip install ply

`QtPy`_
~~~~~~~

The Enaml framework uses the `QtPy`_ library as a compatibility shim between
the various toolkit rendering libraries.

QtPy can be installed with the ``pip install`` command of `Pip`_::

    $ pip install QtPy

.. _Ply: http://www.dabeaz.com/ply
.. _PyQt: http://www.riverbankcomputing.com/software/pyqt/intro
.. _PyQt5: https://pypi.org/project/PyQt5/
.. _QtPy: https://pypi.python.org/pypi/QtPy/
.. _Qt: http://qt-project.org
.. _PyQt Downloads: http://www.riverbankcomputing.com/software/pyqt/download
.. _Homebrew: http://brew.sh
.. _PySide: http://qt-project.org/wiki/PySide
.. _Pyside2: http://wiki.qt.io/Qt_for_Python

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

`Atom`_
~~~~~~~

Atom is the Python framework which provides the foundational object model for
Enaml. Atom objects are extremely lightweight, fast, and support a robust
implementation of the `Observer Pattern`_. If these traits seem all too ideal
for a project like Enaml, it's because Enaml was the primary motivation behind
the development of Atom.

Cloning and building Atom from source is simple::

    $ git clone https://github.com/nucleic/atom.git
    $ cd atom
    $ python setup.py install

.. _Atom: https://github.com/nucleic/atom
.. _Observer Pattern: http://en.wikipedia.org/wiki/Observer_pattern

`Enaml`_
~~~~~~~~

The last item on the list is Enaml itself. The latest (unstable dev) version
can be installed with just a few commands::

    $ git clone https://github.com/nucleic/enaml.git
    $ cd enaml
    $ python setup.py install

.. _Enaml: https://github.com/nucleic/enaml

Supported Platforms
-------------------

Enaml is known to run on Windows, OSX, and Linux; and compiles cleanly
with MSVC, Clang, GCC, and MinGW. However, primary development of the
framework occurs on Windows (7, 8 and 10), so some quirks and bugs may be
present on the other platforms. If you encounter a bug, please report
it on the `Issue Tracker`_.

.. _Issue Tracker: http://github.com/nucleic/enaml/issues
