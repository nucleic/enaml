.. _introduction:

============
Introduction
============

This article is geared towards introducing a brand new user to Enaml. The
article sections cover the background, motivations, and programming paradigm
for the framework.

.. seealso::

    - For an intro to the Enaml language structure, see :doc:`anatomy`.

    - For advanced articles on the Enaml language and framework,
      see the :doc:`/dev_guides/index`.


What is Enaml?
--------------

*Fundamentally*

    Enaml is a declarative extension to the Python language grammar which
    enables a developer to concisely define a hierarchical tree of objects
    which automatically react to changes in a data model.

*Practically*

    Enaml is one of the easiest and most powerful ways to build professional
    quality user interfaces with Python.


Traditional UIs
---------------

Traditional user interface frameworks are typically implemented in a low level
language like C or C++. This is because the frameworks utilize the libraries
and services provided by the underlying operating system in order to draw
pixels on the screen. These low-level drawing operations are abstracted from
the developer with high level easy-to-use APIs. Some UI frameworks can be used
from Python with the help of wrappers which expose the high level toolkit APIs
to the Python runtime. The most common of these frameworks and their Python
wrappers include:

* `Qt`_ and `PyQt`_ or `PySide`_.
* `GTK`_ and `PyGTK`_.
* `wxWidgets`_ and `wxPython`_.
* `Tk`_ and `TkInter`_.

.. _Qt: https://qt-project.org
.. _PyQt: http://www.riverbankcomputing.com/software/pyqt/intro
.. _PySide: http://qt-project.org/wiki/PySide
.. _GTK: http://www.gtk.org
.. _PyGTK: http://www.pygtk.org
.. _wxWidgets: http://www.wxwidgets.org
.. _wxPython: http://www.wxpython.org
.. _Tk: http://www.tcl.tk
.. _TkInter: https://wiki.python.org/moin/TkInter

All of these frameworks share a common theme which is:

.. highlights::

    A user interface is constructed as a tree of graphical widgets with
    some associated state.

Consider this hypothetical abstract object hierarchy, and imagine what it might
look like if converted into a typical UI window:

.. container:: paddedimg

    .. image:: /images/abs_hierarchy.png
        :align: center

With a bit of study, it should be clear that the window would look something
like the following:

.. container:: paddedimg

    .. image:: /images/win_hierarchy.png
        :align: center


The Challenges of UI Development
--------------------------------

The Declarative Programming Model
---------------------------------

Enaml UI
--------

Enaml Advantages
----------------
