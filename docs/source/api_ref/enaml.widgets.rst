.. _widgets-ref:

Widgets
===============================================================================

An Enaml widget is a toolkit-independent abstraction. The widget classes
defined in the :mod:`enaml.widgets` submodule establish a message passing
interface which is implemented by a given GUI toolkit backend. In this way,
a widget interface is not tied to any particular implementation.

Interface
---------

An Enaml widget's interface describes the attributes and events that the
widget exposes as its API. Changes to these attributes and events cause
message to be sent back and forth between the Enaml widget and a given
toolkit implemenation.

.. inheritance-diagram::
    enaml.widgets.abstract_button.AbstractButton
    enaml.widgets.action.Action
    enaml.widgets.action_group.ActionGroup
    enaml.widgets.container.Border
    enaml.widgets.bounded_date.BoundedDate
    enaml.widgets.bounded_datetime.BoundedDatetime
    enaml.widgets.bounded_time.BoundedTime
    enaml.widgets.calendar.Calendar
    enaml.widgets.check_box.CheckBox
    enaml.widgets.combo_box.ComboBox
    enaml.widgets.constraints_widget.ConstraintsWidget
    enaml.widgets.container.Container
    enaml.widgets.control.Control
    enaml.widgets.date_selector.DateSelector
    enaml.widgets.datetime_selector.DatetimeSelector
    enaml.widgets.dock_area.DockArea
    enaml.widgets.dock_item.DockItem
    enaml.widgets.dock_pane.DockPane
    enaml.widgets.dual_slider.DualSlider
    enaml.widgets.field.Field
    enaml.widgets.file_dialog.FileDialog
    enaml.widgets.flow_area.FlowArea
    enaml.widgets.flow_item.FlowItem
    enaml.widgets.form.Form
    enaml.widgets.group_box.GroupBox
    enaml.widgets.html.Html
    enaml.widgets.image_view.ImageView
    enaml.widgets.label.Label
    enaml.widgets.list_control.ListControl
    enaml.widgets.main_window.MainWindow
    enaml.widgets.mdi_area.MdiArea
    enaml.widgets.mdi_window.MdiWindow
    enaml.widgets.menu.Menu
    enaml.widgets.menu_bar.MenuBar
    enaml.widgets.mpl_canvas.MPLCanvas
    enaml.widgets.multiline_field.MultilineField
    enaml.widgets.notebook.Notebook
    enaml.widgets.object_combo.ObjectCombo
    enaml.widgets.page.Page
    enaml.widgets.progress_bar.ProgressBar
    enaml.widgets.push_button.PushButton
    enaml.widgets.radio_button.RadioButton
    enaml.widgets.scroll_area.ScrollArea
    enaml.widgets.separator.Separator
    enaml.widgets.slider.Slider
    enaml.widgets.spin_box.SpinBox
    enaml.widgets.split_item.SplitItem
    enaml.widgets.splitter.Splitter
    enaml.widgets.stack.Stack
    enaml.widgets.stack.Transition
    enaml.widgets.stack_item.StackItem
    enaml.widgets.status_bar.StatusBar
    enaml.widgets.time_selector.TimeSelector
    enaml.widgets.tool_bar.ToolBar
    enaml.widgets.view_table.View
    enaml.widgets.view_table.ViewTableHeaders
    enaml.widgets.view_table.ViewTable
    enaml.widgets.web_view.WebView
    enaml.widgets.widget.Widget
    enaml.widgets.window.Window
    :parts: 1


Base widgets
^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.widgets.widget.Widget
    enaml.widgets.constraints_widget.ConstraintsWidget
    enaml.widgets.control.Control
    enaml.widgets.abstract_button.AbstractButton
    enaml.widgets.bounded_date.BoundedDate
    enaml.widgets.bounded_datetime.BoundedDatetime
    enaml.widgets.bounded_time.BoundedTime

Standard widgets
^^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.widgets.action.Action
    enaml.widgets.action_group.ActionGroup
    enaml.widgets.calendar.Calendar
    enaml.widgets.check_box.CheckBox
    enaml.widgets.combo_box.ComboBox
    enaml.widgets.date_selector.DateSelector
    enaml.widgets.datetime_selector.DatetimeSelector
    enaml.widgets.field.Field
    enaml.widgets.file_dialog.FileDialog
    enaml.widgets.html.Html
    enaml.widgets.image_view.ImageView
    enaml.widgets.label.Label
    enaml.widgets.menu.Menu
    enaml.widgets.menu_bar.MenuBar
    enaml.widgets.mpl_canvas.MPLCanvas
    enaml.widgets.progress_bar.ProgressBar
    enaml.widgets.push_button.PushButton
    enaml.widgets.radio_button.RadioButton
    enaml.widgets.separator.Separator
    enaml.widgets.slider.Slider
    enaml.widgets.spin_box.SpinBox
    enaml.widgets.time_selector.TimeSelector
    enaml.widgets.tool_bar.ToolBar
    enaml.widgets.web_view.WebView


Window widgets
^^^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.widgets.main_window.MainWindow
    enaml.widgets.mdi_window.MdiWindow
    enaml.widgets.window.Window


Container and Layout widgets
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autosummary::
    :toctree: widgets
    :template: widget.rst

    enaml.widgets.container.Container
    enaml.widgets.dock_area.DockArea
    enaml.widgets.dock_item.DockItem
    enaml.widgets.dock_pane.DockPane
    enaml.widgets.flow_area.FlowArea
    enaml.widgets.flow_item.FlowItem
    enaml.widgets.form.Form
    enaml.widgets.group_box.GroupBox
    enaml.widgets.mdi_area.MdiArea
    enaml.widgets.notebook.Notebook
    enaml.widgets.page.Page
    enaml.widgets.scroll_area.ScrollArea
    enaml.widgets.split_item.SplitItem
    enaml.widgets.splitter.Splitter
    enaml.widgets.stack.Stack
    enaml.widgets.stack_item.StackItem


Standard library
^^^^^^^^^^^^^^^^

A number of additional widget types are available in the standard widget
library.  These are not top-level classes implemented in Python, but are
instead |Enaml| widgets implemented using ``enamldef`` declarations.

.. toctree::
   :maxdepth: 2

    Standard Widget Library <std_library_ref>
