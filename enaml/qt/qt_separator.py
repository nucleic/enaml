#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtCore import QSize
from .qt.QtGui import QFrame
from .qt_control import QtControl


# A mapping from Enaml orientation to frame shape enum.
_SHAPE_MAP = {
    'horizontal': QFrame.HLine,
    'vertical': QFrame.VLine,
}


# A mapping from Enaml line style to frame shadow enum.
_SHADOW_MAP = {
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


class QtSeparator(QtControl):
    """ A Qt implementation of an Enaml Separator.

    """
    def create_widget(self, parent, tree):
        """ Create underlying QSeparator control.

        """
        return QSeparator(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtSeparator, self).create(tree)
        self.set_orientation(tree['orientation'])
        self.set_line_style(tree['line_style'])
        self.set_line_width(tree['line_width'])
        self.set_midline_width(tree['midline_width'])

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_orientation(self, content):
        """ Handle the 'set_orientation' action from the Enaml widget.

        """
        self.set_orientation(content['orientation'])
        self.size_hint_updated()

    def on_action_set_line_style(self, content):
        """ Handle the 'set_line_style' action from the Enaml widget.

        """
        self.set_line_style(content['line_style'])
        self.size_hint_updated()

    def on_action_set_line_width(self, content):
        """ Handle the 'set_line_width' action from the Enaml widget.

        """
        self.set_line_width(content['line_width'])
        self.size_hint_updated()
        self.widget().update()

    def on_action_set_midline_width(self, content):
        """ Handle the 'set_midline_width' action from the Enaml widget.

        """
        self.set_midline_width(content['midline_width'])
        self.size_hint_updated()
        self.widget().update()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_orientation(self, orientation):
        """ Set the orientation of the underlying widget.

        """
        self.widget().setFrameShape(_SHAPE_MAP[orientation])

    def set_line_style(self, style):
        """ Set the line style of the underlying widget.

        """
        self.widget().setFrameShadow(_SHADOW_MAP[style])

    def set_line_width(self, width):
        """ Set the line width of the underlying widget.

        """
        self.widget().setLineWidth(width)

    def set_midline_width(self, width):
        """ Set the midline width of the underlying widget.

        """
        self.widget().setMidLineWidth(width)

