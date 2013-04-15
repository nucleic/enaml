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
    # Private API
    #--------------------------------------------------------------------------
    def _initDrag(self, pos):
        """ Initialize the drag state for the tab.

        If the drag state is already inited, this method is a no-op.

        Parameters
        ----------
        pos : QPoint
            The point where the user clicked the mouse, expressed in
            the local coordinate system.

        """
        if self._press_pos is not None:
            return
        self._press_pos = pos

    def _startDrag(self, pos):
        """" Start the drag process for the dock item.

        This method unplugs the dock item from the layout and transfers
        the repsonsibilty of moving the floating frame back to the dock
        item. After calling this method, no mouseReleaseEvent will be
        generated since the dock item grabs the mouse. If the item is
        already being dragged, this method is a no-op.

        Parameters
        ----------
        pos : QPoint
            The mouse location of the drag start, expressed in the
            global coordinate system.

        """
        press_pos = self._press_pos
        if press_pos is None:
            return
        dock_item = self.parent().widget(self.currentIndex())
        dock_item.titleBarWidget().setVisible(True)
        dock_item.unplug(pos, press_pos)
        self._press_pos = None

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def mousePressEvent(self, event):
        """ Handle the mouse press event for the tab bar.

        If the shift key is pressed, and the click is over a tab, a
        dock drag is initiated.

        """
        #shift = Qt.ShiftModifier
        #if event.button() == Qt.LeftButton and event.modifiers() & shift:
        #    if self.tabAt(event.pos()) != -1:
        #        self._initDrag(event.pos())
        super(QDockTabBar, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for the tab bar.

        If the dock drag is initiated and distances is greater than the
        start drag distances, the item will be undocked.

        """
        #press_pos = self._press_pos
        #if press_pos is None:
        super(QDockTabBar, self).mouseMoveEvent(event)
        #else:
        #    dist = (event.pos() - press_pos).manhattanLength()
        #    if dist > QApplication.startDragDistance():
        #        self._startDrag(event.globalPos())
