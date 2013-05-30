#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QMargins, QPoint, QRect, QEvent
from PyQt4.QtGui import QApplication, QLayout, QIcon

from atom.api import Typed, Bool

from .q_dock_area import QDockArea
from .q_dock_frame import QDockFrame
from .q_dock_frame_layout import QDockFrameLayout
from .q_dock_tab_widget import QDockTabWidget
from .utils import repolish


class QDockContainerLayout(QDockFrameLayout):
    """ A QDockFrameLayout subclass which works with a QDockContainer.

    """
    def invalidate(self):
        """ Invalidate the cached layout data.

        """
        super(QDockContainerLayout, self).invalidate()
        widget = self.getWidget()
        if widget is not None:
            self.parentWidget().setSizePolicy(widget.sizePolicy())


def _computePressPos(container, coeff):
    """ Compute the press position for a title bar.

    Parameters
    ----------
    container : QDockContainer
        The dock container which owns the title bar of interest.

    coeff : float
        A floating point value between 0.0 and 1.0 which is the
        proportional x-offset of the mouse press in the title bar.

    """
    margins = container.layout().contentsMargins()
    button_width = 50  # general approximation
    max_x = container.width() - margins.right() - button_width
    test_x = int(coeff * container.width())
    new_x = max(margins.left() + 5, min(test_x, max_x))
    title_bar = container.dockItem().titleBarWidget()
    title_height = title_bar.height() / 2
    mid_title = title_bar.mapTo(container, QPoint(0, title_height))
    return QPoint(new_x, mid_title.y())


class QDockContainer(QDockFrame):
    """ A QDockFrame which holds a QDockItem instance.

    A QDockContainer has a dynamic boolean property 'floating' which
    can be used to apply custom stylesheet styling when the container
    is a floating top level window versus docked in a dock area.

    """
    class FrameState(QDockFrame.FrameState):
        """ A private class for managing container drag state.

        """
        #: The original title bar press position.
        press_pos = Typed(QPoint)

        #: Whether or not the dock item is being dragged.
        dragging = Bool(False)

        #: Whether the dock item is maximized in the dock area.
        item_is_maximized = Bool(False)

    def __init__(self, manager, parent=None):
        """ Initialize a QDockContainer.

        Parameters
        ----------
        manager : DockManager
            The manager which owns the container.

        parent : QWidget or None
            The parent of the QDockContainer.

        """
        super(QDockContainer, self).__init__(manager, parent)
        layout = QDockContainerLayout()
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)
        self.setProperty('floating', False)
        self._dock_item = None

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def titleBarGeometry(self):
        """ Get the geometry rect for the title bar.

        Returns
        -------
        result : QRect
            The geometry rect for the title bar, expressed in frame
            coordinates. An invalid rect is returned if title bar
            should not be active.

        """
        title_bar = self.dockItem().titleBarWidget()
        if title_bar.isHidden():
            return QRect()
        pt = title_bar.mapTo(self, QPoint(0, 0))
        return QRect(pt, title_bar.size())

    def resizeMargins(self):
        """ Get the margins to use for resizing the container.

        Returns
        -------
        result : QMargins
            The margins to use for container resizing when the container
            is a top-level window.

        """
        if self.isMaximized():
            return QMargins()
        return self.layout().contentsMargins()

    def showMaximized(self):
        """ Handle the show maximized request for the dock container.

        """
        def update_buttons(bar, link=False):
            buttons = bar.buttons()
            buttons |= bar.RestoreButton
            buttons &= ~bar.MaximizeButton
            if link:
                buttons &= ~bar.LinkButton
            bar.setButtons(buttons)
        if self.isWindow():
            super(QDockContainer, self).showMaximized()
            self.setLinked(False)
            update_buttons(self.dockItem().titleBarWidget(), link=True)
        else:
            area = self.parentDockArea()
            if area is not None:
                item = self.dockItem()
                update_buttons(item.titleBarWidget())
                area.setMaximizedWidget(item)
                self.frame_state.item_is_maximized = True
                item.installEventFilter(self)

    def showNormal(self):
        """ Handle the show normal request for the dock container.

        """
        def update_buttons(bar, link=False):
            buttons = bar.buttons()
            buttons |= bar.MaximizeButton
            buttons &= ~bar.RestoreButton
            if link:
                buttons |= bar.LinkButton
            bar.setButtons(buttons)
        if self.isWindow():
            super(QDockContainer, self).showNormal()
            self.setLinked(False)
            update_buttons(self.dockItem().titleBarWidget(), link=True)
        elif self.frame_state.item_is_maximized:
            item = self.dockItem()
            update_buttons(item.titleBarWidget())
            self.layout().setWidget(item)
            self.item_is_maximized = False
            item.removeEventFilter(self)

    #--------------------------------------------------------------------------
    # Framework API
    #--------------------------------------------------------------------------
    def dockItem(self):
        """ Get the dock item installed on the container.

        Returns
        -------
        result : QDockItem or None
            The dock item installed in the container, or None.

        """
        return self._dock_item

    def setDockItem(self, dock_item):
        """ Set the dock item for the container.

        Parameters
        ----------
        dock_item : QDockItem
            The dock item to use in the container.

        """
        layout = self.layout()
        old = layout.getWidget()
        if old is not None:
            old.maximizeButtonClicked.disconnect(self.showMaximized)
            old.restoreButtonClicked.disconnect(self.showNormal)
            old.closeButtonClicked.disconnect(self.close)
            old.linkButtonToggled.disconnect(self.linkButtonToggled)
        if dock_item is not None:
            dock_item.maximizeButtonClicked.connect(self.showMaximized)
            dock_item.restoreButtonClicked.connect(self.showNormal)
            dock_item.closeButtonClicked.connect(self.close)
            dock_item.linkButtonToggled.connect(self.linkButtonToggled)
        layout.setWidget(dock_item)
        self._dock_item = dock_item

    def title(self):
        """ Get the title for the container.

        This proxies the call to the underlying dock item.

        """
        item = self.dockItem()
        if item is not None:
            return item.title()
        return u''

    def icon(self):
        """ Get the icon for the container.

        This proxies the call to the underlying dock item.

        """
        item = self.dockItem()
        if item is not None:
            return item.icon()
        return QIcon()

    def closable(self):
        """ Get whether or not the container is closable.

        This proxies the call to the underlying dock item.

        """
        item = self.dockItem()
        if item is not None:
            return item.closable()
        return True

    def isLinked(self):
        """ Get whether or not the container is linked.

        This proxies the call to the underlying dock item.

        """
        item = self.dockItem()
        if item is not None:
            return item.isLinked()
        return False

    def setLinked(self, linked):
        """ Set whether or not the container should be linked.

        This proxies the call to the underlying dock item.

        """
        item = self.dockItem()
        if item is not None:
            item.setLinked(linked)

    def showTitleBar(self):
        """ Show the title bar for the container.

        This proxies the call to the underlying dock item.

        """
        item = self.dockItem()
        if item is not None:
            item.titleBarWidget().show()

    def hideTitleBar(self):
        """ Hide the title bar for the container.

        This proxies the call to the underlying dock item.

        """
        item = self.dockItem()
        if item is not None:
            item.titleBarWidget().hide()

    def showLinkButton(self):
        """ Show the link button on the title bar.

        """
        item = self.dockItem()
        if item is not None:
            bar = item.titleBarWidget()
            bar.setButtons(bar.buttons() | bar.LinkButton)

    def hideLinkButton(self):
        """ Show the link button on the title bar.

        """
        item = self.dockItem()
        if item is not None:
            bar = item.titleBarWidget()
            bar.setButtons(bar.buttons() & ~bar.LinkButton)

    def reset(self):
        """ Reset the container to the initial pre-docked state.

        """
        state = self.frame_state
        state.dragging = False
        state.press_pos = None
        self.showNormal()
        self.unfloat()
        self.hideLinkButton()
        self.setLinked(False)
        self.showTitleBar()
        self.setAttribute(Qt.WA_WState_ExplicitShowHide, False)
        self.setAttribute(Qt.WA_WState_Hidden, False)

    def float(self):
        """ Set the window state to be a toplevel floating window.

        """
        self.hide()
        self.setAttribute(Qt.WA_Hover, True)
        flags = Qt.Tool | Qt.FramelessWindowHint
        self.setParent(self.manager().dock_area(), flags)
        self.layout().setContentsMargins(QMargins(5, 5, 5, 5))
        self.setProperty('floating', True)
        self.setLinked(False)
        self.showLinkButton()
        self.manager()._proximity_handler.addFrame(self)
        repolish(self)

    def unfloat(self):
        """ Set the window state to be non-floating window.

        """
        self.hide()
        self.setAttribute(Qt.WA_Hover, False)
        flags = Qt.Widget
        self.setParent(self.manager().dock_area(), flags)
        self.layout().setContentsMargins(QMargins(0, 0, 0, 0))
        self.unsetCursor()
        self.setProperty('floating', False)
        self.setLinked(False)
        self.hideLinkButton()
        self.manager()._proximity_handler.removeFrame(self)
        repolish(self)

    def parentDockArea(self):
        """ Get the parent dock area of the container.

        Returns
        -------
        result : QDockArea or None
            The nearest ancestor which is an instance of QDockArea, or
            None if no such ancestor exists.

        """
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, QDockArea):
                return parent
            parent = parent.parent()

    def parentDockTabWidget(self):
        """ Get the parent dock area of the container.

        Returns
        -------
        result : QDockTabWidget or None
            The nearest ancestor which is an instance of QDockTabWidget,
            or None if no such ancestor exists.

        """
        parent = self.parent()
        while parent is not None:
            if isinstance(parent, QDockTabWidget):
                return parent
            parent = parent.parent()

    def unplug(self):
        """ Unplug the container from its containing dock area.

        This method is invoked by the framework when appropriate. It
        should not need to be called by user code.

        Returns
        -------
        result : bool
            True if the container was unplugged, False otherwise.

        """
        dock_area = self.parentDockArea()
        if dock_area is None:
            return False
        # avoid a circular import
        from .layout_handling import unplug_container
        return unplug_container(dock_area, self)

    def untab(self, pos):
        """ Unplug the container from a tab control.

        This method is invoked by the QDockTabBar when the container
        should be torn out. It synthesizes the appropriate internal
        state so that the item can continue to be dock dragged. This
        method should not be called by user code.

        Parameters
        ----------
        pos : QPoint
            The global mouse position.

        Returns
        -------
        result : bool
            True on success, False otherwise.

        """
        if not self.unplug():
            return
        state = self.frame_state
        state.mouse_title = True
        state.dragging = True
        self.float()
        self.raiseFrame()
        title_bar = self.dockItem().titleBarWidget()
        title_pos = QPoint(title_bar.width() / 2, title_bar.height() / 2)
        margins = self.layout().contentsMargins()
        offset = QPoint(margins.left(), margins.top())
        state.press_pos = title_bar.mapTo(self, title_pos) + offset
        self.move(pos - state.press_pos)
        self.show()
        self.grabMouse()
        self.activateWindow()
        self.raise_()

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def eventFilter(self, obj, event):
        """ Filter the events for the dock item.

        This filter will proxy out the mouse events for the dock item.
        This event filter will only be activated when the dock item is
        set to maximzed mode.

        """
        if obj is not self._dock_item:
            return False
        if event.type() == QEvent.MouseButtonPress:
            return self.filteredMousePressEvent(event)
        elif event.type() == QEvent.MouseMove:
            return self.filteredMouseMoveEvent(event)
        elif event.type() == QEvent.MouseButtonRelease:
            return self.filteredMouseReleaseEvent(event)
        return False

    def filteredMousePressEvent(self, event):
        """ Handle the filtered mouse press event for the dock item.

        """
        bar = self.dockItem().titleBarWidget()
        if bar.isVisible() and bar.geometry().contains(event.pos()):
            self.frame_state.mouse_title = True
            return self.titleBarMousePressEvent(event)
        return False

    def filteredMouseMoveEvent(self, event):
        """ Handle the filtered mouse move event for the dock item.

        """
        if self.frame_state.mouse_title:
            return self.titleBarMouseMoveEvent(event)
        return False

    def filteredMouseReleaseEvent(self, event):
        """ Handle the filtered mouse release event for the dock item.

        """
        if self.frame_state.mouse_title:
            self.frame_state.mouse_title = False
            return self.titleBarMouseReleaseEvent(event)
        return False

    def closeEvent(self, event):
        """ Handle the close event for the dock container.

        """
        self.manager().close_container(self, event)

    def titleBarMousePressEvent(self, event):
        """ Handle a mouse press event on the title bar.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        if event.button() == Qt.LeftButton:
            state = self.frame_state
            if state.press_pos is None:
                state.press_pos = event.pos()
                return True
        return False

    def titleBarMouseMoveEvent(self, event):
        """ Handle a mouse move event on the title bar.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        state = self.frame_state
        if state.press_pos is None:
            return False

        # If dragging and floating, move the container's position and
        # notify the manager of that the container was mouse moved. If
        # the container is maximized, it is first restored before.
        global_pos = event.globalPos()
        if state.dragging:
            if self.isWindow():
                target_pos = global_pos - state.press_pos
                self.manager().drag_move_frame(self, target_pos, global_pos)
            return True

        # Ensure the drag has crossed the app drag threshold.
        dist = (event.pos() - state.press_pos).manhattanLength()
        if dist <= QApplication.startDragDistance():
            return True

        # If the container is already floating, ensure that it is shown
        # normal size. The next move event will move the window.
        state.dragging = True
        if self.isWindow():
            if self.isMaximized():
                coeff = state.press_pos.x() / float(self.width())
                self.showNormal()
                state.press_pos = _computePressPos(self, coeff)
            return True

        # Restore a maximized dock item before unplugging.
        if state.item_is_maximized:
            bar = self.dockItem().titleBarWidget()
            coeff = state.press_pos.x() / float(bar.width())
            self.showNormal()
            state.press_pos = _computePressPos(self, coeff)

        # Unplug the container from the layout before floating so
        # that layout widgets can clean themselves up when empty.
        if not self.unplug():
            return False

        # Make the container a toplevel frame, update it's Z-order,
        # and grab the mouse to continue processing drag events.
        self.float()
        self.raiseFrame()
        margins = self.layout().contentsMargins()
        state.press_pos += QPoint(0, margins.top())
        self.move(global_pos - state.press_pos)
        self.show()
        self.grabMouse()
        self.activateWindow()
        self.raise_()
        return True

    def titleBarMouseReleaseEvent(self, event):
        """ Handle a mouse release event on the title bar.

        Returns
        -------
        result : bool
            True if the event is handled, False otherwise.

        """
        if event.button() == Qt.LeftButton:
            state = self.frame_state
            if state.press_pos is not None:
                self.releaseMouse()
                if self.isWindow():
                    self.manager().drag_release_frame(self, event.globalPos())
                state.dragging = False
                state.press_pos = None
                return True
        return False
