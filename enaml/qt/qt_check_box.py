#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtGui import QCheckBox
from .qt_abstract_button import QtAbstractButton


class QtCheckBox(QtAbstractButton):
    """ A Qt implementation of an Enaml CheckBox.

    """
    def create_widget(self, parent, tree):
        """ Create the underlying check box widget.

        """
        return QCheckBox(parent)

