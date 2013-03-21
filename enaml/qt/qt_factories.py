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


def dual_slider_factory():
    from .qt_dual_slider import QtDualSlider
    return QtDualSlider


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


def table_view_factory():
    from .qt_table_view import QtTableView
    return QtTableView


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


QT_FACTORIES = {
    'Action': action_factory,
    'ActionGroup': action_group_factory,
    'Calendar': calendar_factory,
    'CheckBox': check_box_factory,
    'ComboBox': combo_box_factory,
    'Container': container_factory,
    'Control': control_factory,
    'DateSelector': date_selector_factory,
    'DatetimeSelector': datetime_selector_factory,
    'DockPane': dock_pane_factory,
    'DualSlider', dual_slider_factory,
    'Field': field_factory,
    'FileDialog': file_dialog_factory,
    'FlowArea': flow_area_factory,
    'FlowItem': flow_item_factory,
    'GroupBox': group_box_factory,
    'Html': html_factory,
    'Image': image_factory,
    'ImageView': image_view_factory,
    'Label': label_factory,
    'ListView': list_view_factory,
    'ListItem': list_item_factory,
    'MainWindow': main_window_factory,
    'MdiArea': mdi_area_factory,
    'MdiWindow': mdi_window_factory,
    'Menu': menu_factory,
    'MenuBar': menu_bar_factory,
    'MPLCanvas': mpl_canvas_factory,
    'MultilineField': multiline_field_factory,
    'Notebook': notebook_factory,
    'Page': page_factory,
    'PushButton': push_button_factory,
    'ProgressBar': progress_bar_factory,
    'RadioButton': radio_button_factory,
    'ScrollArea': scroll_area_factory,
    'Separator': separator_factory,
    'Slider': slider_factory,
    'SpinBox': spin_box_factory,
    'SplitItem': split_item_factory,
    'Splitter': splitter_factory,
    'Stack': stack_factory,
    'StackItem': stack_item_factory,
    'TableView': table_view_factory,
    'TimeSelector': time_selector_factory,
    'ToolBar': tool_bar_factory,
    'WebView': web_view_factory,
    'Window': window_factory,
}