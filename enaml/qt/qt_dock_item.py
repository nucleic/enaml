#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int, Typed

from enaml.widgets.dock_item import ProxyDockItem

from .QtCore import Qt, QSize, Signal
from .QtGui import QIcon

from .docking.q_dock_item import QDockItem

from .q_resource_helpers import get_cached_qicon
from .qt_widget import QtWidget


class QCustomDockItem(QDockItem):
    """ A custom dock item which converts a close event into a signal.

    """
    #: A signal emitted if the close event is accepted. It it emitted
    #: before the close event handler returns.
    closed = Signal()

    def closeEvent(self, event):
        """ Handle the close event for the dock item.

        """
        super(QCustomDockItem, self).closeEvent(event)
        if event.isAccepted():
            self.closed.emit()


# Guard flags
TITLE_GUARD = 0x1


class QtDockItem(QtWidget, ProxyDockItem):
    """ A Qt implementation of an Enaml ProxyDockItem.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QCustomDockItem)

    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QDockItem widget.

        """
        self.widget = QCustomDockItem(self.parent_widget())

    def init_widget(self):
        """ Initialize the state of the underlying widget.

        """
        super(QtDockItem, self).init_widget()
        d = self.declaration
        self.set_name(d.name)
        self.set_title(d.title)
        self.set_title_editable(d.title_editable)
        if not d.title_bar_visible:
            self.set_title_bar_visible(d.title_bar_visible)
        if d.icon is not None:
            self.set_icon(d.icon)
        if -1 not in d.icon_size:
            self.set_icon_size(d.icon_size)
        self.set_stretch(d.stretch)
        self.set_closable(d.closable)

    def init_layout(self):
        """ Initialize the layout for the underyling widget.

        """
        super(QtDockItem, self).init_layout()
        widget = self.widget
        widget.setDockWidget(self.dock_widget())
        # Use a queued connection so the dock manager can finish
        # closing the dock item before the signal handler runs.
        widget.titleEdited.connect(self.on_title_edited)
        widget.titleBarRightClicked.connect(self.on_title_bar_right_clicked)
        widget.closed.connect(self.on_closed, Qt.QueuedConnection)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def dock_widget(self):
        """ Find and return the dock widget child for this widget.

        """
        d = self.declaration.dock_widget()
        if d is not None:
            return d.proxy.widget

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_title_edited(self, text):
        """ Handle the 'titleEdited' signal on the dock item.

        """
        d = self.declaration
        if d is not None:
            self._guard |= TITLE_GUARD
            try:
                d.title = text
            finally:
                self._guard &= ~TITLE_GUARD

    def on_title_bar_right_clicked(self, pos):
        """ Handle the 'titleBarRightClicked' signal on the dock item.

        """
        d = self.declaration
        if d is not None:
            d.title_bar_right_clicked()

    def on_closed(self):
        """ Handle the closed signal from the dock item.

        """
        d = self.declaration
        if d is not None:
            d._item_closed()

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtDockItem.

        """
        super(QtDockItem, self).child_added(child)
        self.widget.setDockWidget(self.dock_widget())

    def child_removed(self, child):
        """ Handle the child added event for a QtDockItem.

        """
        super(QtDockItem, self).child_removed(child)
        self.widget.setDockWidget(self.dock_widget())

    #--------------------------------------------------------------------------
    # ProxyDockItem API
    #--------------------------------------------------------------------------
    def set_name(self, name):
        """ Set the object name on the underlying widget.

        """
        self.widget.setObjectName(name)

    def set_title(self, title):
        """ Set the title on the underlying widget.

        """
        if not self._guard & TITLE_GUARD:
            self.widget.setTitle(title)

    def set_title_editable(self, editable):
        """ Set the title editable state on the underlying widget.

        """
        self.widget.setTitleEditable(editable)

    def set_title_bar_visible(self, visible):
        """ Set the visibility of the widget's title bar.

        """
        self.widget.setTitleBarForceHidden(not visible)

    def set_icon(self, icon):
        """ Set the icon on the underlying widget.

        """
        if icon:
            qicon = get_cached_qicon(icon)
        else:
            qicon = QIcon()
        self.widget.setIcon(qicon)

    def set_icon_size(self, size):
        """ Set the icon size on the underlying widget.

        """
        self.widget.setIconSize(QSize(*size))

    def set_stretch(self, stretch):
        """ Set the stretch factor for the underlyling widget.

        """
        sp = self.widget.sizePolicy()
        sp.setHorizontalStretch(stretch)
        sp.setVerticalStretch(stretch)
        self.widget.setSizePolicy(sp)

    def set_closable(self, closable):
        """ Set the closable flag for the underlying widget.

        """
        self.widget.setClosable(closable)
