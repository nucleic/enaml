#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import cPickle

from atom.api import (
    Coerced, Event, Unicode, Bool, Range, Typed, ForwardTyped, observe
)

import enaml
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

    def alert(self, level, on, off, repeat, persist):
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

    def alert(self, level, on=250, off=250, repeat=4, persist=False):
        """ Set the alert level on the dock item.

        This will override any currently applied alert level.

        Parameters
        ----------
        level : unicode
            The alert level token to apply to the dock item.

        on : int
            The duration of the 'on' cycle, in ms. A value of -1 means
            always on.

        off : int
            The duration of the 'off' cycle, in ms. If 'on' is -1, this
            value is ignored.

        repeat : int
            The number of times to repeat the on-off cycle. If 'on' is
            -1, this value is ignored.

        persist : bool
            Whether to leave the alert in the 'on' state when the cycles
            finish. If 'on' is -1, this value is ignored.

        """
        if self.proxy_is_active:
            self.proxy.alert(level, on, off, repeat, persist)

    def save_state(self):
        """ A method used to save the state of a custom dock item.

        This method is intended to be implemented by subclasses. It is
        invoked by a parent DockArea when the dock area state is saved.
        The created dict will be passed to the 'restore_state' method
        when the dock area restores the saved dock item.

        Returns
        -------
        result : dict
            The dictionary of relevant state information. The contents
            of the dict should be serializable.

        """
        return {'name': self.name, 'title': self.title}

    def restore_state(self, state):
        """ A method used to restore the state of a custom dock item.

        This method is intended to be implemented by subclasses. It is
        invoked by the parent DockArea when the dock area is restored
        from saved state.

        Parameters
        ----------
        state : dict
            The dict returned by a previous call to 'save_state'.

        """
        self.name = state['name']
        self.title = state['title']

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('title', 'title_editable', 'title_bar_visible', 'icon',
        'icon_size', 'stretch', 'closable')
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


def save_dock_item(item):
    """ Save a DockItem to a serializable dictionary.

    Parameters
    ----------
    item : DockItem
        The dock item of interest.

    Returns
    -------
    result : dict
        A serializable dictionary which can be used to reconstruct
        the dock item by invoking the 'restore_dock_item' function.

    """
    assert isinstance(item, DockItem), 'item must be a DockItem'
    data =  {
        'type': cPickle.dumps(type(item)),
        'state': item.save_state(),
    }
    return data


def restore_dock_item(data):
    """ Restore a dock item from its saved information.

    Parameters
    ----------
    data : dict
        The dict returned by a previous call to 'save_dock_item'.

    Returns
    -------
    result : DockItem
        The restored dock item.

    """
    with enaml.imports():
        item_type = cPickle.loads(data['type'])
    item = item_type()
    item.restore_state(data['state'])
    return item
