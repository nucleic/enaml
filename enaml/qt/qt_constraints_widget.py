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

from .qt_widget import QtWidget


# keep around for backwards compatibility
def size_hint_guard(obj):
    return obj.size_hint_guard()


def QtContainer():
    from .qt_container import QtContainer
    return QtContainer


class QtConstraintsWidget(QtWidget, ProxyConstraintsWidget):
    """ A Qt implementation of an Enaml ProxyConstraintsWidget.

    """
    #: The container which manages the layout for this widget. This
    #: is assigned during the layout building pass.
    layout_container = ForwardTyped(QtContainer)

    #: The layout index for this widget's layout item. This is assigned
    #: during the layout building pass.
    layout_index = Int()

    def destroy(self):
        """ A reimplemented destructor.

        This destructor drops the reference to the layout container.

        """
        del self.layout_container
        super(QtConstraintsWidget, self).destroy()

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

    def restyle(self):
        """ Restyle the widget with the current style data.

        This reimplementation restyles from within a size hint guard.

        """
        with self.size_hint_guard():
            super(QtConstraintsWidget, self).restyle()

    #--------------------------------------------------------------------------
    # Layout API
    #--------------------------------------------------------------------------
    def size_hint_updated(self):
        """ Notify the layout system that the size hint has changed.

        This method forwards the update to the layout container.

        """
        container = self.layout_container
        if container is not None:
            container.size_hint_updated(self)

    @contextmanager
    def size_hint_guard(self):
        """ A contenxt manager for guarding the size hint of the widget.

        This manager will call 'size_hint_updated' if the size hint of
        the widget changes during context execution.

        """
        old_hint = self.widget.sizeHint()
        yield
        new_hint = self.widget.sizeHint()
        if old_hint != new_hint:
            self.size_hint_updated()
