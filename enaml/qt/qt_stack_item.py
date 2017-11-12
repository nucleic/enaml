#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.stack_item import ProxyStackItem

from .QtWidgets import QFrame

from .q_single_widget_layout import QSingleWidgetLayout
from .qt_container import QtContainer
from .qt_widget import QtWidget


class QStackItem(QFrame):
    """ A QFrame subclass which acts as an item QStack.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a QStackItem.

        Parameters
        ----------
        *args, **kwargs
            The position and keyword arguments required to initialize
            a QWidget.

        """
        super(QStackItem, self).__init__(*args, **kwargs)
        self._stack_widget = None
        self.setLayout(QSingleWidgetLayout())

    def stackWidget(self):
        """ Get the stack widget for this stack item.

        Returns
        -------
        result : QWidget or None
            The stack widget being managed by this item.

        """
        return self._stack_widget

    def setStackWidget(self, widget):
        """ Set the stack widget for this stack item.

        Parameters
        ----------
        widget : QWidget
            The QWidget to use as the stack widget in this item.

        """
        self._stack_widget = widget
        self.layout().setWidget(widget)


class QtStackItem(QtWidget, ProxyStackItem):
    """ A Qt implementation of an Enaml ProxyStackItem.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QStackItem)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QStackItem widget.

        """
        self.widget = QStackItem(self.parent_widget())

    def init_layout(self):
        """ Initialize the layout for the underyling widget.

        """
        super(QtStackItem, self).init_layout()
        self.widget.setStackWidget(self.stack_widget())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def stack_widget(self):
        """ Find and return the stack widget child for this widget.

        """
        d = self.declaration.stack_widget()
        if d is not None:
            return d.proxy.widget

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtStackItem.

        """
        super(QtStackItem, self).child_added(child)
        if isinstance(child, QtContainer):
            self.widget.setStackWidget(self.stack_widget())

    def child_removed(self, child):
        """ Handle the child added event for a QtStackItem.

        """
        super(QtStackItem, self).child_removed(child)
        if isinstance(child, QtContainer):
            self.widget.setStackWidget(self.stack_widget())

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_visible(self, visible):
        """ An overridden visibility setter.

        This setter disables changing visibility on the widget since
        the visibility is controlled entirely by the parent stack.

        """
        pass
