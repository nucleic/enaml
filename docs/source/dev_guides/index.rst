.. _dev_guides:

================
Developer Guides
================

The Enaml developer guides are intended as the primary reference for learning
and becoming an effective developer with the framework. The guides covers a
variety of topics ranging from language features and syntax rules to
application development and best practices. For the implementation details of
the framework see the :ref:`arch_ref`.

.. This simply prevents the :doc: to create entries in the sidebar
.. container::

    .. rubric:: :doc:`stylesheets`

    Styles sheets are a powerful feature which allow the developer to
    customize the visual appearance of a view independent from the
    view's structural definition. Inspired by CSS, but with all the
    dynamism provided by the Enaml language.

    .. rubric:: :doc:`languagebasedtools`

    Enaml introduces a new syntax. Language-based tools can be
    configured to recognise this syntax. Several such configurations and
    plug-ins are provided.

    .. rubric:: :doc:`workbenches`

    Enaml Workbenches provide a set of low-level components which can
    be used to develop high-level plugin applications.  Workbenches
    enable the developer to write large UI applications which can be
    *safely extended at runtime* by other developers.

.. toctree::
    :hidden:

    stylesheets
    languagebasedtools
    workbenches
