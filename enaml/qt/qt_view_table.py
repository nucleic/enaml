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

from enaml.widgets.view_table import ProxyViewTable

from .q_item_model_wrapper import QItemModelWrapper
from .qt_control import QtControl


class QtViewTable(QtControl, ProxyViewTable):
    """ A Qt implementation of an Enaml ProxyTable.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QTableView)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QTableView widget.

        """
        self.widget = QTableView(self.parent_widget())
        self.widget.setAttribute(Qt.WA_StaticContents, True)

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtViewTable, self).init_widget()
        d = self.declaration
        self.set_table_model(d.table_model)
        self.set_orientation(d.orientation)

    #--------------------------------------------------------------------------
    # ProxyViewTable API
    #--------------------------------------------------------------------------
    def set_table_model(self, model):
        """ Set the table model for the underlying control.

        """
        if model is None:
            self.widget.setModel(None)
        else:
            self.widget.setModel(QItemModelWrapper(model))

    def set_orientation(self, orientation):
        """ Set the orientation for the widget.

        """
        widget = self.widget
        if orientation == 'horizontal':
            widget.verticalHeader().setVisible(False)
            widget.horizontalHeader().setVisible(True)
        else:
            widget.verticalHeader().setVisible(True)
            widget.horizontalHeader().setVisible(False)
