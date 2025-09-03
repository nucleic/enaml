#------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from enaml.widgets.raw_widget import ProxyRawWidget

from .qt_control import QtControl


class QtRawWidget(QtControl, ProxyRawWidget):
    """ A Qt implementation of an Enaml ProxyRawWidget.

    """
    def create_widget(self):
        """ Create the underlying widget for the control.

        """
        self.widget = self.declaration.create_widget(self.parent_widget())

    #--------------------------------------------------------------------------
    # ProxyRawWidget API
    #--------------------------------------------------------------------------
    def get_widget(self):
        """ Retrieve the underlying toolkit widget.

        """
        return self.widget
