#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.check_box import ProxyCheckBox

from .QtWidgets import QCheckBox

from .qt_abstract_button import QtAbstractButton


class QtCheckBox(QtAbstractButton, ProxyCheckBox):
    """ A Qt implementation of an Enaml ProxyCheckBox.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QCheckBox)

    def create_widget(self):
        """ Create the underlying check box widget.

        """
        self.widget = QCheckBox(self.parent_widget())
