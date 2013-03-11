#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
def action_factory():
    from .qt_action import QtAction
    return QtAction


def action_group_factory():
    from .qt_action_group import QtActionGroup
    return QtActionGroup


def calendar_factory():
    from .qt_calendar import QtCalendar
    return QtCalendar


def check_box_factory():
    from .qt_check_box import QtCheckBox
    return QtCheckBox


def combo_box_factory():
    from .qt_combo_box import QtComboBox
    return QtComboBox


def container_factory():
    from .qt_container import QtContainer
    return QtContainer


def control_factory():
    from .qt_control import QtControl
    return QtControl


def date_selector_factory():
    from .qt_date_selector import QtDateSelector
    return QtDateSelector


def datetime_selector_factory():
    from .qt_datetime_selector import QtDatetimeSelector
    return QtDatetimeSelector


def dock_pane_factory():
    from .qt_dock_pane import QtDockPane
    return QtDockPane


def field_factory():
    from .qt_field import QtField
    return QtField


def file_dialog_factory():
    from .qt_file_dialog import QtFileDialog
    return QtFileDialog


def flow_area_factory():
    from .qt_flow_area import QtFlowArea
    return QtFlowArea


def flow_item_factory():
    from .qt_flow_item import QtFlowItem
    return QtFlowItem


def group_box_factory():
    from .qt_group_box import QtGroupBox
    return QtGroupBox


def html_factory():
    from .qt_html import QtHtml
    return QtHtml


def image_factory():
    from .qt_image import QtImage
    return QtImage


def image_view_factory():
    from .qt_image_view import QtImageView
    return QtImageView


def label_factory():
    from .qt_label import QtLabel
    return QtLabel


def list_view_factory():
    from .qt_list_view import QtListView
    return QtListView


def list_item_factory():
    from .qt_list_item import QtListItem
    return QtListItem


def main_window_factory():
    from .qt_main_window import QtMainWindow
    return QtMainWindow


def mdi_area_factory():
    from .qt_mdi_area import QtMdiArea
    return QtMdiArea


def mdi_window_factory():
    from .qt_mdi_window import QtMdiWindow
    return QtMdiWindow


def menu_factory():
    from .qt_menu import QtMenu
    return QtMenu


def menu_bar_factory():
    from .qt_menu_bar import QtMenuBar
    return QtMenuBar


def mpl_canvas_factory():
    from .qt_mpl_canvas import QtMPLCanvas
    return QtMPLCanvas


def multiline_field_factory():
    from .qt_multiline_field import QtMultilineField
    return QtMultilineField


def notebook_factory():
    from .qt_notebook import QtNotebook
    return QtNotebook


def page_factory():
    from .qt_page import QtPage
    return QtPage


def push_button_factory():
    from .qt_push_button import QtPushButton
    return QtPushButton


def progress_bar_factory():
    from .qt_progress_bar import QtProgressBar
    return QtProgressBar


def radio_button_factory():
    from .qt_radio_button import QtRadioButton
    return QtRadioButton


def scroll_area_factory():
    from .qt_scroll_area import QtScrollArea
    return QtScrollArea


def separator_factory():
    from .qt_separator import QtSeparator
    return QtSeparator


def slider_factory():
    from .qt_slider import QtSlider
    return QtSlider


def spin_box_factory():
    from .qt_spin_box import QtSpinBox
    return QtSpinBox


def split_item_factory():
    from .qt_split_item import QtSplitItem
    return QtSplitItem


def splitter_factory():
    from .qt_splitter import QtSplitter
    return QtSplitter


def stack_factory():
    from .qt_stack import QtStack
    return QtStack


def stack_item_factory():
    from .qt_stack_item import QtStackItem
    return QtStackItem


#def text_editor_factory():
#    from .qt_text_editor import QtTextEditor
#    return QtTextEditor


def time_selector_factory():
    from .qt_time_selector import QtTimeSelector
    return QtTimeSelector


def tool_bar_factory():
    from .qt_tool_bar import QtToolBar
    return QtToolBar


def web_view_factory():
    from .qt_web_view import QtWebView
    return QtWebView


def window_factory():
    from .qt_window import QtWindow
    return QtWindow


def register_default():
    from .qt_widget_registry import QtWidgetRegistry
    reg = QtWidgetRegistry.register
    register = lambda name, factory: reg(name, factory, 'default')
    register('Action', action_factory)
    register('ActionGroup', action_group_factory)
    register('Calendar', calendar_factory)
    register('CheckBox', check_box_factory)
    register('ComboBox', combo_box_factory)
    register('Container', container_factory)
    register('Control', control_factory)
    register('DateSelector', date_selector_factory)
    register('DatetimeSelector', datetime_selector_factory)
    register('DockPane', dock_pane_factory)
    register('Field', field_factory)
    register('FileDialog', file_dialog_factory)
    register('FlowArea', flow_area_factory)
    register('FlowItem', flow_item_factory)
    register('GroupBox', group_box_factory)
    register('Html', html_factory)
    register('Image', image_factory)
    register('ImageView', image_view_factory)
    register('Label', label_factory)
    register('ListView', list_view_factory)
    register('ListItem', list_item_factory)
    register('MainWindow', main_window_factory)
    register('MdiArea', mdi_area_factory)
    register('MdiWindow', mdi_window_factory)
    register('Menu', menu_factory)
    register('MenuBar', menu_bar_factory)
    register('MPLCanvas', mpl_canvas_factory)
    register('MultilineField', multiline_field_factory)
    register('Notebook', notebook_factory)
    register('Page', page_factory)
    register('PushButton', push_button_factory)
    register('ProgressBar', progress_bar_factory)
    register('RadioButton', radio_button_factory)
    register('ScrollArea', scroll_area_factory)
    register('Separator', separator_factory)
    register('Slider', slider_factory)
    register('SpinBox', spin_box_factory)
    register('SplitItem', split_item_factory)
    register('Splitter', splitter_factory)
    register('Stack', stack_factory)
    register('StackItem', stack_item_factory)
    register('TimeSelector', time_selector_factory)
    register('ToolBar', tool_bar_factory)
    register('WebView', web_view_factory)
    register('Window', window_factory)
