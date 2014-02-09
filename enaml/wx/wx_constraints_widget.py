#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from contextlib import contextmanager

from atom.api import Int, ForwardTyped

from enaml.widgets.constraints_widget import ProxyConstraintsWidget

from .wx_widget import WxWidget


# keep around for backwards compatibility
def size_hint_guard(obj):
    return obj.geometry_guard()


def WxContainer():
    from .wx_container import WxContainer
    return WxContainer


class WxConstraintsWidget(WxWidget, ProxyConstraintsWidget):
    """ A Wx implementation of an Enaml ProxyConstraintsWidget.

    """
    #: The container which manages the layout for this widget. This
    #: is assigned during the layout building pass.
    layout_container = ForwardTyped(WxContainer)

    #: The layout index for this widget's layout item. This is assigned
    #: during the layout building pass.
    layout_index = Int()

    def destroy(self):
        """ A reimplemented destructor.

        This destructor drops the reference to the layout container.

        """
        del self.layout_container
        super(WxConstraintsWidget, self).destroy()

    #--------------------------------------------------------------------------
    # ProxyConstraintsWidget API
    #--------------------------------------------------------------------------
    def request_relayout(self):
        """ Request a relayout of the proxy widget.

        This method forwards the request to the layout container.

        """
        container = self.layout_container
        if container is not None:
            container.request_relayout()

    #--------------------------------------------------------------------------
    # Layout API
    #--------------------------------------------------------------------------
    def geometry_updated(self):
        """ Notify the layout system that the geometry has changed.

        This method forwards the update to the layout container.

        """
        container = self.layout_container
        if container is not None:
            container.geometry_updated(self)
        self.post_wx_layout_request()

    @contextmanager
    def geometry_guard(self):
        """ A context manager for guarding the geometry of the widget.

        This manager will call 'geometry_updated' if the size hint,
        minimum, or maximum size of the widget has changed.

        """
        widget = self.widget
        old_hint = widget.GetBestSize()
        old_min = widget.GetMinSize()
        old_max = widget.GetMaxSize()
        yield
        if (old_hint != widget.GetBestSize() or
            old_min != widget.GetMinSize() or
            old_max != widget.GetMaxSize()):
            self.geometry_updated()
