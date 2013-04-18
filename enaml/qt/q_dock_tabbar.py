#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QTabBar


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
        if self._press_pos is None:
            super(QDockTabBar, self).mouseMoveEvent(event)
        else:
            dist = (event.pos() - self._press_pos).manhattanLength()
            if dist > QApplication.startDragDistance():
                container = self.parent().widget(self.currentIndex())
                container.handler.untab(event.globalPos())
                self._press_pos = None

    def mouseReleaseEvent(self, event):
        """ Handle the mouse release event for the tab bar.

        This handler will release the press state of the tabs.

        """
        if self._press_pos is None:
            super(QDockTabBar, self).mouseReleaseEvent(event)
        else:
            self._press_pos = None
