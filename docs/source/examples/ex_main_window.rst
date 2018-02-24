Main Window Example
===============================================================================

:download:`main_window <../../../examples/widgets/main_window.enaml>`

::

    An example of the `MainWindow` widget.
    
    This example demonstrates the use of the `MainWindow` widget. This is a
    subclass of the `Window` widget which adds support for dock panes, tool
    bars and a menu bar. The children of a `MainWindow` can be defined in
    any order. Like `Window`, a `MainWindow` has at most one central widget
    which is an instance of `Container`. A `MainWindow` can have any number
    of `DockPane` and `ToolBar` children, and at most one `MenuBar`.
    
    Support for a `StatusBar` will be added in the future.
    
    Implementation Notes:
    
        The main window facilities in Wx are very weak. If these features
        are required for a particular application, strongly prefer the Qt
        backend over Wx (this is generally a good life-rule).

::

 $ enaml-run main_window

.. image:: images/ex_main_window.png

.. literalinclude:: ../../../examples/widgets/main_window.enaml
    :language: enaml

