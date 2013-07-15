#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import os

from atom.api import (
    Bool, Coerced, Enum, Typed, ForwardTyped, Unicode, observe, set_default
)

from enaml.core.declarative import d_
from enaml.layout.dock_layout import DockLayout, DockLayoutValidator

from .constraints_widget import ConstraintsWidget, ProxyConstraintsWidget
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

    def save_layout(self):
        raise NotImplementedError

    def apply_layout(self, layout):
        raise NotImplementedError

    if os.environ.get('ENAML_DEPRECATED_DOCK_LAYOUT'):

        def apply_layout_op(self, op, direction, *item_names):
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
            available = set(i.name for i in self.dock_items())
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

    if os.environ.get('ENAML_DEPRECATED_DOCK_LAYOUT'):

        def apply_layout_op(self, op, direction, *item_names):
            """ This method is deprecated.

            """
            assert op in ('split_item', 'tabify_item', 'split_area')
            assert direction in ('left', 'right', 'top', 'bottom')
            if self.proxy_is_active:
                self.proxy.apply_layout_op(op, direction, *item_names)

        def split(self, direction, *item_names):
            """ This method is deprecated.

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

    @observe(('tab_position', 'live_drag', 'style'))
    def _update_proxy(self, change):
        """ Update the proxy when the area state changes.

        """
        # The superclass implementation is sufficient.
        super(DockArea, self)._update_proxy(change)
