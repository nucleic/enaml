#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from contextlib import contextmanager
import os

from atom.api import (
    Bool, Coerced, Enum, Typed, ForwardTyped, Unicode, Event, observe,
    set_default
)

from enaml.core.declarative import d_
from enaml.layout.dock_layout import (
    DockLayout, DockLayoutValidator, DockLayoutOp
)

from .constraints_widget import ConstraintsWidget, ProxyConstraintsWidget
from .dock_events import DockEvent
from .dock_item import DockItem



if os.environ.get('ENAML_DEPRECATED_DOCK_LAYOUT'):

    from enaml.layout.dock_layout import (
        docklayout, dockarea, dockitem, docksplit, docktabs
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

    def set_live_drag(self, live_drag):
        raise NotImplementedError

    def set_style(self, style):
        raise NotImplementedError

    def set_dock_events_enabled(self, enabled):
        raise NotImplementedError

    def save_layout(self):
        raise NotImplementedError

    def apply_layout(self, layout):
        raise NotImplementedError

    def update_layout(self, ops):
        raise NotImplementedError


class DockArea(ConstraintsWidget):
    """ A component which aranges dock item children.

    """
    if os.environ.get('ENAML_DEPRECATED_DOCK_LAYOUT'):

        layout = d_(Coerced(docklayout, (None,), coercer=coerce_layout))

    else:

        #: The layout of dock items for the area. This attribute is *not*
        #: kept in sync with the layout state of the widget at runtime. The
        #: 'save_layout' method should be called to retrieve the current
        #: layout state.
        layout = d_(Coerced(DockLayout, ()))

        def _post_validate_layout(self, old, new):
            """ Post validate the layout using the DockLayoutValidator.

            """
            available = (i.name for i in self.dock_items())
            DockLayoutValidator(available)(new)
            return new

    #: The default tab position for newly created dock tabs.
    tab_position = d_(Enum('top', 'bottom', 'left', 'right'))

    #: Whether the dock items resize as a dock splitter is being dragged
    #: (True), or if a simple indicator is drawn until the drag handle
    #: is released (False). The default is True.
    live_drag = d_(Bool(True))

    #: The style to apply to the dock area. The default style resembles
    #: Visual Studio 2010. The builtin styles are: 'vs-2010', 'grey-wind',
    #: 'new-moon', and 'metro'.
    style = d_(Unicode('vs-2010'))

    #: Whether or not dock events are enabled for the area.
    dock_events_enabled = d_(Bool(False))

    #: An event emitted when a dock event occurs in the dock area.
    #: `dock_events_enabled` must be True in order to recieve events.
    dock_event = d_(Event(DockEvent), writable=False)

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
        if os.environ.get('ENAML_DEPRECATED_DOCK_LAYOUT'):
            assert isinstance(layout, docklayout), 'layout must be a docklayout'
        else:
            assert isinstance(layout, DockLayout), 'layout must be a DockLayout'
            available = (i.name for i in self.dock_items())
            DockLayoutValidator(available)(layout)
        if self.proxy_is_active:
            return self.proxy.apply_layout(layout)

    def update_layout(self, ops):
        """ Update the layout configuration using layout operations.

        Paramters
        ---------
        ops : DockLayoutOp or iterable
            A single DockLayoutOp instance or an iterable of the same.
            The operations will be executed in order. If a given op is
            not valid for the current layout state, it will be skipped.

        """
        if isinstance(ops, DockLayoutOp):
            ops = [ops]
        for op in ops:
            assert isinstance(op, DockLayoutOp)
        if self.proxy_is_active:
            self.proxy.update_layout(ops)

    if os.environ.get('ENAML_DEPRECATED_DOCK_LAYOUT'):

        def apply_layout_op(self, op, direction, *item_names):
            """ This method is deprecated.

            """
            assert op in ('split_item', 'tabify_item', 'split_area')
            assert direction in ('left', 'right', 'top', 'bottom')
            if not self.proxy_is_active:
                return

            from enaml.layout.dock_layout import (
                InsertItem, InsertBorderItem, InsertTab
            )

            ops = []
            item_names = list(item_names)
            if op == 'split_item':
                target = item_names.pop(0)
                for name in item_names:
                    l_op = InsertItem(
                        target=target, item=name, position=direction
                    )
                    ops.append(l_op)
            elif op == 'split_area':
                for name in item_names:
                    l_op = InsertBorderItem(item=name, position=direction)
                    ops.append(l_op)
            else:
                target = item_names.pop(0)
                for name in item_names:
                    l_op = InsertTab(
                        target=target, item=name, tab_position=direction
                    )
                    ops.append(l_op)
            self.proxy.update_layout(ops)

        def split(self, direction, *item_names):
            """ This method is deprecated.

            """
            self.apply_layout_op('split_area', direction, *item_names)

    @contextmanager
    def suppress_dock_events(self):
        """ A context manager which supresses dock events.

        This manager will disable dock events for the duration of the
        context, and restore the old value upon exit.

        """
        enabled = self.dock_events_enabled
        self.dock_events_enabled = False
        yield
        self.dock_events_enabled = enabled

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('layout')
    def _update_layout(self, change):
        """ An observer which updates the layout when it changes.

        """
        if change['type'] == 'update':
            self.apply_layout(change['value'])

    @observe(('tab_position', 'live_drag', 'style', 'dock_events_enabled'))
    def _update_proxy(self, change):
        """ Update the proxy when the area state changes.

        """
        # The superclass implementation is sufficient.
        super(DockArea, self)._update_proxy(change)
