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

- `Qt`_ and `PyQt`_ or `PySide`_.
- `GTK`_ and `PyGTK`_.
- `wxWidgets`_ and `wxPython`_.
- `Tk`_ and `TkInter`_.

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

    A user interface is constructed as a tree of graphical objects with
    some associated state.

Consider a hypothetical abstract object hierarchy, and what it might look like
if converted into a typical UI window:

.. container:: h-imgs

    .. image:: /images/abs_hierarchy.png
        :align: center

    .. image:: /images/win_hierarchy.png
        :align: center

In order to create such a window, most frameworks require the developer to
write imperative code to setup up the window's object hierachy. This leads to
code which looks similar to the following Python snippet:

.. code-block:: python

    window = Window()

    menu = Menu(window)
    item_1 = MenuItem(menu, "Item 1")
    item_2 = MenuItem(menu, "Item 2")
    item_3 = MenuItem(menu, "Item 3")

    window.setMenu(menu)

    label_1 = Label(window, "Label 1")
    field_1 = Field(window)
    label_2 = Label(window, "Label 2")
    field_2 = Field(window)

    form = FormLayout()
    form.addRow(label_1, field_1)
    form.addRow(label_2, field_2)

    button = Button(window, "Button")

    vbox = VBoxLayout()
    vbox.addLayout(form)
    vbox.addWidget(button)

    window.setLayout(vbox)

The problem with code like this is that its structure does not map well to
the objects which it is producing. The code is tedious to read, write, and
understand; which makes it error-prone and difficult to maintain.

.. highlights::

    Imperative programming constructs are simply not well suited for defining
    nested object hierarchies.

Programming against these frameworks is a fairly low level task and procedural
task. A developer is responsible for:

- procedurally building the object hierarchy
- tracking the data model for changes
- manually updating the UI to reflect data model changes

.. note::

    There are design patterns (such as `MVC`_) which exist to make this
    process more manageable, but they require strict developer discipline and
    do little to reduce the tedium of the development process.

.. _MVC: http://en.wikipedia.org/wiki/Model-view-controller


Declarative UIs
---------------

Relatively recently, there has been a shift in the UI development paradigm
which places emphasis on the declarative specification of the object
hierarchy. Microsoft's `WPF`_ and Qt's `QML`_ are two great examples. In both
of these frameworks, the developer provides a declarative representation of
the UI and defines how the visual elements of the UI should bind to data in
the data model; the framework takes care of everything else.

.. _WPF: http://msdn.microsoft.com/en-us/library/aa970268.aspx
.. _QML: http://qt-project.org/doc/qt-5.0/qtquick/qtquick-index.html

These two frameworks have similar but approaches, but expose the declarative
interface to the developer using different `Domain Specific Languages`_ (DSL):

.. _Domain Specific Languages: http://en.wikipedia.org/wiki/Domain-specific_language

+------------------------------+-------------------------------------+
| Microsofts's WPF             | Qt's QML                            |
+==============================+=====================================+
| XML-based declarative DSL    | Javascript-based declarative DSL    |
+------------------------------+-------------------------------------+
| Data models written in .Net  | Data models written in C++ or JS    |
+------------------------------+-------------------------------------+
| UI binds to model properties | UI binds to signals and properties  |
+------------------------------+-------------------------------------+
| Markup is translated to .Net | Markup is interpreted by a VM       |
+------------------------------+-------------------------------------+

Enaml brings this UI development paradigm to Python in a seamlessly integrated
fashion. The grammar of the Enaml language is a strict superset of Python.
This means that any valid Python file is a valid Enaml file, though the
converse is not necessary true. The tight integration with Python means that
the developer feels at home and uses standard Python syntax when expressing
how their data should bind to the visual attributes of the UI.

The following snippet shows how the window above is defined in Enaml:

.. code-block:: enaml

    enamldef Main(MainWindow):
        title = 'Window'
        MenuBar:
            Menu:
                title = 'Item 1'
            Menu:
                title = 'Item 2'
            Menu:
                title = 'Item 3'
        Container:
            Form:
                Label:
                    text = 'Label 1'
                Field:
                    pass
                Label:
                    text = 'Label 2'
                Field:
                    pass
            PushButton:
                text = 'Button'

Enaml Advantages
----------------
