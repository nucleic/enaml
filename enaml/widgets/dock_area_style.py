#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom

from enaml.colors import ColorMember, Color
from enaml.fonts import FontMember


class DockAreaStyle(Atom):
    """ A class used to define the style to apply to the dock area.

    The developer is not required to explicitly specify all of the
    style values. The toolkit will apply an appropriate default for
    any value which is not explicitly provided.

    """
    #: The background color of a dock area.
    dock_area_background = ColorMember()

    #: The background color of a splitter handle.
    splitter_handle_background = ColorMember()

    #: The background color of a dock windows.
    dock_window_background = ColorMember()

    #: The border color of a dock window.
    dock_window_border = ColorMember()

    #: The background color of a dock container.
    dock_container_background = ColorMember()

    #: The border color of a floating dock container.
    dock_container_border = ColorMember()

    #: The background color of a dock item.
    dock_item_background = ColorMember()

    #: The background color of a dock item title bar.
    title_bar_background = ColorMember()

    #: The foreground color of a dock item title bar.
    title_bar_foreground = ColorMember()

    #: The font of a dock item title bar.
    title_bar_font = FontMember()

    #: The background color of a tab in a dock tab bar.
    tab_background = ColorMember()

    #: The background color of a hovered tab in a dock tab bar.
    tab_hover_background = ColorMember()

    #: The background color of a selected tab in a dock tab bar.
    tab_selected_background = ColorMember()

    #: The foreground color of a tab in the dock tab bar.
    tab_foreground = ColorMember()

    #: The foreground color of a hovered tab in a dock tab bar.
    tab_hover_foreground = ColorMember()

    #: The foreground color of a selected tab in a dock tab bar.
    tab_selected_foreground = ColorMember()


def vs_2010_style():
    """ A style which is inspired by Visual Studio 2010.

    """
    return DockAreaStyle(
        dock_area_background=Color(49, 67, 98),
        splitter_handle_background=Color(0, 0, 0, 0),
        dock_window_background=Color(53, 73, 106),
        dock_window_border=Color(40, 60, 90),
        dock_container_background=Color(53, 73, 106),
        dock_container_border=Color(40, 60, 90),
        dock_item_background=Color(240, 240, 240),
        title_bar_background=Color(77, 96, 130),
        title_bar_foreground=Color(250, 251, 254),
        title_bar_font='9pt "Segoe UI"',
        tab_background=Color(255, 255, 255, 15),
        tab_hover_background=Color(76, 105, 153),
        tab_selected_background=Color(240, 240, 240),
        tab_foreground=Color(250, 251, 254),
        tab_selected_foreground=Color(0, 0, 0),
    )


def grey_wind_style():
    """ A mild grey and brown color scheme.

    Inspired by:
        http://www.colourlovers.com/palette/2866138/Grey_Wind

    """
    return DockAreaStyle(
        dock_area_background=Color(139, 131, 129),
        splitter_handle_background=Color(0, 0, 0, 0),
        dock_window_background=Color(175, 182, 190),
        dock_window_border=Color(144, 144, 152),
        dock_container_background=Color(175, 178, 183),
        dock_container_border=Color(144, 144, 152),
        dock_item_background=Color(244, 244, 244),
        title_bar_background=Color(144, 144, 152),
        title_bar_foreground=Color(244, 244, 244),
        title_bar_font='9pt "Segoe UI"',
        tab_background=Color(255, 255, 255, 35),
        tab_foreground=Color(244, 244, 244),
        tab_hover_background=Color(193, 191, 196),
        tab_hover_foreground=Color(70, 70, 70),
        tab_selected_background=Color(244, 244, 244),
        tab_selected_foreground=Color(0, 0, 0),
    )


def new_moon_style():
    """ A yellow, brown, and grey scheme which has lights and darks.

    Inspired by:
        http://www.colourlovers.com/palette/90734/Newly_Risen_Moon

    """
    return DockAreaStyle(
        dock_area_background=Color(54, 57, 59),
        splitter_handle_background=Color(0, 0, 0, 0),
        dock_window_background=Color(197, 188, 142),
        dock_window_border=Color(105, 103, 88),
        dock_container_background=Color(62, 72, 75),
        dock_container_border=Color(54, 57, 59),
        dock_item_background=Color(240, 240, 240),
        title_bar_background=Color(105, 103, 88),
        title_bar_foreground=Color(244, 244, 244),
        title_bar_font='9pt "Segoe UI"',
        tab_background=Color(255, 255, 255, 30),
        tab_foreground=Color(244, 244, 244),
        tab_hover_background=Color(197, 188, 142),
        tab_selected_background=Color(240, 240, 240),
        tab_selected_foreground=Color(0, 0, 0),
    )


def daydreamer_style():
    """ A tempered olive colored theme.

    Inspired by:
        http://www.colourlovers.com/palette/590207/d_a_y_d_r_e_a_m_e_r

    """
    return DockAreaStyle(
        dock_area_background=Color(168, 168, 120),
        splitter_handle_background=Color(0, 0, 0, 0),
        dock_window_background=Color(131, 144, 116),
        dock_window_border=Color(6, 16, 19),
        dock_container_background=Color(147, 158, 120),
        dock_container_border=Color(6, 16, 19),
        dock_item_background=Color(244, 244, 244),
        title_bar_background=Color(131, 144, 116),
        title_bar_foreground=Color(250, 250, 250),
        title_bar_font='9pt "Segoe UI"',
        tab_background=Color(255, 255, 255, 35),
        tab_foreground=Color(244, 244, 244),
        tab_hover_background=Color(205, 205, 118),
        tab_selected_background=Color(244, 244, 244),
        tab_selected_foreground=Color(6, 16, 19),
    )
