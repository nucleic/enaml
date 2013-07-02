#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import IntEnum

from enaml.qt.QtCore import (
    QSize, QPoint, QRect, QMargins, QEvent, QObject, QPropertyAnimation
)
from enaml.qt.QtGui import (
    QBoxLayout, QSizePolicy, QFrame, QPushButton, QStyle, QStyleOption,
    QGraphicsDropShadowEffect, QStylePainter, QStyleOptionButton,
    QApplication
)

from .event_types import DockAreaContentsChanged


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

    #: A mapping from PinPosition to layout direction.
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
        return self.Position(self.property('position'))

    def isEmpty(self):
        """ Get whether or not the dock bar is empty.

        Returns
        -------
        result : bool
            True if the dock bar has dock buttons, False otherwise.

        """
        layout = self.layout()
        for index in xrange(layout.count()):
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
        painter.drawControl(QStyle.CE_PushButton, opt);


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
        self._active_containers = {}
        self._button_map = {}

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: A static mapping of dock position to drop shadow offset.
    _shadow_offsets = [
        (0, 4),   # QDockBar.North
        (-4, 0),  # QDockBar.East
        (0, -4),  # QDockBar.South
        (4, 0),   # QDockBar.West
    ]

    #: A static mapping of dock position to grid layout coordinates.
    _layout_coords = [
        (0, 1, 1, 1),  # QDockBar.North
        (1, 2, 1, 1),  # QDockBar.East
        (2, 1, 1, 1),  # QDockBar.South
        (1, 0, 1, 1),  # QDockBar.West
    ]

    @classmethod
    def _createDropShadowEffect(cls, position):
        """ Create a drop shadow effect for the given position.

        Parameters
        ----------
        position : QDockBar.Position
            The dock position for which to create the effect.

        Returns
        -------
        result : QGraphicsDropShadowEffect
            A drop shadow effect configured for the given position.

        """
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(10)
        dx, dy = cls._shadow_offsets[position]
        effect.setOffset(dx, dy)
        return effect

    @staticmethod
    def _prepareAnimation(container):
        """ Prepare the animation object for a dock container.

        Parameters
        ----------
        container : QDockContainer
            The container for which to resolve the animation.

        """
        animation = container.frame_state.dock_bar_animation
        if animation is not None:
            animation.stop()
            animation.finished.disconnect()
        else:
            animation = QPropertyAnimation(container, 'geometry')
            container.frame_state.dock_bar_animation = animation
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

    def _createButton(self, container):
        """ Create a dock button for the given container and position.

        Parameters
        ----------
        container : QDockContainer
            The container for which to create the button.

        Returns
        -------
        result : QDockBarButton
            The dock bar button for the given container.

        """
        button = QDockBarButton()
        button.setText(container.title())
        button.setIcon(container.icon())
        button.toggled.connect(self._onButtonToggled)
        self._button_map[button] = container
        self._button_map[container] = button
        return button

    def _trackForResize(self, container, position, slide_out):
        """ Track the given container for resize events on the pane.

        Parameters
        ----------
        container : QDockContainer
            The dock container which should track pane resizes.

        position : QDockBar.Position
            The dock position of the container.

        slide_out : bool
            Whether the container is in the slide out position.

        """
        active = self._active_containers
        install = len(active) == 0
        active[container] = (position, slide_out)
        if install:
            self.parent().centralPane().installEventFilter(self)

    def _untrackForResize(self, container):
        """ Untrack the given container for resize events on the pane.

        Parameters
        ----------
        container : QDockContainer
            The dock container which should untrack pane resizes.

        """
        active = self._active_containers
        active.pop(container, None)
        if len(active) == 0:
            self.parent().centralPane().removeEventFilter(self)

    def _slideOut(self, container, position):
        """ Animate the slide out for the container and position.

        Parameters
        ----------
        container : QDockContainer
            The dock container which should be slide out animated.

        position : QDockBar.Position
            The dock position at which to animate.

        """
        self._trackForResize(container, position, True)
        animation = self._prepareAnimation(container)
        animation.finished.connect(self._onSlideOutFinished)
        start_geo, end_geo = self._animationGeo(container, position)
        if container.isVisible():
            start_geo = container.geometry()
        else:
            container.setGeometry(start_geo)
            container.show()
        container.raise_()
        animation.setStartValue(start_geo)
        animation.setEndValue(end_geo)
        animation.start()

    def _slideIn(self, container, position):
        """ Animate the slide in for the container and position.

        Parameters
        ----------
        container : QDockContainer
            The dock container which should be slide in animated.

        position : QDockBar.Position
            The dock position at which to animate.

        """
        if not container.isVisible():
            return
        self._trackForResize(container, position, False)
        animation = self._prepareAnimation(container)
        animation.finished.connect(self._onSlideInFinished)
        start_geo = container.geometry()
        end_geo, ignored = self._animationGeo(container, position)
        animation.setStartValue(start_geo)
        animation.setEndValue(end_geo)
        animation.start()

    def _animationGeo(self, container, position):
        """ Get the animation geometry for the container and position.

        Parameters
        ----------
        container : QDockContainer
            The dock container to be animated.

        position : QDockBar.Position
            The dock position at which to animate.

        Returns
        -------
        result : tuple
            A 2-tuple of QRect objects representing the start and end
            geometries for the animation assuming a slide out effect.

        """
        pane = self.parent().centralPane()
        hint = container.sizeHint().boundedTo(pane.size())
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
        for key in self._button_map:
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
        container = self._button_map.get(button)
        if container is not None:
            position = button.parent().position()
            if checked:
                self._slideOut(container, position)
            else:
                self._slideIn(container, position)

    def _onSlideOutFinished(self):
        """ Handle the 'finished' signal from a slide out animation.

        """
        animation = self.sender()
        container = animation.targetObject()
        container.frame_state.dock_bar_animation = None
        self.parent().centralPane().installEventFilter(self)

    def _onSlideInFinished(self):
        """ Handle the 'finished' signal from a slide in animation.

        """
        animation = self.sender()
        container = animation.targetObject()
        container.frame_state.dock_bar_animation = None
        container.hide()
        self._untrackForResize(container)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def addContainer(self, container, position):
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

        """
        assert isinstance(position, QDockBar.Position)
        self.removeContainer(container)
        button = QDockBarButton()
        button.setText(container.title())
        button.setIcon(container.icon())
        button.toggled.connect(self._onButtonToggled)
        self._button_map[button] = container
        self._button_map[container] = button
        dock_bar = self._getDockBar(position)
        dock_bar.addButton(button)
        container.setParent(self.parent().centralPane())
        container.setGraphicsEffect(self._createDropShadowEffect(position))
        container.frame_state.in_dock_bar = True
        area = self.parent()
        QApplication.sendEvent(area, QEvent(DockAreaContentsChanged))

    def removeContainer(self, container):
        """ Remove a container from its dock bar.

        Parameters
        ----------
        container : QDockContainer
            The container to remove from the dock bars.

        """
        button = self._button_map.pop(container, None)
        if button is not None:
            del self._button_map[button]
            container.setParent(None)
            container.setGraphicsEffect(None)
            container.frame_state.in_dock_bar = False
            self._untrackForResize(container)
            dock_bar = self._getDockBar(button.position())
            button.toggled.disconnect(self._onButtonToggled)
            button.setParent(None)
            if dock_bar.isEmpty():
                self._dock_bars[dock_bar.position()] = None
                dock_bar.setParent(None)
            area = self.parent()
            QApplication.sendEvent(area, QEvent(DockAreaContentsChanged))

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
        for key, value in self._button_map.iteritems():
            if isinstance(key, QDockBarButton):
                res.append((value, key.position()))
        return res

    def isEmpty(self):
        """ Get whether or not the dock bars are empty.

        Returns
        -------
        result : bool
            True if the dock bars are empty, False otherwise.

        """
        return len(self._button_map) == 0

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
            active = self._active_containers
            for container, (position, slide_out) in active.iteritems():
                start, end = self._animationGeo(container, position)
                animation = container.frame_state.dock_bar_animation
                if slide_out:
                    if animation is None:
                        container.setGeometry(end)
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
