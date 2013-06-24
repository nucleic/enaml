#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import (
    Qt, QSize, QPoint, QRect, QMargins, QEvent, QObject, QPropertyAnimation
)
from PyQt4.QtGui import (
    QBoxLayout, QPainter, QSizePolicy, QFrame, QAbstractButton, QStyle,
    QStyleOption, QWidget, QColor, QGraphicsDropShadowEffect
)

from atom.api import Atom, Enum, IntEnum, Typed


class QDockBarButton(QAbstractButton):
    """

    """
    def __init__(self, parent=None):
        """

        """
        super(QDockBarButton, self).__init__(parent)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.setCheckable(True)

    def sizeHint(self):
        """

        """
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        """

        """
        return QSize(50, 20)

    def paintEvent(self, event):
        """

        """
        opt = QStyleOption()
        opt.initFrom(self)
        opt.state |= QStyle.State_AutoRaise
        is_down = self.isDown()
        is_enabled = self.isEnabled()
        is_checked = self.isChecked()
        under_mouse = self.underMouse()
        if is_enabled and under_mouse and not is_checked and not is_down:
            opt.state |= QStyle.State_Raised
        if is_checked:
            opt.state |= QStyle.State_On
        if is_down:
            opt.state |= QStyle.State_Sunken
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        # hack to get the current stylesheet foreground color
        hint = QStyle.SH_GroupBox_TextLabelColor
        fg = self.style().styleHint(hint, opt, self)
        # mask signed to unsigned which 'fromRgba' requires
        painter.setPen(QColor.fromRgba(0xffffffff & fg))
        painter.drawText(self.rect(), Qt.AlignCenter, self.text())


class QDockBar(QFrame):
    """

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
        """

        """
        super(QDockBar, self).__init__(parent)
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
        """

        """
        if event.type() == QEvent.StyleChange:
            self.updateSpacing()
        return super(QDockBar, self).event(event)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def updateSpacing(self):
        """

        """
        opt = QStyleOption()
        opt.initFrom(self)
        style = self.style()
        spacing = style.pixelMetric(QStyle.PM_ToolBarItemSpacing, opt, self)
        self.layout().setSpacing(spacing)

    def position(self):
        """

        """
        return self.Position(self.property('position'))

    def isEmpty(self):
        """

        """
        layout = self.layout()
        for index in xrange(layout.count()):
            item = layout.itemAt(index)
            if item.widget() is not None:
                return False
        return True

    def addButton(self, button):
        """

        """
        return self.insertButton(-1, button)

    def insertButton(self, index, button):
        """

        """
        assert isinstance(button, QDockBarButton)
        layout = self.layout()
        if index < 0:
            index = layout.count()
        if index == layout.count():
            index = max(0, index - 1)
        layout.insertWidget(index, button)


class QDockBarManager(QObject):
    """

    """
    def __init__(self, parent):
        super(QDockBarManager, self).__init__(parent)
        self._mask = QWidget(parent)
        self._out_animator = QPropertyAnimation()
        self._in_animator = QPropertyAnimation()
        self._out_animator.setPropertyName('geometry')
        self._in_animator.setPropertyName('geometry')
        self._in_animator.finished.connect(self._onSlideInFinished)
        self._dock_bars = [None, None, None, None]
        self._on_button = None
        self._buttons = {}

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    _shadow_offsets = [
        (0, 4),   # QDockBar.North
        (-4, 0),  # QDockBar.East
        (0, -4),  # QDockBar.South
        (4, 0),   # QDockBar.West
    ]

    @classmethod
    def _createDropShadowEffect(cls, position):
        """

        """
        effect = QGraphicsDropShadowEffect()
        effect.setBlurRadius(10)
        dx, dy = cls._shadow_offsets[position]
        effect.setOffset(dx, dy)
        return effect

    _layout_coords = [
        (0, 1, 1, 1),  # QDockBar.North
        (0, 2, 3, 1),  # QDockBar.East
        (2, 1, 1, 1),  # QDockBar.South
        (0, 0, 3, 1),  # QDockBar.West
    ]

    def _getDockBar(self, position):
        """

        """
        dock_bar = self._dock_bars[position]
        if dock_bar is not None:
            return dock_bar
        dock_bar = self._dock_bars[position] = QDockBar(position=position)
        coords = self._layout_coords[position]
        layout = self.parent().layoutPane().layout()
        layout.addWidget(dock_bar, *coords)
        return dock_bar

    def _maybeReleaseDockBar(self, dock_bar):
        """

        """
        if dock_bar.isEmpty():
            self._dock_bars[dock_bar.position()] = None
            dock_bar.hide()
            dock_bar.setParent(None)

    def _createButton(self, container):
        """

        """
        button = QDockBarButton()
        button.setText(container.title())
        button.setIcon(container.icon())
        self._buttons[container] = button
        self._buttons[button] = container
        button.toggled.connect(self._onButtonToggled)
        return button

    def _releaseButton(self, button):
        """

        """
        dock_bar = button.parent()
        button.toggled.disconnect(self._onButtonToggled)
        button.hide()
        button.setParent(None)
        self._maybeReleaseDockBar(dock_bar)

    def _onButtonToggled(self, checked):
        """

        """
        button = self.sender()
        container = self._buttons.get(button)
        if container is not None:
            position = button.parent().position()
            if checked:
                on_btn = self._on_button
                if on_btn is not None:
                    self._on_button = None
                    if on_btn is not button:
                        on_btn.setChecked(False)
                self._on_button = button
                self._slideOut(container, position)
            else:
                self._slideIn(container, position)

    def _slideOut(self, container, position):
        in_anim = self._in_animator
        if in_anim.targetObject() is container:
            in_anim.stop()
            in_anim.setTargetObject(None)
        out_anim = self._out_animator
        out_target = out_anim.targetObject()
        if out_target is container:
            return
        out_anim.stop()
        out_anim.setTargetObject(container)
        if out_target is not None:
            self._slideIn(out_target, QDockBar.North)
        start, end, mask = self._getAnimGeometries(container, position)
        if container.isVisibleTo(self._mask):
            start = container.geometry()
        else:
            container.setGeometry(start)
            container.show()
        out_anim.setStartValue(start)
        out_anim.setEndValue(end)
        self._mask.setGeometry(mask)
        self._mask.raise_()
        container.raise_()
        out_anim.start()

    def _slideIn(self, container, position):
        if not container.isVisibleTo(self._mask):
            return
        in_anim = self._in_animator
        in_target = in_anim.targetObject()
        if in_target is container:
            return
        in_anim.stop()
        in_anim.setTargetObject(container)
        if in_target is not None:
            in_target.hide()
        end, ignr_1, ignr_2 = self._getAnimGeometries(container, position)
        start = container.geometry()
        in_anim.setStartValue(start)
        in_anim.setEndValue(end)
        container.lower()
        in_anim.start()

    def _onSlideInFinished(self):
        in_anim = self._in_animator
        in_obj = in_anim.targetObject()
        in_anim.setTargetObject(None)
        in_obj.hide()
        if in_obj is self._out_animator.targetObject():
            self._out_animator.setTargetObject(None)
            self._mask.lower()

    def _centerGeometry(self):
        area = self.parent()
        pane = area.layoutPane()
        layout = pane.layout()
        cell = layout.cellRect(1, 1)
        pos = pane.mapTo(area, cell.topLeft())
        return QRect(pos, cell.size())

    def _getAnimGeometries(self, container, position):
        area = self.parent()
        pane = area.layoutPane()
        layout = pane.layout()
        cell = layout.cellRect(1, 1)
        hint = container.sizeHint()
        if position == QDockBar.North:
            start_pos = QPoint(0, -hint.height())
            end_pos = QPoint(0, 0)
            size = QSize(cell.width(), hint.height())
            adjust = (0, 0, 0, 10)
        elif position == QDockBar.East:
            start_pos = QPoint(cell.width(), 0)
            end_pos = QPoint(cell.width() - hint.width(), 0)
            size = QSize(hint.width(), cell.height())
            adjust = (-10, 0, 0, 0)
        elif position == QDockBar.South:
            start_pos = QPoint(0, cell.height())
            end_pos = QPoint(0, cell.height() - hint.height())
            size = QSize(cell.width(), hint.height())
            adjust = (0, -10, 0, 0)
        else:
            start_pos = QPoint(-hint.width(), 0)
            end_pos = QPoint(0, 0)
            size = QSize(hint.width(), cell.height())
            adjust = (0, 0, 10, 0)
        start_geo = QRect(start_pos, size)
        end_geo = QRect(end_pos, size)
        mask_geo = end_geo.adjusted(*adjust)
        origin = pane.mapTo(area, cell.topLeft())
        mask_geo.moveTopLeft(origin + mask_geo.topLeft())
        return start_geo, end_geo, mask_geo

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def addContainer(self, container, position):
        assert isinstance(position, QDockBar.Position)
        self.removeContainer(container)
        dock_bar = self._getDockBar(position)
        button = self._createButton(container)
        dock_bar.addButton(button)
        container.setParent(self._mask)
        container.setGraphicsEffect(self._createDropShadowEffect(position))

    def removeContainer(self, container):
        button = self._buttons.get(container, None)
        if button is not None:
            self._releaseButton(button)
            container.setGraphicsEffect(None)
