#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.label import ProxyLabel

from .QtCore import Qt
from .QtWidgets import QLabel

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
        self.set_text(d.text)
        self.set_align(d.align)
        self.set_vertical_align(d.vertical_align)
        self.widget.linkActivated.connect(self.on_link_activated)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_link_activated(self, link):
        """ Handle the link activated signal.

        """
        self.declaration.link_activated(link)

    #--------------------------------------------------------------------------
    # ProxyLabel API
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Set the text in the widget.

        """
        with self.geometry_guard():
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
