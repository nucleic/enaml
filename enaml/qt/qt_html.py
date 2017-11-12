#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.html import ProxyHtml

from .QtWidgets import QTextEdit

from .qt_control import QtControl


class QtHtml(QtControl, ProxyHtml):
    """ A Qt implementation of an Enaml ProxyHtml widget.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QTextEdit)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying html widget.

        """
        widget = QTextEdit(self.parent_widget())
        widget.setReadOnly(True)
        self.widget = widget

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtHtml, self).init_widget()
        self.set_source(self.declaration.source)

    #--------------------------------------------------------------------------
    # ProxyHtml API
    #--------------------------------------------------------------------------
    def set_source(self, source):
        """ Set the source of the html widget

        """
        self.widget.setHtml(source)
