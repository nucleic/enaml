#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.radio_button import ProxyRadioButton

from .QtWidgets import QRadioButton

from .qt_abstract_button import QtAbstractButton


class QtRadioButton(QtAbstractButton, ProxyRadioButton):
    """ A Qt implementation of an Enaml RadioButton.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QRadioButton)

    def create_widget(self):
        """ Create the underlying radio button widget.

        """
        self.widget = QRadioButton(self.parent_widget())
