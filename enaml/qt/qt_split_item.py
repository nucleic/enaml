#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.split_item import ProxySplitItem

from .QtGui import QFrame, QSplitter, QLayout

from .q_single_widget_layout import QSingleWidgetLayout
from .qt_container import QtContainer
from .qt_widget import QtWidget


class QSplitItem(QFrame):
    """ A QFrame subclass which acts as an item in a QSplitter.

    """
    def __init__(self, parent=None):
        """ Initialize a QSplitItem.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget of the split item, or None if it has no
            parent.

        """
        super(QSplitItem, self).__init__(parent)
        self._split_widget = None
        self.setLayout(QSingleWidgetLayout())
        self.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)

    def splitWidget(self):
        """ Get the split widget for this split item.

        Returns
        -------
        result : QWidget or None
            The split widget being managed by this item.

        """
        return self._split_widget

    def setSplitWidget(self, widget):
        """ Set the split widget for this split item.

        Parameters
        ----------
        widget : QWidget
            The QWidget to use as the split widget in this item.

        """
        self._split_widget = widget
        self.layout().setWidget(widget)

    def stretch(self):
        """ Get the stretch factor for this split item.

        Returns
        -------
        result : int
            The stretch factor for this split item.

        """
        # horizontal and vertical stretch are set to be the same,
        # so which one is returned here is irrelevant.
        return self.sizePolicy().horizontalStretch()

    def setStretch(self, stretch):
        """ Set the stretch factor for this split item.

        Parameters
        ----------
        stretch : int
            The stretch factor to use for this split item.

        """
        stretch = max(0, stretch)
        policy = self.sizePolicy()
        policy.setHorizontalStretch(stretch)
        policy.setVerticalStretch(stretch)
        self.setSizePolicy(policy)

    def collapsible(self):
        """ Get whether or not this widget is collapsible.

        Returns
        -------
        result : bool
            Whether or not this item can be collapsed to zero size.

        """
        parent = self.parentWidget()
        if isinstance(parent, QSplitter):
            return parent.isCollapsible(parent.indexOf(self))
        return False

    def setCollapsible(self, collapsible):
        """ Set whether or not this widget is collapsible.

        Parameters
        ----------
        collapsible : bool
            Whether or not this item can be collapsed to zero size.
            This holds regardless of the minimum size of the item.

        """
        parent = self.parentWidget()
        if isinstance(parent, QSplitter):
            return parent.setCollapsible(parent.indexOf(self), collapsible)


class QtSplitItem(QtWidget, ProxySplitItem):
    """ A Qt implementation of an Enaml ProxySplitItem.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QSplitItem)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QStackItem widget.

        """
        self.widget = QSplitItem(self.parent_widget())

    def init_widget(self):
        """ Initialize the underyling widget.

        """
        super(QtSplitItem, self).init_widget()
        d = self.declaration
        self.set_stretch(d.stretch)
        self.set_collapsible(d.collapsible)

    def init_layout(self):
        """ Initialize the layout for the underyling widget.

        """
        super(QtSplitItem, self).init_layout()
        self.widget.setSplitWidget(self.split_widget())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def split_widget(self):
        """ Find and return the split widget child for this widget.

        """
        d = self.declaration.split_widget()
        if d is not None:
            return d.proxy.widget

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtSplitItem.

        """
        super(QtSplitItem, self).child_added(child)
        if isinstance(child, QtContainer):
            self.widget.setSplitWidget(self.split_widget())

    def child_removed(self, child):
        """ Handle the child removed event for a QtSplitItem.

        """
        super(QtSplitItem, self).child_removed(child)
        if isinstance(child, QtContainer):
            self.widget.setSplitWidget(self.split_widget())

    #--------------------------------------------------------------------------
    # ProxySplitItem API
    #--------------------------------------------------------------------------
    def set_stretch(self, stretch):
        """ Set the stretch factor for the underlying widget.

        """
        self.widget.setStretch(stretch)

    def set_collapsible(self, collapsible):
        """ Set the collapsible flag for the underlying widget.

        """
        self.widget.setCollapsible(collapsible)
