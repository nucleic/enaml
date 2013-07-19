#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.qt.QtCore import Qt, QPoint, QSize, QMetaObject, QEvent
from enaml.qt.QtGui import (
    QApplication, QTabBar, QTabWidget, QMouseEvent, QResizeEvent, QStyle,
    QCursor
)

from .event_types import QDockItemEvent, DockTabSelected
from .q_bitmap_button import QBitmapButton
from .xbms import CLOSE_BUTTON


class QDockTabCloseButton(QBitmapButton):
    """ A bitmap button subclass used as a dock tab close button.

    """
    def styleOption(self):
        """ Get a filled style option for the button.

        Returns
        -------
        result : QStyleOption
            A style option initialized for the current button state.

        """
        opt = super(QDockTabCloseButton, self).styleOption()
        parent = self.parent()
        if isinstance(parent, QDockTabBar):
            index = parent.currentIndex()
            if parent.tabButton(index, QTabBar.RightSide) is self:
                opt.state |= QStyle.State_Selected
        return opt


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
        self._has_mouse = False

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def setCloseButtonVisible(self, index, visible):
        """ Set the close button visibility for the given tab index.

        Parameters
        ----------
        index : int
            The index of the tab to set the close button visibility.

        visible : bool
            Whether or not the close button should be visible.

        """
        if index < 0 or index >= self.count():
            return
        button = self.tabButton(index, QTabBar.RightSide)
        if button is not None:
            if button.isVisibleTo(self) != visible:
                # The public QTabBar api does not provide a way to
                # trigger the 'layoutTabs' method of QTabBarPrivate
                # and there are certain operations (such as modifying
                # a tab close button) which need to have that happen.
                # A workaround is to send a dummy resize event.
                button.setVisible(visible)
                if not visible:
                    button.resize(0, 0)
                else:
                    button.resize(button.sizeHint())
                size = self.size()
                event = QResizeEvent(size, size)
                QApplication.sendEvent(self, event)
                self.update()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _onCloseButtonClicked(self):
        """ Handle the 'clicked' signal on the tab close buttons.

        This handler will find the tab index for the clicked button
        and emit the 'tabCloseRequested' signal with that index.

        """
        button = self.sender()
        for index in xrange(self.count()):
            if self.tabButton(index, QTabBar.RightSide) is button:
                self.tabCloseRequested.emit(index)

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def tabInserted(self, index):
        """ Handle a tab insertion in the tab bar.

        This handler will create the close button for the tab and then
        update its visibilty depending on whether or not the dock item
        is closable. This method assumes that this tab bar is parented
        by a QDockTabWidget.

        """
        button = QDockTabCloseButton(self)
        button.setObjectName('docktab-close-button')
        button.setBitmap(CLOSE_BUTTON.toBitmap())
        button.setIconSize(QSize(14, 13))
        button.clicked.connect(self._onCloseButtonClicked)
        self.setTabButton(index, QTabBar.LeftSide, None)
        self.setTabButton(index, QTabBar.RightSide, button)
        visible = self.parent().widget(index).closable()
        self.setCloseButtonVisible(index, visible)

    def mousePressEvent(self, event):
        """ Handle the mouse press event for the tab bar.

        This handler will set the internal '_has_mouse' flag if the
        left mouse button is pressed on a tab.

        """
        super(QDockTabBar, self).mousePressEvent(event)
        self._has_mouse = False
        if event.button() == Qt.LeftButton:
            if self.tabAt(event.pos()) != -1:
                self._has_mouse = True
        elif event.button() == Qt.RightButton:
            index = self.tabAt(event.pos())
            if index != -1:
                button = self.tabButton(index, QTabBar.RightSide)
                if button.geometry().contains(event.pos()):
                    return
                item = self.parent().widget(index).dockItem()
                item.titleBarRightClicked.emit(event.globalPos())
                # Emitting the clicked signal may have caused a popup
                # menu to open, which will have grabbed the mouse. When
                # this happens, the hover leave event is not sent and
                # the tab bar will be stuck in the hovered paint state.
                # Manual checking as 'underMouse' yields False negatives.
                p = self.mapFromGlobal(QCursor.pos())
                if not self.rect().contains(p):
                    QApplication.sendEvent(self, QEvent(QEvent.HoverLeave))

    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for the tab bar.

        This handler will undock the tab if the mouse is held and the
        drag leaves the boundary of the container by the application
        drag distance amount.

        """
        super(QDockTabBar, self).mouseMoveEvent(event)
        if not self._has_mouse:
            return
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
            self._has_mouse = False

    def mouseReleaseEvent(self, event):
        """ Handle the mouse release event for the tab bar.

        This handler will reset the internal '_has_mouse' flag when the
        left mouse button is released.

        """
        super(QDockTabBar, self).mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self._has_mouse = False


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
        self.currentChanged.connect(self._onCurrentChanged)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _onTabCloseRequested(self, index):
        """ Handle the close request for the given tab index.

        """
        # Invoke the close slot later to allow the signal to return.
        container = self.widget(index)
        QMetaObject.invokeMethod(container, 'close', Qt.QueuedConnection)

    def _onCurrentChanged(self, index):
        """ Handle the 'currentChanged' signal for the tab widget.

        """
        # These checks protect against the signal firing during close.
        container = self.widget(index)
        if container is None:
            return
        manager = container.manager()
        if manager is None:
            return
        area = manager.dock_area()
        if area is None:
            return
        if area.dockEventsEnabled():
            event = QDockItemEvent(DockTabSelected, container.objectName())
            QApplication.postEvent(area, event)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def setCloseButtonVisible(self, index, visible):
        """ Set the close button visibility for the given tab index.

        Parameters
        ----------
        index : int
            The index of the tab to set the close button visibility.

        visible : bool
            Whether or not the close button should be visible.

        """
        self.tabBar().setCloseButtonVisible(index, visible)
