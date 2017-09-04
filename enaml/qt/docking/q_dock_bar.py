#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import IntEnum

from enaml.qt.QtCore import (
    Qt, QSize, QPoint, QRect, QMargins, QEvent, QObject, QPropertyAnimation,
    Signal
)
from enaml.qt.QtWidgets import (
    QBoxLayout, QSizePolicy, QFrame, QPushButton, QStyle, QStyleOption,
    QStylePainter, QStyleOptionButton, QApplication, QVBoxLayout, QHBoxLayout,
    QLayout
)

from .event_types import (
    QDockItemEvent, DockItemExtended, DockItemRetracted,
    DockAreaContentsChanged
)
from .utils import repolish


class QDockBar(QFrame):
    """ A QFrame which acts as a container for QDockBarButtons.

    """
    class Position(IntEnum):
        """ An int enum defining the position for a dock bar.

        """
        #: The north pin position.
        North = 0

        #: The east pin position.
        East = 1

        #: The south pin position.
        South = 2

        #: The west pin position.
        West = 3

    #: Proxy the Position values as if it were an anonymous enum.
    North = Position.North
    East = Position.East
    South = Position.South
    West = Position.West

    #: A mapping from Position to layout direction.
    LayoutPositions = [
        QBoxLayout.LeftToRight,  # PinPosition.North
        QBoxLayout.TopToBottom,  # PinPosition.East
        QBoxLayout.LeftToRight,  # PinPosition.South
        QBoxLayout.TopToBottom,  # PinPosition.West
    ]

    def __init__(self, parent=None, position=Position.North):
        """ Initialize a QDockBar.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget of the dock bar.

        position : QDockBar.Position, optional
            The position enum value for the dock bar. This dictates the
            layout and orientation of the contained dock buttons. The
            default position is QDockBar.North.

        """
        super(QDockBar, self).__init__(parent)
        assert isinstance(position, QDockBar.Position)
        self.setProperty('position', int(position))
        layout = QBoxLayout(self.LayoutPositions[position])
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.addStretch(1)
        self.setLayout(layout)
        self.updateSpacing()

    #--------------------------------------------------------------------------
    # Protected API
    #--------------------------------------------------------------------------
    def event(self, event):
        """ A generic event handler for the dock bar.

        """
        if event.type() == QEvent.StyleChange:
            self.updateSpacing()
        return super(QDockBar, self).event(event)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def updateSpacing(self):
        """ Update the layout spacing for the dock bar.

        This method will extract spacing value defined in the style
        sheet for the dock area and apply it to the spacing between
        the dock bars and the central widget.

        """
        opt = QStyleOption()
        opt.initFrom(self)
        style = self.style()
        # hack to get the style sheet 'spacing' property.
        spacing = style.pixelMetric(QStyle.PM_ToolBarItemSpacing, opt, self)
        self.layout().setSpacing(spacing)

    def position(self):
        """ Get the position of the dock bar.

        Returns
        -------
        result : QDockBar.Position
            The position enum value for the dock bar.

        """
        return QDockBar.Position(self.property('position'))

    def isEmpty(self):
        """ Get whether or not the dock bar is empty.

        Returns
        -------
        result : bool
            True if the dock bar has dock buttons, False otherwise.

        """
        layout = self.layout()
        for index in range(layout.count()):
            item = layout.itemAt(index)
            if item.widget() is not None:
                return False
        return True

    def addButton(self, button):
        """ Add a dock button to the dock bar.

        Parameters
        ----------
        button : QDockBarButton
            The dock button to add to the dock bar.

        """
        return self.insertButton(-1, button)

    def insertButton(self, index, button):
        """ Insert a dock button into the dock bar.

        Parameters
        ----------
        index : int
            The index at which to insert the button.

        button : QDockBarButton
            The dock button to insert into the dock bar.

        """
        assert isinstance(button, QDockBarButton)
        layout = self.layout()
        if index < 0:
            index = layout.count()
        if index == layout.count():
            index = max(0, index - 1)
        layout.insertWidget(index, button)


class QDockBarButton(QPushButton):
    """ A custom QPushButton for use in a QDockBar.

    """
    def __init__(self, parent=None):
        """ Initialize a QDockBarButton.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget of the dock bar button.

        """
        super(QDockBarButton, self).__init__(parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setCheckable(True)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def position(self):
        """ Get the position for the dock bar button.

        Returns
        -------
        result : QDockBar.Position
            The position of the dock bar in which this button resides.

        """
        parent = self.parent()
        if isinstance(parent, QDockBar):
            return parent.position()
        return QDockBar.North

    def onAlerted(self, level):
        """ A slot which can be connected to an 'alerted' signal.

        """
        self.setProperty(u'alert', level or None)
        repolish(self)

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def sizeHint(self):
        """ Get the size hint for the button.

        """
        hint = super(QDockBarButton, self).sizeHint()
        p = self.position()
        if p == QDockBar.East or p == QDockBar.West:
            hint.transpose()
        return hint

    def paintEvent(self, event):
        """ Handle the paint event for the button.

        """
        painter = QStylePainter(self)
        opt = QStyleOptionButton()
        self.initStyleOption(opt)
        opt.state &= ~QStyle.State_HasFocus  # don't draw the focus rect
        p = self.position()
        if p == QDockBar.East:
            size = opt.rect.size()
            size.transpose()
            opt.rect.setSize(size)
            painter.rotate(90)
            painter.translate(0, -size.height())
        elif p == QDockBar.West:
            size = opt.rect.size()
            size.transpose()
            opt.rect.setSize(size)
            painter.rotate(-90)
            painter.translate(-size.width(), 0)
        painter.drawControl(QStyle.CE_PushButton, opt)


class QDockBarItemHandle(QFrame):
    """ A frame which provides a resize border for a QDockBarItem.

    """
    #: A signal emitted when the handle is moved. The payload is a
    #: QPoint which represents the delta drag distance.
    handleMoved = Signal(QPoint)

    def __init__(self, parent=None):
        """ Initialize a QDockBarItemHandle.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget of the handle.

        """
        super(QDockBarItemHandle, self).__init__(parent)
        policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setSizePolicy(policy)
        self._press_pos = QPoint()
        self._size_hint = QSize(5, 5)

    def sizeHint(self):
        """ Get the size hint for the widget.

        """
        return self._size_hint

    def mousePressEvent(self, event):
        """ Handle the mouse press event for the widget.

        """
        event.ignore()
        if event.button() == Qt.LeftButton:
            self._press_pos = event.pos()
            event.accept()

    def mouseReleaseEvent(self, event):
        """ Handle the mouse release event for the widget.

        """
        event.ignore()
        if event.button() == Qt.LeftButton:
            self._press_pos = QPoint()
            event.accept()

    def mouseMoveEvent(self, event):
        """ Handle the mouse move event for the widget.

        """
        event.ignore()
        if not self._press_pos.isNull():
            self.handleMoved.emit(event.pos() - self._press_pos)
            event.accept()


class QDockBarItem(QFrame):
    """ A QFrame which holds an item for a QDockBar.

    This class serves as a container which holds the dock widget of
    interest and a resize handle which permits resizing of the item.

    """
    def __init__(self, parent=None, position=QDockBar.North):
        """ Initialize a QDockBarItem.

        Parameters
        ----------
        parent : QWidget, optional
            The parent of the dock bar item.

        position : QDockBar.Position, optional
            The position of the dock bar for the item.

        """
        super(QDockBarItem, self).__init__(parent)
        assert isinstance(position, QDockBar.Position)
        self.setProperty('position', int(position))
        self._user_size = QSize()
        self._animation = None
        self._widget = None
        handle = QDockBarItemHandle()
        handle.handleMoved.connect(self._onHandleMoved)
        if position == QDockBar.North or position == QDockBar.South:
            layout = QVBoxLayout()
            handle.setCursor(Qt.SizeVerCursor)
        else:
            layout = QHBoxLayout()
            handle.setCursor(Qt.SizeHorCursor)
        layout.addWidget(handle, 0)
        layout.setSpacing(0)
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        self.setLayout(layout)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def _onHandleMoved(self, delta):
        """ Handle the 'handleMoved' signal on the item handle.

        This handler resizes the item by the delta and then updates
        the internal user size. The resize is bounded by the limits
        of the widget and the parent dock area size.

        Resizing is disabled if an animation is running.

        """
        animation = self._animation
        if animation and animation.state() == animation.Running:
            return
        p = self.position()
        if p == QDockBar.North:
            delta = QSize(0, delta.y())
        elif p == QDockBar.East:
            delta = QSize(-delta.x(), 0)
        elif p == QDockBar.South:
            delta = QSize(0, -delta.y())
        else:
            delta = QSize(delta.x(), 0)
        user_size = self.size() + delta
        user_size = user_size.expandedTo(self.minimumSize())
        parent = self.parent()
        if parent is not None:
            user_size = user_size.boundedTo(parent.size())
        self._user_size = user_size
        if p == QDockBar.East or p == QDockBar.South:
            d = user_size - self.size()
            p = self.pos() - QPoint(d.width(), d.height())
            self.setGeometry(QRect(p, user_size))
        else:
            self.resize(user_size)

    def widget(self):
        """ Get the primary widget for the dock bar item.

        Returns
        -------
        result : QWidget or None
            The primary dock widget installed on the item.

        """
        return self._widget

    def setWidget(self, widget):
        """ Set the primary widget for the dock bar item.

        Parameters
        ----------
        widget : QWidget or None
            The primary dock widget to install on the item. Any old
            widget will be unparented, but not destroyed.

        """
        old = self._widget
        if old is not None:
            old.setParent(None)
        self._widget = widget
        if widget is not None:
            index = (0, 1, 1, 0)[self.position()]
            layout = self.layout()
            layout.insertWidget(index, widget, 1)

    def position(self):
        """ Get the position of the dock bar item.

        Returns
        -------
        result : QDockBar.Position
            The position of the dock bar item.

        """
        return QDockBar.Position(self.property('position'))

    def animation(self):
        """ Get the animation object associated with the item.

        Returns
        -------
        result : QPropertyAnimation or None
            The property animation installed on the item.

        """
        return self._animation

    def setAnimation(self, animation):
        """ Set the animation object associated with the item.

        Parameters
        ----------
        animation : QPropertyAnimation or None
            The animation object to associate with this item.

        """
        self._animation = animation

    def sizeHint(self):
        """ Get the size hint for the item.

        """
        user = self._user_size
        if user.isValid():
            return user
        return super(QDockBarItem, self).sizeHint()


class QDockBarManager(QObject):
    """ An object which manages the dock bars for a QDockArea.

    """
    def __init__(self, parent):
        """ Initialize a QDockBarManager.

        Parameters
        ----------
        parent : QDockArea
            The parent dock area on which this manager should operate.

        """
        super(QDockBarManager, self).__init__(parent)
        self._dock_bars = [None, None, None, None]
        self._active_items = {}
        self._widgets = {}

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: A static mapping of dock position to grid layout coordinates.
    _layout_coords = [
        (0, 1, 1, 1),  # QDockBar.North
        (1, 2, 1, 1),  # QDockBar.East
        (2, 1, 1, 1),  # QDockBar.South
        (1, 0, 1, 1),  # QDockBar.West
    ]

    @staticmethod
    def _prepareAnimation(item):
        """ Prepare the animation object for a dock container.

        Parameters
        ----------
        item : QDockBarItem
            The item which should have an animation prepared.

        """
        animation = item.animation()
        if animation is not None:
            animation.stop()
            animation.finished.disconnect()
        else:
            animation = QPropertyAnimation(item, b'geometry')
            item.setAnimation(animation)
        return animation

    def _getDockBar(self, position, create=True):
        """ Get the dock bar for a given position.

        Parameters
        ----------
        position : QDockBar.Position
            The dock position of interest.

        create : bool, optional
            Whether to force create the bar if one does not exist. The
            default is True.

        Returns
        -------
        result : QDockBar or None
            The dock bar instance for the given position. If no dock
            bar exists, and `create` is False None will be returned.

        """
        dock_bar = self._dock_bars[position]
        if dock_bar is not None:
            return dock_bar
        if create:
            dock_bar = self._dock_bars[position] = QDockBar(position=position)
            coords = self._layout_coords[position]
            layout = self.parent().primaryPane().layout()
            layout.addWidget(dock_bar, *coords)
            return dock_bar

    def _trackForResize(self, item, slide_out):
        """ Track the given container for resize events on the pane.

        Parameters
        ----------
        item : QDockBarItem
            The dock bar item which should track pane resizes.

        slide_out : bool
            Whether the item is in the slide out position.

        """
        active = self._active_items
        install = len(active) == 0
        active[item] = slide_out
        if install:
            self.parent().centralPane().installEventFilter(self)

    def _untrackForResize(self, item):
        """ Untrack the given item for resize events on the pane.

        Parameters
        ----------
        item : QDockBarItem
            The dock bar item which should untrack pane resizes.

        """
        active = self._active_items
        active.pop(item, None)
        if len(active) == 0:
            self.parent().centralPane().removeEventFilter(self)

    def _slideOut(self, item):
        """ Animate the slide out for the given item.

        Parameters
        ----------
        item : QDockBarItem
            The dock bar item which should be slid out.

        """
        self._trackForResize(item, True)
        animation = self._prepareAnimation(item)
        animation.finished.connect(self._onSlideOutFinished)
        start_geo, end_geo = self._animationGeo(item)
        if item.isVisible():
            start_geo = item.geometry()
        else:
            item.setGeometry(start_geo)
            item.show()
        item.raise_()
        animation.setStartValue(start_geo)
        animation.setEndValue(end_geo)
        animation.start()

    def _slideIn(self, item):
        """ Animate the slide in for the given item.

        Parameters
        ----------
        item : QDockBarItem
            The dock bar item which should be slide in.

        """
        if not item.isVisible():
            return
        self._trackForResize(item, False)
        animation = self._prepareAnimation(item)
        animation.finished.connect(self._onSlideInFinished)
        start_geo = item.geometry()
        end_geo, ignored = self._animationGeo(item)
        animation.setStartValue(start_geo)
        animation.setEndValue(end_geo)
        animation.start()

    def _animationGeo(self, item):
        """ Get the animation geometry for the given item.

        Parameters
        ----------
        item : QDockBarItem
            The dock bar item to be animated.

        Returns
        -------
        result : tuple
            A 2-tuple of QRect objects representing the start and end
            geometries for the animation assuming a slide out effect.

        """
        pane = self.parent().centralPane()
        hint = item.sizeHint().boundedTo(pane.size())
        position = item.position()
        if position == QDockBar.North:
            start_pos = QPoint(0, -hint.height())
            end_pos = QPoint(0, 0)
            size = QSize(pane.width(), hint.height())
        elif position == QDockBar.East:
            start_pos = QPoint(pane.width(), 0)
            end_pos = QPoint(pane.width() - hint.width(), 0)
            size = QSize(hint.width(), pane.height())
        elif position == QDockBar.South:
            start_pos = QPoint(0, pane.height())
            end_pos = QPoint(0, pane.height() - hint.height())
            size = QSize(pane.width(), hint.height())
        else:
            start_pos = QPoint(-hint.width(), 0)
            end_pos = QPoint(0, 0)
            size = QSize(hint.width(), pane.height())
        start_geo = QRect(start_pos, size)
        end_geo = QRect(end_pos, size)
        return start_geo, end_geo

    def _toggleCheckedButtons(self, allowed):
        """ Toggle off the checked buttons.

        Parameters
        ----------
        allowed : QDockBarButton
            The dock button which should be allowed to remain checked.

        """
        for key in self._widgets:
            if isinstance(key, QDockBarButton):
                if key is not allowed and key.isChecked():
                    key.setChecked(False)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def _onButtonToggled(self, checked):
        """ Handle the 'toggled' signal from a QDockBarButton.

        """
        button = self.sender()
        if checked:
            self._toggleCheckedButtons(button)
        item = self._widgets.get(button)
        if item is not None:
            if checked:
                self._slideOut(item)
            else:
                self._slideIn(item)

    def _onSlideOutFinished(self):
        """ Handle the 'finished' signal from a slide out animation.

        """
        item = self.sender().targetObject()
        item.setAnimation(None)
        container = item.widget()
        area = container.manager().dock_area()
        if area.dockEventsEnabled():
            event = QDockItemEvent(DockItemExtended, container.objectName())
            QApplication.postEvent(area, event)

    def _onSlideInFinished(self):
        """ Handle the 'finished' signal from a slide in animation.

        """
        item = self.sender().targetObject()
        item.setAnimation(None)
        item.hide()
        self._untrackForResize(item)
        container = item.widget()
        area = container.manager().dock_area()
        if area.dockEventsEnabled():
            event = QDockItemEvent(DockItemRetracted, container.objectName())
            QApplication.postEvent(area, event)

    def _onButtonPressed(self):
        """ Handle the 'pressed' signal from a dock bar button.

        """
        button = self.sender()
        container = self._widgets[button].widget()
        container.dockItem().clearAlert()  # likey a no-op, but just in case

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def addContainer(self, container, position, index=-1):
        """ Add a container to the specified dock bar.

        Parameters
        ----------
        container : QDockContainer
            The container to add to the dock bar. It should already be
            unplugged from a layout or other dock manager before being
            added to this manager.

        position : QDockBar.Position
            The position of the dock bar to which the container should
            be added.

        index : int, optional
            The index at which to insert the item. The default is -1
            and will append the item to the dock bar.

        """
        assert isinstance(position, QDockBar.Position)
        self.removeContainer(container)
        container.setPinned(True, quiet=True)
        container.frame_state.in_dock_bar = True

        button = QDockBarButton()
        button.setText(container.title())
        button.setIcon(container.icon())
        button.toggled.connect(self._onButtonToggled)
        button.pressed.connect(self._onButtonPressed)
        container.alerted.connect(button.onAlerted)

        dock_bar = self._getDockBar(position)
        dock_bar.insertButton(index, button)

        item = QDockBarItem(self.parent().centralPane(), position=position)
        item.hide()
        item.setWidget(container)
        container.show()

        self._widgets[button] = item
        self._widgets[container] = button

        event = QEvent(DockAreaContentsChanged)
        QApplication.sendEvent(self.parent(), event)

    def removeContainer(self, container):
        """ Remove a container from its dock bar.

        Parameters
        ----------
        container : QDockContainer
            The container to remove from the dock bars.

        """
        button = self._widgets.pop(container, None)
        if button is not None:
            container.setParent(None)
            container.setPinned(False, quiet=True)
            container.frame_state.in_dock_bar = False
            container.alerted.disconnect(button.onAlerted)

            item = self._widgets.pop(button)
            item.setParent(None)
            self._untrackForResize(item)

            dock_bar = self._getDockBar(button.position())
            button.toggled.disconnect(self._onButtonToggled)
            button.setParent(None)
            if dock_bar.isEmpty():
                self._dock_bars[dock_bar.position()] = None
                dock_bar.setParent(None)

            event = QEvent(DockAreaContentsChanged)
            QApplication.sendEvent(self.parent(), event)

    def dockBarGeometry(self, position):
        """ Get the geometry of the dock bar at the given position.

        Parameters
        ----------
        position : QDockBar.Position
            The enum value specifying the dock bar of interest.

        Returns
        -------
        result : QRect
            The geometry of the given dock bar expressed in area
            coordinates. If no dock bar exists at the given position,
            an invalid QRect will be returned.

        """
        bar = self._getDockBar(position, create=False)
        if bar is None:
            return QRect()
        pos = bar.mapTo(self.parent(), QPoint(0, 0))
        return QRect(pos, bar.size())

    def dockBarContainers(self):
        """ Get the containers held in the dock bars.

        Returns
        -------
        result : list
            A list of tuples of the form (container, position).

        """
        res = []
        for value in self._widgets.values():
            if isinstance(value, QDockBarItem):
                res.append((value.widget(), value.position()))
        return res

    def dockBarPosition(self, container):
        """ Get the dock bar position of the given container.

        Parameters
        ----------
        container : QDockContainer
            The dock container of interest.

        Returns
        -------
        result : QDockBar.Position or None
            The position of the container, or None if the container
            does not exist in the manager.

        """
        button = self._widgets.get(container)
        if button is not None:
            return button.position()

    def clearDockBars(self):
        """ Clear all of the items from the dock bars.

        This method can be called to unconditionally remove all of the
        dock bars and reset the internal state of the manager. It is
        used by the framework and should not be called by user code.

        """
        for bar in self._dock_bars:
            if bar is not None:
                bar.setParent(None)
        self._dock_bars = [None, None, None, None]
        self._active_items = {}
        self._widgets = {}

    def isEmpty(self):
        """ Get whether or not the dock bars are empty.

        Returns
        -------
        result : bool
            True if the dock bars are empty, False otherwise.

        """
        return len(self._widgets) == 0

    def extendContainer(self, container):
        """ Extend the specified container.

        Parameters
        ----------
        container : QDockContainer
            The container to put in the extended position. If the
            container does not exist in the manager, this method is
            a no-op.

        """
        button = self._widgets.get(container)
        if button is not None:
            button.setChecked(True)

    def retractContainer(self, container):
        """ Retract the specified container.

        Parameters
        ----------
        container : QDockContainer
            The container to put in the retracted position. If the
            container does not exist in the manager, this method is
            a no-op.

        """
        button = self._widgets.get(container)
        if button is not None:
            button.setChecked(False)

    #--------------------------------------------------------------------------
    # Protected API
    #--------------------------------------------------------------------------
    def eventFilter(self, obj, event):
        """ Filter the events on the central pane.

        This event filter will resize the active containers in response
        to a resize of the central pane. This event filter is installed
        only when there are active containers for resizing.

        """
        if event.type() == QEvent.Resize:
            active = self._active_items
            for item, slide_out in active.items():
                start, end = self._animationGeo(item)
                animation = item.animation()
                if slide_out:
                    if animation is None:
                        item.setGeometry(end)
                    else:
                        animation.pause()
                        animation.setStartValue(start)
                        animation.setEndValue(end)
                        animation.resume()
                elif animation is not None:
                    animation.pause()
                    animation.setStartValue(end)
                    animation.setEndValue(start)
                    animation.resume()
        return False
