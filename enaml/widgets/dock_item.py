#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os

from atom.api import (
    Coerced, Event, Unicode, Bool, Range, Typed, ForwardTyped, observe
)

from enaml.application import deferred_call
from enaml.core.declarative import d_
from enaml.icon import Icon
from enaml.layout.geometry import Size

from .container import Container
from .widget import Widget, ProxyWidget


class ProxyDockItem(ProxyWidget):
    """ The abstract definition of a proxy DockItem object.

    """
    #: A reference to the DockItem declaration.
    declaration = ForwardTyped(lambda: DockItem)

    def set_title(self, title):
        raise NotImplementedError

    def set_title_editable(self, editable):
        raise NotImplementedError

    def set_title_bar_visible(self, visible):
        raise NotImplementedError

    def set_icon(self, icon):
        raise NotImplementedError

    def set_icon_size(self, size):
        raise NotImplementedError

    def set_stretch(self, stretch):
        raise NotImplementedError

    def set_closable(self, closable):
        raise NotImplementedError


class DockItem(Widget):
    """ A widget which can be docked in a DockArea.

    A DockItem is a widget which can be docked inside of a DockArea. It
    can have at most a single Container child widget.

    """
    #: The title to use in the title bar.
    title = d_(Unicode())

    #: Whether or the not the title is user editable.
    title_editable = d_(Bool(False))

    #: Whether or not the title bar is visible.
    title_bar_visible = d_(Bool(True))

    #: The icon to use in the title bar.
    icon = d_(Typed(Icon))

    #: The size to use for the icon in the title bar.
    icon_size = d_(Coerced(Size, (-1, -1)))

    #: The stretch factor for the item when docked in a splitter.
    stretch = d_(Range(low=0, value=1))

    #: Whether or not the dock item is closable via a close button.
    closable = d_(Bool(True))

    #: An event emitted when the title bar is right clicked.
    title_bar_right_clicked = d_(Event(), writable=False)

    #: An event emitted when the dock item is closed. The item will be
    #: destroyed after this event has completed.
    closed = d_(Event(), writable=False)

    #: A reference to the ProxyDockItem object.
    proxy = Typed(ProxyDockItem)

    def dock_widget(self):
        """ Get the dock widget defined for the dock pane.

        The last child Container is considered the dock widget.

        """
        for child in reversed(self.children):
            if isinstance(child, Container):
                return child

    if os.environ.get('ENAML_DEPRECATED_DOCK_LAYOUT'):

        def split(self, direction, *names):
            """ This method is deprecated.

            """
            args = ('split_item', direction, self.name) + names
            self._call_parent('apply_layout_op', *args)

        def tabify(self, direction, *names):
            """ This method is deprecated.

            """
            args = ('tabify_item', direction, self.name) + names
            self._call_parent('apply_layout_op', *args)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('title', 'title_editable', 'title_bar_visible', 'icon',
        'icon_size', 'stretch', 'closable'))
    def _update_proxy(self, change):
        """ Update the proxy when the item state changes.

        """
        # The superclass implementation is sufficient.
        super(DockItem, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _item_closed(self):
        """ Called by the proxy when the toolkit item is closed.

        """
        # TODO allow the user to veto the close request
        self.closed()
        deferred_call(self.destroy)

    def _call_parent(self, name, *args, **kwargs):
        """ Call a parent method with the given name and arguments.

        """
        # Avoid a circular import
        from .dock_area import DockArea
        parent = self.parent
        if isinstance(parent, DockArea):
            getattr(parent, name)(*args, **kwargs)
