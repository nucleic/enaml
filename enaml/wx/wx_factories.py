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


def form_factory():
    from .wx_form import WxForm
    return WxForm


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


# def text_editor_factory():
#     from .wx_text_editor import WxTextEditor
#     return WxTextEditor


def tool_bar_factory():
    from .wx_tool_bar import WxToolBar
    return WxToolBar


def window_factory():
    from .wx_window import WxWindow
    return WxWindow


def register_default():
    from .wx_widget_registry import WxWidgetRegistry
    reg = WxWidgetRegistry.register
    register = lambda name, factory: reg(name, factory, 'default')
    register('Action', action_factory)
    register('ActionGroup', action_group_factory)
    register('Calendar', calendar_factory)
    register('CheckBox', check_box_factory)
    register('ComboBox', combo_box_factory)
    register('Container', container_factory)
    register('DateSelector', date_selector_factory)
    register('DockPane', dock_pane_factory)
    register('Field', field_factory)
    register('Form', form_factory)
    register('GroupBox', group_box_factory)
    register('Html', html_factory)
    register('Label', label_factory)
    register('MainWindow', main_window_factory)
    register('Menu', menu_factory)
    register('MenuBar', menu_bar_factory)
    register('MPLCanvas', mpl_canvas_factory)
    register('Notebook', notebook_factory)
    register('Page', page_factory)
    register('PushButton', push_button_factory)
    register('ProgressBar', progress_bar_factory)
    register('RadioButton', radio_button_factory)
    register('ScrollArea', scroll_area_factory)
    register('Slider', slider_factory)
    register('SpinBox', spin_box_factory)
    register('SplitItem', split_item_factory)
    register('Splitter', splitter_factory)
    register('ToolBar', tool_bar_factory)
    register('Window', window_factory)
