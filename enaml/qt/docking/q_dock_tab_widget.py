#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QMetaObject
from PyQt4.QtGui import QApplication, QTabBar, QTabWidget


class QDockTabBar(QTabBar):
    """ A custom QTabBar that manages safetly undocking a tab.

    The user can undock a tab by holding Shift before dragging the tab.
    This tab bar assumes that its parent is a QTabWidget and that the
    tabs in the tab widget are QDockItem instances.

    """
    def __init__(self, parent=None):
        """ Initialize a QDockTabBar.

        Parameters
        ----------
        parent : QWidget or None
            The parent widget for the tab bar.

        """
        super(QDockTabBar, self).__init__(parent)
        self.setSelectionBehaviorOnRemove(QTabBar.SelectPreviousTab)
        self._press_pos = None

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def mousePressEvent(self, event):
        """ Handle the mouse press event for the tab bar.

        If the shift key is pressed, and the click is over a tab, a
        dock drag is initiated.

        """
        shift = Qt.ShiftModifier
        if event.button() == Qt.LeftButton and event.modifiers() & shift:
            if self.tabAt(event.pos()) != -1 and self._press_pos is None:
                self._press_pos = event.pos()
        super(QDockTabBar, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for the tab bar.

        If the dock drag is initiated and distances is greater than the
        start drag distances, the item will be undocked.

        """
        # Only pass along the event to the superclass if the tab is
        # not being undocked. Forwarding the event causes the tab bar
        # animations to start, which can cause painting artifacts on
        # the remaining tabs after the tab is undocked.
        if self._press_pos is not None:
            dist = (event.pos() - self._press_pos).manhattanLength()
            if dist > QApplication.startDragDistance():
                container = self.parent().widget(self.currentIndex())
                container.untab(event.globalPos())
                self._press_pos = None
        else:
            super(QDockTabBar, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """ Handle the mouse release event for the tab bar.

        This handler resets the internal drag state for the tab bar.

        """
        super(QDockTabBar, self).mouseReleaseEvent(event)
        self._press_pos = None


class QDockTabWidget(QTabWidget):
    """ A custom tab widget for use in the dock area.

    This custom widget ensures that the proper dock tab bar is used. It
    also allows distinguishing dock tab widgets from standard QTabWidget
    instances used elsewhere in the application.

    """
    def __init__(self, parent=None):
        """ Initialize a QDockTabWidget.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget of the tab widget.

        """
        super(QDockTabWidget, self).__init__(parent)
        self.setTabBar(QDockTabBar())
        self.setElideMode(Qt.ElideRight)
        self.setUsesScrollButtons(True)
        self.setTabsClosable(True)
        self.setDocumentMode(True)
        self.setMovable(True)
        self.tabBar().setDrawBase(False)
        self.tabCloseRequested.connect(self._onTabCloseRequested)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _onTabCloseRequested(self, index):
        """ Handle the close request for the given tab index.

        """
        # Invoke the close slot later to allow the signal to return.
        container = self.widget(index)
        QMetaObject.invokeMethod(container, 'close', Qt.QueuedConnection)
