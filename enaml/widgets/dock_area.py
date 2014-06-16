#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from contextlib import contextmanager

from atom.api import (
    Bool, Coerced, Enum, Typed, ForwardTyped, Unicode, Event, observe,
    set_default
)

from enaml.core.declarative import d_
from enaml.layout.dock_layout import DockLayout, DockLayoutOp
from enaml.styling import StyleSheet

from .constraints_widget import ConstraintsWidget, ProxyConstraintsWidget
from .dock_events import DockEvent
from .dock_item import DockItem


_dock_area_styles = None
def get_registered_styles(name):
    # lazy import the stdlib module in case it's never needed.
    global _dock_area_styles
    if _dock_area_styles is None:
        import enaml
        with enaml.imports():
            from enaml.stdlib import dock_area_styles
        _dock_area_styles = dock_area_styles
    return _dock_area_styles.get_registered_styles(name)


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
    """ A component which arranges dock item children.

    """
    #: The layout of dock items for the area. This attribute is *not*
    #: kept in sync with the layout state of the widget at runtime. The
    #: 'save_layout' method should be called to retrieve the current
    #: layout state.
    layout = d_(Coerced(DockLayout, ()))

    #: The default tab position for newly created dock tabs.
    tab_position = d_(Enum('top', 'bottom', 'left', 'right'))

    #: Whether the dock items resize as a dock splitter is being dragged
    #: (True), or if a simple indicator is drawn until the drag handle
    #: is released (False). The default is True.
    live_drag = d_(Bool(True))

    #: The name of the registered style to apply to the dock area. The
    #: list of available styles can be retrieved by calling the function
    #: `available_styles` in the `enaml.stdlib.dock_area_styles` module.
    #: The default is a style inspired by Visual Studio 2010
    #:
    #: Users can also define and use their own custom style sheets with
    #: the dock area. Simply set this attribute to an empty string so
    #: the default styling is disabled, and proceed to use style sheets
    #: as with any other widget (see the stdlib styles for inspiration).
    #:
    #: Only one mode of styling should be used for the dock area at a
    #: time. Using both modes simultaneously is undefined.
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

    #: The style sheet created from the 'style' attribute.
    _internal_style = Typed(StyleSheet)

    def initialized(self):
        """ A reimplemented initializer method.

        This method ensures the internal style sheet is created.

        """
        super(DockArea, self).initialized()
        self._refresh_internal_style()

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
        layout : DockLayout
            The dock layout to apply to the dock area.

        """
        assert isinstance(layout, DockLayout), 'layout must be a DockLayout'
        if self.proxy_is_active:
            return self.proxy.apply_layout(layout)

    def update_layout(self, ops):
        """ Update the layout configuration using layout operations.

        Parameters
        ----------
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
    @observe('style')
    def _update_style(self, change):
        """ An observer which updates the internal style sheet.

        """
        change_t = change['type']
        if change_t == 'update' or change_t == 'delete':
            self._refresh_internal_style()

    @observe('layout')
    def _update_layout(self, change):
        """ An observer which updates the layout when it changes.

        """
        if change['type'] == 'update':
            self.apply_layout(change['value'])

    @observe('tab_position', 'live_drag', 'style', 'dock_events_enabled')
    def _update_proxy(self, change):
        """ Update the proxy when the area state changes.

        """
        # The superclass implementation is sufficient.
        super(DockArea, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _refresh_internal_style(self):
        old = self._internal_style
        if old is not None:
            old.destroy()
            self._internal_style = None
        if self.style:
            style_t = get_registered_styles(self.style)
            if style_t is not None:
                sheet = StyleSheet()
                style_t()(sheet)
                self._internal_style = sheet
                sheet.set_parent(self)
