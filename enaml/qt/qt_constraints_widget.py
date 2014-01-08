#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from contextlib import contextmanager

from atom.api import Callable, ForwardTyped, Typed

from enaml.layout.layout_helpers import expand_constraints
from enaml.layout.layout_manager import LayoutItem
from enaml.widgets.constraints_widget import ProxyConstraintsWidget

from .QtCore import QRect

from .qt_widget import QtWidget


# keep around for backwards compatibility
def size_hint_guard(obj):
    return obj.size_hint_guard()


class QtLayoutItem(LayoutItem):
    """ A concrete LayoutItem implementation for a constraints widget.

    """
    #: The constraints widget owner of the layout item. This will be
    #: assigned by the container when it creates the layout item.
    owner = ForwardTyped(lambda: QtConstraintsWidget)

    def constrainable(self):
        """ Get a reference to the underlying constrainable object.

        Returns
        -------
        result : Contrainable
            An object which implements the Constrainable interface.

        """
        return self.owner.declaration

    def margins(self):
        """ Get the margins for the underlying widget.

        Returns
        -------
        result : tuple
            An empty tuple as constraints widgets do not have margins.

        """
        return ()

    def size_hint(self):
        """ Get the size hint for the underlying widget.

        Returns
        -------
        result : tuple
            A 2-tuple of numbers representing the (width, height)
            size hint of the widget.

        """
        hint = self.owner.widget_item.sizeHint()
        return (hint.width(), hint.height())

    def strength_object(self):
        """ Get a reference to an object which holds strength strings.

        Returns
        -------
        result : object
            An appropriate strength object.

        """
        return self.owner.declaration

    def layout_constraints(self):
        """ Get the user-defined layout constraints for the item.

        Returns
        -------
        result : list
            The list of user-defined layout constraints.

        """
        d = self.owner.declaration
        return expand_constraints(d, d.layout_constraint())

    def set_geometry(self, x, y, width, height):
        """ Set the geometry of the underlying widget.

        This abstract method must be implemented by subclasses.

        Parameters
        ----------
        x : float
            The new value for the x-origin of the widget.

        y : float
            The new value for the y-origin of the widget.

        width : float
            The new value for the width of the widget.

        height : float
            The new value for the height of the widget.

        """
        self.owner.widget_item.setGeometry(QRect(x, y, width, height))


class QtConstraintsWidget(QtWidget, ProxyConstraintsWidget):
    """ A Qt implementation of an Enaml ProxyConstraintsWidget.

    """
    #: The relayout request handler for the widget. This is assigned
    #: by an ancestor container during the layout building pass.
    relayout_handler = Callable()

    #: The size hint update handler for the widget. This is assigned
    #: by an ancestor container during the layout building pass.
    size_hint_handler = Callable()

    #: The layout item for the constraint widget. This will be
    #: created and assigned during a layout pass.
    layout_item = Typed(QtLayoutItem)

    def destroy(self):
        """ A reimplemented destructor.

        This destructor breaks the reference cycle with the layout item.

        """
        super(QtConstraintsWidget, self).destroy()
        item = self.layout_item
        if item is not None:
            item.owner = None
            del self.layout_item

    #--------------------------------------------------------------------------
    # ProxyConstraintsWidget API
    #--------------------------------------------------------------------------
    def request_relayout(self):
        """ Request a relayout of the proxy widget.

        This method forwards the request to the layout handler.

        """
        handler = self.relayout_handler
        if handler is not None:
            handler()

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

        This method forwards the update to the layout notifier.

        """
        handler = self.size_hint_handler
        if handler is not None:
            handler(self)

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
