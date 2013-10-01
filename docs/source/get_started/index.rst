.. _get_started:

===============
Getting Started
===============

It's easy to get started with Enaml. If you are comfortable programming in
Python, you should find yourself quickly up to speed. The sections below
provide the information you need to start writing simple Enaml applications.
When you are comfortable with the topics here, have a look at the
:ref:`dev_guides` for in-depth articles about developing with the framework.


.. toctree::
    :hidden:

    introduction
    installation
    anatomy
    operators
    layout
    widgets


.. list-table::

    * - :ref:`introduction`

        The introduction to Enaml explains the motivations behind the project
        and what it seeks to achieve in the context of the larger Python
        ecosystem. It presents the challenges inherent to UI development and
        how the declarative programming model is used to address them.

    * - :ref:`installation`

        The installation instructions present the steps needed to install
        Enaml and its dependencies.

    * - :ref:`anatomy`

        The building blocks of an Enaml application are presented in the
        form of a runnable example. The example shows how the various
        syntactic constructs and framework components combine to create a
        simple user interface application.

    * - :ref:`operators`

        One of the great features of Enaml is its rich set of operators. This
        section describes how those operators are used to connect user defined
        data models to Enaml views and how they automatically keep the views
        up-to-date when the data in the models change at runtime.

    * - :ref:`layout`

        The layout systems of typical user interface frameworks can quickly
        become tedious for all but the simplest of cases. Enaml sheds the
        status quo and provides a flexible layout system which uses symbolic
        constraints. This section covers the basics of constraints layout.

    * - :ref:`widgets`

        This sections provides a brief overview about the structure of an
        Enaml widget and how it communicates with a rendering backend. A
        high level understanding of the widget structure is useful for
        building a mental model of the application data and event flow.
