#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtCore import Qt
from .qt.QtGui import QLabel
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


class QtLabel(QtControl):
    """ A Qt implementation of an Enaml Label.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying label widget.

        """
        return QLabel(parent)

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtLabel, self).create(tree)
        self.set_text(tree['text'])
        self.set_align(tree['align'])
        self.set_vertical_align(tree['vertical_align'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_text(self, content):
        """ Handle the 'set_text' action from the Enaml widget.

        """
        with size_hint_guard(self):
            self.set_text(content['text'])

    def on_action_set_align(self, content):
        """ Handle the 'set_align' action from the Enaml widget.

        """
        self.set_align(content['align'])

    def on_action_set_vertical_align(self, content):
        """ Handle the 'set_vertical_align' action from the Enaml widget.

        """
        self.set_vertical_align(content['vertical_align'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Set the text in the underlying widget.

        """
        self.widget().setText(text)

    def set_align(self, align):
        """ Set the alignment of the text in the underlying widget.

        """
        widget = self.widget()
        alignment = widget.alignment()
        alignment &= ~Qt.AlignHorizontal_Mask
        alignment |= ALIGN_MAP[align]
        widget.setAlignment(alignment)

    def set_vertical_align(self, align):
        """ Set the vertical alignment of the text in the underlying
        widget.

        """
        widget = self.widget()
        alignment = widget.alignment()
        alignment &= ~Qt.AlignVertical_Mask
        alignment |= VERTICAL_ALIGN_MAP[align]
        widget.setAlignment(alignment)

