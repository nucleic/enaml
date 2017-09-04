#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
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
    return obj.geometry_guard()


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

        This reimplementation restyles from within a geometry guard.

        """
        with self.geometry_guard():
            super(QtConstraintsWidget, self).restyle()

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

    @contextmanager
    def geometry_guard(self):
        """ A context manager for guarding the geometry of the widget.

        If the proxy is fully active, this context manager will call the
        'geometry_updated' method if the size hint, minimum, or maximum
        size of the widget changes during context execution.

        """
        if not self.is_active:
            yield
            return
        widget = self.widget
        old_hint = widget.sizeHint()
        old_min = widget.minimumSize()
        old_max = widget.maximumSize()
        yield
        if (old_hint != widget.sizeHint() or
            old_min != widget.minimumSize() or
            old_max != widget.maximumSize()):
            self.geometry_updated()

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def set_font(self, font):
        """ A reimplemented font setter.

        This method sets the font from within a geometry guard.

        """
        with self.geometry_guard():
            super(QtConstraintsWidget, self).set_font(font)
