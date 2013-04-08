#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Enum, Unicode, Bool, Range, Typed, ForwardTyped

from enaml.core.declarative import d_

from .container import Container
from .widget import Widget, ProxyWidget


class ProxyDockItem(ProxyWidget):
    """ The abstract definition of a proxy DockItem object.

    """
    #: A reference to the DockItem declaration.
    declaration = ForwardTyped(lambda: DockItem)

    def set_title(self, title):
        raise NotImplementedError

    def set_title_bar_visible(self, visible):
        raise NotImplementedError

    def set_title_bar_position(self, position):
        raise NotImplementedError

    def set_native_window(self, native):
        raise NotImplementedError

    def set_closable(self, closable):
        raise NotImplementedError

    def set_movable(self, movable):
        raise NotImplementedError


class DockItem(Widget):
    """ A widget which can be docked in a DockArea.

    A DockItem is a widget which can be docked inside of a DockArea. It
    can have at most a single Container child widget.

    """
    #: The title to use in the title bar.
    title = d_(Unicode())

    #: Whether or not the title bar is visible.
    title_bar_visible = d_(Bool(True))

    #: The orientation of the title bar.
    title_bar_position = d_(Enum('top', 'bottom', 'left', 'right'))

    #: Whether to use a native window when the dock item is floating.
    native_window = d_(Bool(True))

    #: Whether dock item is collapsible when docked in a splitter.
    collapsible = d_(Bool(True))

    #: The stretch factor for the dock item when docked in a splitter.
    stretch = d_(Range(low=0, value=1))

    #: A reference to the ProxyDockItem object.
    proxy = Typed(ProxyDockItem)

    def dock_widget(self):
        """ Get the dock widget defined for the dock pane.

        The last child Container is considered the dock widget.

        """
        for child in reversed(self.children):
            if isinstance(child, Container):
                return child
