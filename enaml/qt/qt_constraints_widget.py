#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from contextlib import contextmanager

from atom.api import Atom, ForwardTyped, List, Typed

from enaml.widgets.constraints_widget import ProxyConstraintsWidget

from .QtCore import QRect

from .qt_widget import QtWidget


# Keeping around for backwards compatibility
def size_hint_guard(obj):
    return obj.size_hint_guard()


def QtContainer():
    from .qt_container import QtContainer
    return QtContainer


class ConstraintCache(Atom):
    """ A class which holds cached constraint lists.

    The cached is manipulated directly by the layout container.

    """
    #: The list of cached size hint constraints.
    size_hint = List()


class QtConstraintsWidget(QtWidget, ProxyConstraintsWidget):
    """ A Qt implementation of an Enaml ProxyConstraintsWidget.

    """
    #: The ancestor QtContainer which handles layout for this widget.
    layout_container = ForwardTyped(QtContainer)

    #: The constraint cache for this constraint widget.
    constraint_cache = Typed(ConstraintCache, ())

    def destroy(self):
        """ An overridden destructor method.

        This destructor drops the reference to the layout container.

        """
        del self.layout_container
        super(QtConstraintsWidget, self).destroy()

    #--------------------------------------------------------------------------
    # ProxyConstraintsWidget API
    #--------------------------------------------------------------------------
    def request_relayout(self):
        """ Request a relayout of the proxy widget.

        This call will forward the request to the layout container.

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
    def relayout(self):
        """ Perform an immediate relayout of the proxy widget.

        This call will forward the call to the layout container.

        """
        container = self.layout_container
        if container is not None:
            container.relayout()

    def size_hint_updated(self):
        """ Notify the layout system that the size hint has changed.

        This call will inform the layout container of the change.

        """
        container = self.layout_container
        if container is not None:
            container.size_hint_changed(self)

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

    def update_geometry(self, dx, dy):
        """ Update the geometry of the underlying widget.

        This method is invoked by the layout engine when new values
        for the position and/or size of the widget are available.

        Parameters
        ----------
        dx : float
            The x origin offset to subtract from the left value.

        dy : float
            The y origin offset to subtract from the top value.

        Returns
        -------
        result : tuple
            A 2-tuple of floats representing the x, y widget origin.

        """
        d = self.declaration
        x = d.left.value()
        y = d.top.value()
        w = d.width.value()
        h = d.height.value()
        self.widget_item.setGeometry(QRect(x - dx, y - dy, w, h))
        return x, y
