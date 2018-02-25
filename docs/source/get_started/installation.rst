.. _installation:

============
Installation
============

Installing Enaml is a straight forward process. It requires few external
dependencies, and those which are required are easily installed, with most
projects providing binaries or a simple Python setup script. The sections
below describe how to install Enaml and all of its dependencies from scratch,
starting with the installation of a Python runtime. The instructions assume
that the user's system has a C++ compiler and the `Git`_ command line tools
installed and available on the system path.

.. _Git: http://git-scm.com


.. topic:: The Easy Way

    If installing and building Enaml and its dependencies from scratch is not
    appealing, the free (and unaffiliated) `Anaconda`_ Python distribution
    provides a complete Python environment in which the last release of Enaml
    can be installed using conda from the conda-forge channel::
    
    $ conda install enaml -c conda-forge
    
    If you have a working C++ compiler, you can install using pip::

    $ pip install enaml

.. _Anaconda: https://store.continuum.io/cshop/anaconda


.. topic:: Supported Platforms

    Enaml is known to run on Windows, OSX, and Linux; and compiles cleanly
    with MSVC, Clang, GCC, and MinGW. However, primary development of the
    framework occurs on Windows (7, 8 and 10), so some quirks and bugs may be
    present on the other platforms. If you encounter a bug, please report
    it on the `Issue Tracker`_.

.. _Issue Tracker: http://github.com/nucleic/enaml/issues


`Python`_
---------

Enaml is a Python framework and requires a supported Python runtime. Enaml
currently supports **Python 2.7**, **Python 3.4**, **Python 3.5**,
**Python 3.6**.

The most recent Python releases are available on the `Python Downloads`_ pages.
Installers are available for Windows and OSX. Linux users should install Python
using their OS package manager.

.. _Python: http://python.org
.. _Python Downloads: http://python.org/download


`Setuptools`_ and `Pip`_
------------------------

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


`Future`_
---------

Enaml supports both Python 2 and 3 and uses the future library as a 
compatibility layer. Future can be installed with the ``pip install`` command 
of `Pip`_::

    C:\> pip install future


`Ply`_
------

The Enaml framework extends the grammar Python language with new declarative
syntax constructs. To accomplish this, Enaml has a fully compliant Python 
2.7/3.4/3.5/3.6 lexer and parser with added support for the new syntax. These 
components are built using the PLY parsing tools, which contain Python 
implementations of lex and yacc.

Ply can be installed with the ``pip install`` command of `Pip`_::

    C:\> pip install ply

.. _Ply: http://www.dabeaz.com/ply


`PyQt`_
-------

Enaml's declarative widgets provide a layer of abstraction on top of the
widgets of a toolkit rendering library. While Enaml is architected to be
toolkit agnostic, the recommended toolkit library is `Qt`_.

Enaml supports using either PyQt4 or PyQt5 and uses the `qtpy`_ library
as compatibility layer.

PyQt4 is a robust set of Python bindings to the Qt 4 toolkit.
The `PyQt Downloads`_ page contains Windows installers which include the Qt
binaries. OSX users can install PyQt4 via `Homebrew`_. Linux users should
install via the system package manager.

PyQt5 is a robust set of Python bindings to the Qt 5 toolkit. On Python 3,
it can install via pip::

$ pip install pyqt5

.. topic:: Note for PySide/PySide2 Users

    Enaml has unofficial support for using the `PySide`_ bindings to Qt. To
    activate PySide support, set the environment variable ``QT_API=pyside``
    (``QT_API=pyside2`` for PySide2) before starting the Enaml application.
    Note that the PySide bindings are not nearly as stable as PyQt and contain
    several bugs which can and will cause applications to crash. There are also
    some API differences between the two libraries. So while some effort is
    made to support the use of PySide in Enaml, it is "use at your own risk".

.. _PyQt: http://www.riverbankcomputing.com/software/pyqt/intro
.. _qtpy: https://pypi.python.org/pypi/QtPy/
.. _Qt: http://qt-project.org
.. _PyQt Downloads: http://www.riverbankcomputing.com/software/pyqt/download
.. _Homebrew: http://brew.sh
.. _PySide: http://qt-project.org/wiki/PySide


`Kiwisolver`_
-------------

Enaml's layout engine is built on top of the `Cassowary`_ linear constraint
optimizer. This is the same algorithm used by the Cocoa Autolayout engine in
OSX. Kiwisolver provides Python bindings to a C++ implementation of the
Cassowary algorithm.

The simplest way to install Kiwisolver is with ``pip``::

    C:\> pip install kiwisolver

.. _Kiwisolver: https://github.com/nucleic/kiwi
.. _Cassowary: http://www.cs.washington.edu/research/constraints/cassowary


`Atom`_
-------

Atom is the Python framework which provides the foundational object model for
Enaml. Atom objects are extremely lightweight, fast, and support a robust
implementation of the `Observer Pattern`_. If these traits seem all too ideal
for a project like Enaml, it's because Enaml was the primary motivation behind
the development of Atom.

Cloning and building Atom from source is simple::

    C:\> git clone https://github.com/nucleic/atom.git
    C:\> cd atom
    C:\> python setup.py install

.. _Atom: https://github.com/nucleic/atom
.. _Observer Pattern: http://en.wikipedia.org/wiki/Observer_pattern


`Enaml`_
--------

The last item on the list is Enaml itself, and it can be installed with just
a few commands::

    C:\> git clone https://github.com/nucleic/enaml.git
    C:\> cd enaml
    C:\> python setup.py install

.. _Enaml: https://github.com/nucleic/enaml
