Welcome to Enaml
================

.. image:: https://travis-ci.org/nucleic/enaml.svg?branch=master
    :target: https://travis-ci.org/nucleic/enaml
    :alt: Build Status
.. image:: https://ci.appveyor.com/api/projects/status/p2bapt3y6n7xixcl?svg=true
    :target: https://ci.appveyor.com/project/nucleic/enaml
    :alt: Appveyor Build Status
.. image:: https://github.com/nucleic/enaml/workflows/Continuous%20Integration/badge.svg
    :target: https://github.com/nucleic/enaml/actions
.. image:: https://codecov.io/gh/nucleic/enaml/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/nucleic/enaml
    :alt: Code Coverage Status
.. image:: https://github.com/nucleic/enaml/workflows/Documentation%20building/badge.svg
    :target: https://github.com/nucleic/enaml/actions
.. image:: https://readthedocs.org/projects/enaml/badge/?version=latest
    :target: http://enaml.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://img.shields.io/pypi/v/enaml.svg
    :target: https://pypi.org/project/enaml/
    :alt: PyPI version

Enaml is a programming language and framework for creating professional-quality
user interfaces with minimal effort.

What you get
============
* A declarative programming language, with a Pythonic flavour.
* Dozens of widgets, ready to go out-of-the-box (built on `Qt <https://www.qt.io/>`_).
* A constraints-based layout engine (built on `Kiwi <https://github.com/nucleic/kiwi>`_).
* Integration with a data model tool (built on `Atom <https://github.com/nucleic/atom>`_).
* An (optional) editor to allow you to see what the results will look like, as you type your code.
* A well-documented and easy-to-follow code base, plus documentation with plenty of worked examples.
* Language definitions for a number of popular editors.

What it can do for you
======================
- Build native GUI applications for a range of platforms

  + Quick and simple or complex and specialised.
  + See the structure of your GUI at a glance.

- Let you rapidly protoype new GUIs interfaces.

  + Intelligently layout your GUI, using symbolic constraints.
  + It automatically adapts for different platforms, different window sizes.
  + Tell the layout engine what your priorities are for layout, without having to count pixels.

- Encourages easy-to-maintain code:

  + The GUI can detect updates in the model, and refresh its widgets automatically, without low-level code.
  + Clean separation between your model and view, while keeping your controller code simple.

    * You can incorporate Python code directly in the view layer.
    * As your GUI design evolves, the constraints engine can adapt the layout.
    * Object-Oriented design allows you to reuse parts of your GUI in other parts of your projects.

- Let you customise a GUI for your particular needs.

  + Integrates with your Python code.
  + Include style-sheets to change the appearance across all, or part, of your application quickly.
  + Extend the available widgets or build your own.

Supported Versions
==================
Enaml applications can be run on any platform which supports Python (2.7, 3.4, 3.5 and 3.6) and Qt (versions 4 or 5, see https://doc.qt.io/qt-5/supported-platforms.html).

Enaml 0.10.4 will be the last version to support Python 2.7 and 3.4 and Qt 4.
Moving forward support will be limited to Python 3.5+ and Qt 5.

This includes Linux, Windows, macOs, Android and iOS. (Automated testing of Enaml runs on Linux.)

Enaml is licensed under the `Modified BSD License <https://github.com/nucleic/enaml/blob/master/LICENSE>`_.

Learn More
==========
The `Getting Started <http://enaml.readthedocs.io/en/latest/get_started/index.html>`_ chapter is a good first step to learn more. It includes `installation instructions <http://enaml.readthedocs.io/en/latest/get_started/installation.html>`_.

Watch some introductory talks about Enaml and what it can do:

.. image:: https://img.youtube.com/vi/ycFEwz_hAxk/2.jpg
  :target: https://youtu.be/ycFEwz_hAxk

`S. Chris Colbert (@sccolbert) presents at Enthought 2012. <https://www.youtube.com/watch?v=ycFEwz_hAxk>`_

.. image:: https://img.youtube.com/vi/G5ZYUGL7uTo/1.jpg
  :target: https://www.youtube.com/watch?v=G5ZYUGL7uTo

`Tom Stordy-Allison (@tstordyallison) presents at Pycon UK 2016. <https://www.youtube.com/watch?v=G5ZYUGL7uTo>`_

The `Enaml documentation <http://enaml.readthedocs.io/en/latest>`_ includes all the details, including `useful examples <http://enaml.readthedocs.io/en/latest/examples>`_.

You can ask questions on the `Enaml Google Group <http://groups.google.com/d/forum/enaml>`_
or with the `Enaml tag on StackOverflow <https://stackoverflow.com/questions/tagged/enaml>`_.

For version information, see the  `release notes <https://github.com/nucleic/enaml/blob/master/releasenotes.rst>`_.

Examples
========
The `Enaml documentation <http://enaml.readthedocs.io/en/latest>`_ includes many  `fully-functioning code samples <http://enaml.readthedocs.io/en/latest/examples/index.html>`_ of how to use Enaml. They range from `simple demonstrations of how a widget is used <http://enaml.readthedocs.io/en/latest/examples/ex_progress_bar.html>`_, to advanced explorations of the customisability of Enaml GUIs.

Employee Tutorial
~~~~~~~~~~~~~~~~~
The `Employee Tutorial <http://enaml.readthedocs.io/en/latest/examples/tut_employee.html>`_ shows how constraints and validators can be used to create easy-to-use and professional-looking applications:

.. image:: http://enaml.readthedocs.io/en/latest/_images/tut_employee_layout.png
    :target: http://enaml.readthedocs.io/en/latest/examples/tut_employee.html

Button Ring
~~~~~~~~~~~
The `Button Ring Example <https://enaml.readthedocs.io/en/latest/examples/ex_button_ring.html>`_ goes the other way. The result is neither professional-looking nor easy-to-use, but it shows the power and  flexibility of constraints-based layout - it might be silly, but this could not be achieved with typical layout systems.

.. image:: http://enaml.readthedocs.io/en/latest/_images/ex_button_ring.png
    :target: https://enaml.readthedocs.io/en/latest/examples/ex_button_ring.htm

Dock Item Alerts
~~~~~~~~~~~~~~~~
The `Dock Item Alerts Example <https://enaml.readthedocs.io/en/latest/examples/ex_dock_item_alerts.html>`_ shows some of the customisability of the appearances of an Enaml application. This application's appearance is based on Visual Studio 2010 style, with dockable items, but has some customisations based on the importance of the alerts being shown.

.. image:: http://enaml.readthedocs.io/en/latest/_images/ex_dock_item_alerts.png
    :target: https://enaml.readthedocs.io/en/latest/examples/ex_dock_item_alerts.html

Check out the `documentation <http://enaml.readthedocs.io/en/latest/examples/index.html>`_ for more examples.
