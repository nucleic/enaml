#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtGui import QMdiArea
from .qt_constraints_widget import QtConstraintsWidget
from .qt_mdi_window import QtMdiWindow


class QtMdiArea(QtConstraintsWidget):
    """ A Qt implementation of an Enaml MdiArea.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying QMdiArea widget.

        """
        return QMdiArea(parent)

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(QtMdiArea, self).init_layout()
        widget = self.widget()
        for child in self.children():
            if isinstance(child, QtMdiWindow):
                widget.addSubWindow(child.widget())

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtMdiArea.

        """
        if isinstance(child, QtMdiWindow):
            self.widget().removeSubWindow(child.widget())

    def child_added(self, child):
        """ Handle the child added event for a QtMdiArea.

        """
        # The size hint of a QMdiArea is typically quite large and the
        # size hint constraints are usually ignored. There is no need
        # to notify of a change in size hint here.
        if isinstance(child, QtMdiWindow):
            self.widget().addSubWindow(child.widget())

