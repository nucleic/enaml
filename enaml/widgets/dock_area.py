#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Atom, Coerced, Enum, Typed, ForwardTyped, observe, set_default
)

from enaml.colors import ColorMember, Color
from enaml.core.declarative import d_
from enaml.fonts import FontMember
from enaml.layout.dock_layout import (
    docklayout, dockarea, dockitem, docksplit, docktabs
)

from .constraints_widget import ConstraintsWidget, ProxyConstraintsWidget
from .dock_item import DockItem


class DockAreaStyle(Atom):
    """ A class used to define the style to apply to the dock area.

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


#: A dock area style which resembles Visual Studio 2010
VS_2010_STYLE = DockAreaStyle(
    dock_area_background = Color(49, 67, 98),
    splitter_handle_background = Color(0, 0, 0, 0),
    dock_window_background = Color(53, 73, 106),
    dock_window_border = Color(40, 60, 90),
    dock_container_background = Color(53, 73, 106),
    dock_container_border = Color(40, 60, 90),
    dock_item_background = Color(237, 237, 237),
    title_bar_background = Color(77, 96, 130),
    title_bar_foreground = Color(250, 251, 254),
    title_bar_font = '9pt "Segoe UI"',
    tab_background = Color(255, 255, 255, 15),
    tab_hover_background = Color(76, 105, 153),
    tab_selected_background = Color(237, 237, 237),
    tab_foreground = Color(250, 251, 254),
    tab_selected_foreground = Color(0, 0, 0),
)


#: A dock area style which has a nice contrasting gray style.
GRAY_STYLE = DockAreaStyle(
    dock_area_background = Color(184, 185, 188),
    splitter_handle_background = Color(0, 0, 0, 0),
    dock_window_background = Color(194, 195, 198),
    dock_window_border = Color(128, 128, 128),
    dock_container_background = Color(194, 195, 198),
    dock_container_border = Color(138, 138, 138),
    dock_item_background = Color(237, 237, 237),
    title_bar_background = Color(135, 135, 145),
    title_bar_foreground = Color(250, 251, 254),
    title_bar_font = '9pt "Segoe UI"',
    tab_background = Color(255, 255, 255, 35),
    tab_hover_background = Color(155, 155, 165),
    tab_selected_background = Color(237, 237, 237),
    tab_foreground = Color(0, 0, 0),
    tab_selected_foreground = Color(0, 0, 0),
)

def coerce_layout(thing):
    """ Coerce a variety of objects into a docklayout.

    Parameters
    ----------
    thing : dict, basetring, dockitem, dockarea, split, or tabs
        Something that can be coerced into a dock layout.

    """
    if thing is None:
        return docklayout(None)
    if isinstance(thing, basestring):
        thing = dockitem(thing)
    if isinstance(thing, (dockitem, docksplit, docktabs)):
        return docklayout(dockarea(thing))
    if isinstance(thing, dockarea):
        return docklayout(thing)
    msg = "cannot coerce '%s' to a 'docklayout'"
    raise TypeError(msg % type(thing).__name__)


class ProxyDockArea(ProxyConstraintsWidget):
    """ The abstract definition of a proxy DockArea object.

    """
    #: A reference to the Stack declaration.
    declaration = ForwardTyped(lambda: DockArea)

    def set_tab_position(self, position):
        raise NotImplementedError

    def save_layout(self):
        raise NotImplementedError

    def apply_layout(self, layout):
        raise NotImplementedError

    def apply_layout_op(self, op, direction, *item_names):
        raise NotImplementedError


class DockArea(ConstraintsWidget):
    """ A component which aranges dock item children.

    """
    #: The layout of dock items for the area. The layout can also be
    #: changed at runtime with the 'apply_layout' and 'apply_layout_op'
    #: methods. This attribute is *not* kept in sync with the layout
    #: state of the widget at runtime. The 'save_layout' method should
    #: be called to retrieve the current layout state.
    layout = d_(Coerced(docklayout, (None,), coercer=coerce_layout))

    #: The default tab position for newly created dock tabs.
    tab_position = d_(Enum('top', 'bottom', 'left', 'right'))

    #: The style to apply to the dock area. The default style resembles
    #: the Visual Studio 2010 color scheme.
    style = d_(Typed(DockAreaStyle, factory=lambda: GRAY_STYLE))
    #style = d_(Typed(DockAreaStyle, factory=lambda: VS_2010_STYLE))

    #: A Stack expands freely in height and width by default
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyStack widget.
    proxy = Typed(ProxyDockArea)

    def dock_items(self):
        """ Get the dock items defined on the stack

        """
        return [c for c in self.children if isinstance(c, DockItem)]

    def save_layout(self):
        """ Save the current layout state of the dock area.

        Returns
        -------
        result : docklayout
            The current layout state of the dock area.

        """
        if self.proxy_is_active:
            return self.proxy.save_layout()
        return self.layout

    def apply_layout(self, layout):
        """ Apply a new layout to the dock area.

        Parameters
        ----------
        layout : docklayout
            The docklayout to apply to the dock area.

        """
        assert isinstance(layout, docklayout), 'layout must be a docklayout'
        if self.proxy_is_active:
            return self.proxy.apply_layout(layout)

    def apply_layout_op(self, op, direction, *item_names):
        """ Apply a layout operation to the dock area.

        Parameters
        ----------
        op : str
            The operation to peform. This must be one of 'split_item',
            'tabify_item', or 'split_area'.

        direction : str
            The direction to peform the operation. This must be one of
            'left', 'right', 'top', or 'bottom'.

        *item_names
            The list of string names of the dock items to include in
            the operation. See the notes about the requirements for
            the item names for a given layout operation.

        Notes
        -----
        The item names must meet for the following requirements for the
        various layout operations:

        split_item
            There must be two or more names and they must reference
            dock items which have already been parented by the dock
            area. The first name is used as the item to which the
            operation is applied. The following command will insert
            the dock item 'bar' to the left of dock item 'foo':

                apply_layout_op('split_item', 'left', 'foo', 'bar')

        tabify_item
            There must be two or more names and they must reference
            dock items which have already been parented by the dock
            area. The first name is used as the item to which the
            operation is applied. The following command will create
            a tabbed area out of 'foo' and 'bar' with the tabs at
            the top of the tab widget.

                apply_layout_op('tabify_item', 'top', 'foo', 'bar')

        'split_area'
            There must be one or more names and they must reference
            dock items which have already been parented by the dock
            area. The names are inserted into the dock area in the
            specified direction. The following command will insert
            'foo' and 'bar' to the left side of the dock area.

                apply_layout_op('split_area', 'left', 'foo', 'bar')

        In all cases, conflicting layout specifications will be resolved
        using reasonable behavior. For example, attempting to split an
        item which lives in a tabbed area, will instead tabify the items
        into the existing tab widget.

        Warnings will be emitted if the layout conditions do not hold.

        """
        assert op in ('split_item', 'tabify_item', 'split_area')
        assert direction in ('left', 'right', 'top', 'bottom')
        if self.proxy_is_active:
            self.proxy.apply_layout_op(op, direction, *item_names)

    def split(self, direction, *item_names):
        """ Split the dock area in the given direction.

        This is a convenience method for applying a 'split_area' layout
        operation. See the 'apply_layout_op' method for more info.

        """
        self.apply_layout_op('split_area', direction, *item_names)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('layout')
    def _update_layout(self, change):
        """ An observer which updates the layout when it changes.

        """
        if change['type'] == 'update':
            self.apply_layout(change['value'])

    @observe('tab_position')
    def _update_proxy(self, change):
        """ Update the proxy when the area state changes.

        """
        # The superclass implementation is sufficient.
        super(DockArea, self)._update_proxy(change)
