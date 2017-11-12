#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from weakref import ref

from enaml.qt import QT_API, PYQT5_API, PYSIDE2_API
from enaml.qt.QtCore import Qt, QPoint, QSize, QMetaObject, QEvent
from enaml.qt.QtGui import (
    QMouseEvent, QResizeEvent, QCursor, QPainter, QPixmap
)
from enaml.qt.QtWidgets import (
    QApplication, QTabBar, QTabWidget, QStyle, QStylePainter
)
if QT_API in PYQT5_API or QT_API in PYSIDE2_API:
    from enaml.qt.QtWidgets import QStyleOptionTab
else:
    from enaml.qt.QtWidgets import QStyleOptionTabV3 as QStyleOptionTab

from .event_types import QDockItemEvent, DockTabSelected
from .q_bitmap_button import QBitmapButton
from .utils import repolish
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


class _TabData(object):
    """ A private class which holds data about a tab in a tab bar.

    """
    __slots__ = ('ref', 'normal', 'selected', 'alerted')

    def __init__(self, container):
        self.ref = ref(container)
        self.normal = None
        self.selected = None
        self.alerted = False

    @property
    def container(self):
        return self.ref()


class QDockTabBar(QTabBar):
    """ A custom QTabBar that manages safely undocking a tab.

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
        self.tabMoved.connect(self._onTabMoved)
        self._has_alerts = False
        self._has_mouse = False
        self._tab_data = []

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
    def _onTabMoved(self, from_index, to_index):
        """ A handler for the 'tabMoved' signal.

        This handler synchronizes the internal tab data structures for
        the new positions of the tabs.

        """
        data = self._tab_data.pop(from_index)
        self._tab_data.insert(to_index, data)

    def _onCloseButtonClicked(self):
        """ Handle the 'clicked' signal on the tab close buttons.

        This handler will find the tab index for the clicked button
        and emit the 'tabCloseRequested' signal with that index.

        """
        button = self.sender()
        for index in range(self.count()):
            if self.tabButton(index, QTabBar.RightSide) is button:
                self.tabCloseRequested.emit(index)

    def _onAlerted(self, level):
        """ A signal handler for the 'alerted' signal on a container.

        This handler will re-snap the pixmaps for the alerted tab
        and trigger a repaint of the tab bar.

        """
        container = self.sender()
        index = self.parent().indexOf(container)
        if index != -1:
            if level:
                self._snapAlertPixmaps(index, level)
            else:
                self._clearAlertPixmaps(index)
            self.update()

    def _snapAlertPixmaps(self, index, level):
        """ Snap the alert pixmaps for the specified tab.

        Parameters
        ----------
        index : int
            The index of the tab of interest.

        level : unicode
            The alert level for which to snap the pixmaps.

        """
        # Force an internal update of the stylesheet rules
        self.setProperty(u'alert', level)
        repolish(self)

        # Setup the style option for the control
        opt = QStyleOptionTab()
        self.initStyleOption(opt, index)
        opt.rect.moveTo(0, 0)

        # Snap the normal pixmap
        opt.state &= ~QStyle.State_Selected
        normal = QPixmap(opt.rect.size())
        normal.fill(Qt.transparent)
        painter = QStylePainter(normal, self)
        painter.initFrom(self)
        painter.drawControl(QStyle.CE_TabBarTab, opt)

        # Snap the selected pixmap
        opt.state |= QStyle.State_Selected
        selected = QPixmap(opt.rect.size())
        selected.fill(Qt.transparent)
        painter = QStylePainter(selected, self)
        painter.initFrom(self)
        painter.drawControl(QStyle.CE_TabBarTab, opt)

        # Reset the internal stylesheet style
        self.setProperty(u'alert', None)
        repolish(self)

        # Update the internal tab data
        data = self._tab_data[index]
        data.normal = normal
        data.selected = selected
        data.alerted = True

        # Flip the alert flag so the pixmaps are painted
        self._has_alerts = True

    def _clearAlertPixmaps(self, index):
        """ Clear the alert pixmaps for the specified tab.

        Parameters
        ----------
        index : int
            The index of the tab of interest.

        """
        data = self._tab_data[index]
        data.normal = None
        data.selected = None
        data.alerted = False

        # Turn off alert painting if there are no more alerts
        self._has_alerts = any(d.alerted for d in self._tab_data)

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def tabInserted(self, index):
        """ Handle a tab insertion in the tab bar.

        This handler will create the close button for the tab and then
        update its visibilty depending on whether or not the dock item
        is closable. It will also build the internal tab data structure
        for the new tab. This method assumes that this tab bar is
        parented by a QDockTabWidget.

        """
        button = QDockTabCloseButton(self)
        button.setObjectName('docktab-close-button')
        button.setBitmap(CLOSE_BUTTON.toBitmap())
        button.setIconSize(QSize(14, 13))
        button.clicked.connect(self._onCloseButtonClicked)
        self.setTabButton(index, QTabBar.LeftSide, None)
        self.setTabButton(index, QTabBar.RightSide, button)
        container = self.parent().widget(index)
        container.alerted.connect(self._onAlerted)
        self.setCloseButtonVisible(index, container.closable())
        self._tab_data.insert(index, _TabData(container))

    def tabRemoved(self, index):
        """ Handle a tab removal from the tab bar.

        This will remove the internal tab data structure and disconnect
        the relevant signals.

        """
        data = self._tab_data.pop(index)
        container = data.container
        if container is not None:
            container.alerted.disconnect(self._onAlerted)

    def mousePressEvent(self, event):
        """ Handle the mouse press event for the tab bar.

        This handler will set the internal '_has_mouse' flag if the
        left mouse button is pressed on a tab.

        """
        super(QDockTabBar, self).mousePressEvent(event)
        self._has_mouse = False
        if event.button() == Qt.LeftButton:
            index = self.tabAt(event.pos())
            if index != -1:
                self._has_mouse = True
                data = self._tab_data[index]
                container = data.container
                if container is not None:
                    # likey a no-op, but just in case
                    container.dockItem().clearAlert()
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

    def paintEvent(self, event):
        """ A custom paint event for the tab bar.

        This paint event will blit the pixmaps for the alerted tabs as
        necessary, after the superclass paint event handler is run.

        """
        super(QDockTabBar, self).paintEvent(event)
        if self._has_alerts:
            painter = QPainter(self)
            current = self.currentIndex()
            for index, data in enumerate(self._tab_data):
                if data.alerted:
                    rect = self.tabRect(index)
                    pm = data.selected if index == current else data.normal
                    painter.drawPixmap(rect, pm)


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
