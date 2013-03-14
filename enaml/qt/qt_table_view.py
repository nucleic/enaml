#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QTableView

from atom.api import Typed

from enaml.widgets.table_view import ProxyTableView

from .q_item_model_wrapper import QItemModelWrapper
from .qt_control import QtControl


class QtTableView(QtControl, ProxyTableView):
    """ A Qt implementation of an Enaml ProxyTableView.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QTableView)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying widget.

        """
        self.widget = QTableView(self.parent_widget())
        self.widget.setAttribute(Qt.WA_StaticContents, True)

    def init_widget(self):
        """ Create and initialize the underlying control.

        """
        super(QtTableView, self).init_widget()
        d = self.declaration
        self.set_item_model(d.item_model)

    #--------------------------------------------------------------------------
    # ProxyListView API
    #--------------------------------------------------------------------------
    def set_item_model(self, model):
        """ Set the item model for the widget.

        """
        if not model:
            self.widget.setModel(None)
        else:
            self.widget.setModel(QItemModelWrapper(model))
