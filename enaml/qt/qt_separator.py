#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.separator import ProxySeparator

from .QtCore import QSize
from .QtWidgets import QFrame

from .qt_control import QtControl


# A mapping from Enaml orientation to frame shape enum.
LINE_SHAPES = {
    'horizontal': QFrame.HLine,
    'vertical': QFrame.VLine,
}


# A mapping from Enaml line style to frame shadow enum.
LINE_STYLES = {
    'sunken': QFrame.Sunken,
    'raised': QFrame.Raised,
    'plain': QFrame.Plain
}


class QSeparator(QFrame):
    """ A QFrame subclass which acts as a separator.

    This subclass reimplements the sizeHint method to compute a hint
    which is appropriate for a frame being used as a vertical or
    horizontal separator line.

    """
    def sizeHint(self):
        # The default sizeHint method returns (-1, 3) or (3, -1) when
        # the frame is used as a separator, regardless of the computed
        # frame width. This override corrects that behavior.
        hint = super(QSeparator, self).sizeHint()
        if self.frameShadow() in (QFrame.Raised, QFrame.Sunken):
            shape = self.frameShape()
            if shape == QFrame.HLine:
                hint = QSize(hint.width(), max(3, self.frameWidth() * 2))
            elif shape == QFrame.VLine:
                hint = QSize(max(3, self.frameWidth() * 2), hint.height())
        return hint


class QtSeparator(QtControl, ProxySeparator):
    """ A Qt implementation of an Enaml ProxySeparator.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QSeparator)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create underlying QSeparator control.

        """
        self.widget = QSeparator(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtSeparator, self).init_widget()
        d = self.declaration
        self.set_orientation(d.orientation)
        self.set_line_style(d.line_style)
        self.set_line_width(d.line_width)
        self.set_midline_width(d.midline_width)

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_orientation(self, orientation):
        """ Set the orientation of the underlying widget.

        """
        with self.geometry_guard():
            self.widget.setFrameShape(LINE_SHAPES[orientation])

    def set_line_style(self, style):
        """ Set the line style of the underlying widget.

        """
        with self.geometry_guard():
            self.widget.setFrameShadow(LINE_STYLES[style])

    def set_line_width(self, width):
        """ Set the line width of the underlying widget.

        """
        with self.geometry_guard():
            self.widget.setLineWidth(width)
        self.widget.update()

    def set_midline_width(self, width):
        """ Set the midline width of the underlying widget.

        """
        with self.geometry_guard():
            self.widget.setMidLineWidth(width)
        self.widget.update()
