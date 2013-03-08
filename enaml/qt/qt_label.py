#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QLabel

from atom.api import Typed

from enaml.widgets.label import ProxyLabel

from .qt_constraints_widget import size_hint_guard
from .qt_control import QtControl


ALIGN_MAP = {
    'left': Qt.AlignLeft,
    'right': Qt.AlignRight,
    'center': Qt.AlignHCenter,
    'justify': Qt.AlignJustify,
}


VERTICAL_ALIGN_MAP = {
    'top': Qt.AlignTop,
    'bottom': Qt.AlignBottom,
    'center': Qt.AlignVCenter,
}


class QtLabel(QtControl, ProxyLabel):
    """ A Qt implementation of an Enaml ProxyLabel.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QLabel)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying label widget.

        """
        self.widget = QLabel(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtLabel, self).init_widget()
        d = self.declaration
        self.set_text(d.text, sh_guard=False)
        self.set_align(d.align)
        self.set_vertical_align(d.vertical_align)

    #--------------------------------------------------------------------------
    # ProxyLabel API
    #--------------------------------------------------------------------------
    def set_text(self, text, sh_guard=True):
        """ Set the text in the widget.

        """
        if sh_guard:
            with size_hint_guard(self):
                self.widget.setText(text)
        else:
            self.widget.setText(text)

    def set_align(self, align):
        """ Set the alignment of the text in the widget.

        """
        widget = self.widget
        alignment = widget.alignment()
        alignment &= ~Qt.AlignHorizontal_Mask
        alignment |= ALIGN_MAP[align]
        widget.setAlignment(alignment)

    def set_vertical_align(self, align):
        """ Set the vertical alignment of the text in the widget.

        """
        widget = self.widget
        alignment = widget.alignment()
        alignment &= ~Qt.AlignVertical_Mask
        alignment |= VERTICAL_ALIGN_MAP[align]
        widget.setAlignment(alignment)
