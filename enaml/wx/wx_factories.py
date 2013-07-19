#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
def action_factory():
    from .wx_action import WxAction
    return WxAction


def action_group_factory():
    from .wx_action_group import WxActionGroup
    return WxActionGroup


def calendar_factory():
    from .wx_calendar import WxCalendar
    return WxCalendar


def check_box_factory():
    from .wx_check_box import WxCheckBox
    return WxCheckBox


def combo_box_factory():
    from .wx_combo_box import WxComboBox
    return WxComboBox


def container_factory():
    from .wx_container import WxContainer
    return WxContainer


def date_selector_factory():
    from .wx_date_selector import WxDateSelector
    return WxDateSelector


# def datetime_selector_factory():
#     from .wx_datetime_selector import WxDatetimeSelector
#     return WxDatetimeSelector


def dock_pane_factory():
    from .wx_dock_pane import WxDockPane
    return WxDockPane


def field_factory():
    from .wx_field import WxField
    return WxField


def group_box_factory():
    from .wx_group_box import WxGroupBox
    return WxGroupBox


def html_factory():
    from .wx_html import WxHtml
    return WxHtml


# def image_view_factory():
#     from .wx_image_view import WxImageView
#     return WxImageView


def label_factory():
    from .wx_label import WxLabel
    return WxLabel


def main_window_factory():
    from .wx_main_window import WxMainWindow
    return WxMainWindow


def menu_factory():
    from .wx_menu import WxMenu
    return WxMenu


def menu_bar_factory():
    from .wx_menu_bar import WxMenuBar
    return WxMenuBar


def mpl_canvas_factory():
    from .wx_mpl_canvas import WxMPLCanvas
    return WxMPLCanvas


def notebook_factory():
    from .wx_notebook import WxNotebook
    return WxNotebook


def page_factory():
    from .wx_page import WxPage
    return WxPage


def push_button_factory():
    from .wx_push_button import WxPushButton
    return WxPushButton


def progress_bar_factory():
    from .wx_progress_bar import WxProgressBar
    return WxProgressBar


def radio_button_factory():
    from .wx_radio_button import WxRadioButton
    return WxRadioButton


def scroll_area_factory():
    from .wx_scroll_area import WxScrollArea
    return WxScrollArea


def slider_factory():
    from .wx_slider import WxSlider
    return WxSlider


def spin_box_factory():
    from .wx_spin_box import WxSpinBox
    return WxSpinBox


def split_item_factory():
    from .wx_split_item import WxSplitItem
    return WxSplitItem


def splitter_factory():
    from .wx_splitter import WxSplitter
    return WxSplitter


def tool_bar_factory():
    from .wx_tool_bar import WxToolBar
    return WxToolBar


def window_factory():
    from .wx_window import WxWindow
    return WxWindow


WX_FACTORIES = {
    'Action': action_factory,
    'ActionGroup': action_group_factory,
    'Calendar': calendar_factory,
    'CheckBox': check_box_factory,
    'ComboBox': combo_box_factory,
    'Container': container_factory,
    'DateSelector': date_selector_factory,
    'DockPane': dock_pane_factory,
    'Field': field_factory,
    'GroupBox': group_box_factory,
    'Html': html_factory,
    'Label': label_factory,
    'MainWindow': main_window_factory,
    'Menu': menu_factory,
    'MenuBar': menu_bar_factory,
    'MPLCanvas': mpl_canvas_factory,
    'Notebook': notebook_factory,
    'Page': page_factory,
    'PushButton': push_button_factory,
    'ProgressBar': progress_bar_factory,
    'RadioButton': radio_button_factory,
    'ScrollArea': scroll_area_factory,
    'Slider': slider_factory,
    'SpinBox': spin_box_factory,
    'SplitItem': split_item_factory,
    'Splitter': splitter_factory,
    'ToolBar': tool_bar_factory,
    'Window': window_factory,
}
