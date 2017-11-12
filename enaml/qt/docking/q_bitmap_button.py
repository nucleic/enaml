#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.qt.QtCore import QPoint, QRect, QEvent
from enaml.qt.QtGui import QPainter, QColor
from enaml.qt.QtWidgets import (
    QAbstractButton, QStyle, QStyleOption, QToolTip
)


class QBitmapButton(QAbstractButton):
    """ A button widget which renders a bitmap.

    This class is used to render the various maximize, restore, and
    close buttons in the docking framework. Bitmap images are chosen
    for rendering so that the button can be fully styled using Qt
    style sheets.

    """
    _bitmap = None

    def bitmap(self):
        """ Get the bitmap associated with the button.

        """
        return self._bitmap

    def setBitmap(self, bitmap):
        """ Set the bitmap associate with the button.

        """
        self._bitmap = bitmap
        self.update()

    def sizeHint(self):
        """ Get the size hint for the bitmap button.

        The size hint of the button is equal to it's icon size.

        """
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        """ Get the minimum size hint for the bitmap button.

        The minimum size hint of the button is equal to it's icon size.

        """
        return self.iconSize()

    def enterEvent(self, event):
        """ Handle the enter event for the button.

        """
        if self.isEnabled():
            self.update()
        super(QBitmapButton, self).enterEvent(event)

    def leaveEvent(self, event):
        """ Handle the leave event for the button.

        """
        if self.isEnabled():
            self.update()
        super(QBitmapButton, self).leaveEvent(event)

    def styleOption(self):
        """ Get a filled style option for the button.

        Returns
        -------
        result : QStyleOption
            A style option initialized for the current button state.

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
        return opt

    def drawBitmap(self, bmp, opt, painter):
        """ Draw the bitmap for the button.

        The bitmap will be drawn with the foreground color set by
        the style sheet and the style option.

        Parameters
        ----------
        bmp : QBitmap
            The bitmap to draw.

        opt : QStyleOption
            The style option to use for drawing.

        painter : QPainter
            The painter to use for drawing.

        """
        # hack to get the current stylesheet foreground color
        hint = QStyle.SH_GroupBox_TextLabelColor
        fg = self.style().styleHint(hint, opt, self)
        # mask signed to unsigned which 'fromRgba' requires
        painter.setPen(QColor.fromRgba(0xffffffff & fg))
        size = self.size()
        im_size = bmp.size()
        x = size.width() / 2 - im_size.width() / 2
        y = size.height() / 2 - im_size.height() / 2
        source = QRect(QPoint(0, 0), im_size)
        dest = QRect(QPoint(x, y), im_size)
        painter.drawPixmap(dest, bmp, source)

    def paintEvent(self, event):
        """ Handle the paint event for the button.

        """
        painter = QPainter(self)
        opt = self.styleOption()
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        bmp = self._bitmap
        if bmp is not None:
            self.drawBitmap(bmp, opt, painter)


class QCheckedBitmapButton(QBitmapButton):
    """ A bitmap button subclass which supports a checked bitmap.

    """
    _tool_tip = u''
    _checked_tool_tip = u''
    _checked_bitmap = None

    def __init__(self, parent=None):
        """ Initialize a QCheckedBitmapButton.

        Parameters
        ----------
        parent : QWidget or None
            The parent widget of the button.

        """
        super(QCheckedBitmapButton, self).__init__(parent)
        self.setCheckable(True)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _effectiveToolTip(self):
        """ Get the current effective tool tip for the button.

        """
        if self.isChecked():
            tool_tip = self._checked_tool_tip or self._tool_tip
        else:
            tool_tip = self._tool_tip
        return tool_tip

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def toolTip(self):
        """ Get the tool tip for the button.

        """
        return self._tool_tip

    def setToolTip(self, tool_tip):
        """ Set the tool tip for the button.

        """
        self._tool_tip = tool_tip

    def checkedToolTip(self):
        """ Get the checked tool tip for the button.

        """
        return self._checked_tool_tip

    def setCheckedToolTip(self, tool_tip):
        """ Set the checked tool tip for the button.

        """
        self._checked_tool_tip = tool_tip

    def checkedBitmap(self):
        """ Get the bitmap associated with the button checked state.

        """
        return self._checked_bitmap

    def setCheckedBitmap(self, bitmap):
        """ Set the bitmap associate with the button checked state.

        """
        self._checked_bitmap = bitmap
        self.update()

    def event(self, event):
        """ A generic event handler for the button.

        This handler shows the effective tool tip on a tool tip event.

        """
        if event.type() == QEvent.ToolTip:
            tool_tip = self._effectiveToolTip()
            if tool_tip:
                QToolTip.showText(event.globalPos(), tool_tip, self)
            return True
        return super(QCheckedBitmapButton, self).event(event)

    def paintEvent(self, event):
        """ Handle the paint event for the button.

        """
        painter = QPainter(self)
        opt = self.styleOption()
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
        if self.isChecked():
            bmp = self._checked_bitmap or self._bitmap
        else:
            bmp = self._bitmap
        if bmp is not None:
            self.drawBitmap(bmp, opt, painter)
