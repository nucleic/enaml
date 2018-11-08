.. _get_started:

===============
Getting Started
===============

It's easy to get started with Enaml. If you are comfortable programming in
Python, you should find yourself quickly up to speed. The sections below
provide the information you need to start writing simple Enaml applications.
When you are comfortable with the topics here, have a look at the
:ref:`dev_guides` for in-depth articles about developing with the framework.


.. This simply prevents the :doc: to create entries in the sidebar
.. container::

    .. rubric:: :doc:`introduction`

    The introduction to Enaml explains the motivations behind the project
    and what it seeks to achieve in the context of the larger Python
    ecosystem. It presents the challenges inherent to UI development and
    how the declarative programming model is used to address them.

    .. rubric:: :doc:`installation`

    The installation instructions present the steps needed to install
    Enaml and its dependencies.

    .. rubric:: :doc:`anatomy`

    The building blocks of an Enaml application are presented in the
    form of a runnable example. The example shows how the various
    syntactic constructs and framework components combine to create a
    simple user interface application.

    .. rubric:: :doc:`syntax`

    Enaml defines a superset of Python that allows to define the UI in a 
    declarative way. One of the great features of Enaml is its ability to 
    automatically bind to data models through a rich set of operators. This 
    section describes the Enaml specific part of the syntax and how those 
    operators are used to connect user defined data models to Enaml views 
    and  how they automatically keep the views up-to-date when the data in 
    the models change at runtime.

    .. rubric:: :doc:`layout`

    The layout systems of typical user interface frameworks can quickly
    become tedious for all but the simplest of cases. Enaml sheds the
    status quo and provides a flexible layout system which uses symbolic
    constraints. This section covers the basics of constraints layout.


.. toctree::
    :titlesonly:
    :hidden:

    introduction
    installation
    anatomy
    syntax
    layout
