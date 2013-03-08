#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtGui import QTextEdit
from .qt_control import QtControl


class QtHtml(QtControl):
    """ A Qt implementation of an Enaml HTML widget.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying html widget.

        """
        widget = QTextEdit(parent)
        widget.setReadOnly(True)
        return widget

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(QtHtml, self).create(tree)
        self.set_source(tree['source'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_source(self, content):
        """ Handle the 'set_source' action from the Enaml widget.

        """
        self.set_source(content['source'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_source(self, source):
        """ Set the source of the html widget

        """
        self.widget().setHtml(source)

