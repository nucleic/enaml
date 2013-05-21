#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QPoint, QMetaObject, QEvent
from PyQt4.QtGui import QApplication, QTabBar, QTabWidget, QMouseEvent


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

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for the tab bar.

        If the dock drag is initiated and distances is greater than the
        start drag distances, the item will be undocked.

        """
        super(QDockTabBar, self).mouseMoveEvent(event)
        pos = event.pos()
        if self.rect().contains(pos):
            return
        x = max(0, min(pos.x(), self.width()))
        y = max(0, min(pos.y(), self.height()))
        dist = (QPoint(x, y) - pos).manhattanLength()
        if dist > QApplication.startDragDistance():
            # Fake a mouse release event so that the tab resets its
            # internal state and finalizes the animation for the tab.
            # The button must be Qt.LeftButton, not event.button().
            btn = Qt.LeftButton
            mod = event.modifiers()
            evt = QMouseEvent(QEvent.MouseButtonRelease, pos, btn, btn, mod)
            QApplication.sendEvent(self, evt)
            container = self.parent().widget(self.currentIndex())
            container.untab(event.globalPos())


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
