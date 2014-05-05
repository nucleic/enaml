#------------------------------------------------------------------------------
# Copyright (c) 2014, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.timer import ProxyFocusTraversal

from .QtCore import Qt
from .QtGui import QWidget

from .qt_toolkit_object import QtToolkitObject


class QtFocusTraversal(QtToolkitObject, ProxyFocusTraversal):
    """ A Qt implementation of an Enaml ProxyFocusTraversal.

    """
    target = Typed(QWidget)

    def create_widget(self):
        """ Create the calender widget.

        """
        self.widget = None
        self.target = self.parent_widget()

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtFocusTraversal, self).init_widget()
        self.target.focusNextPrevChild = self.focusNextPrevChild

    def destroy(self):
        """ Destroy the underlying widget.

        """
        del self.target.focusNextPrevChild
        del self.target
        super(QtFocusTraversal, self).destroy()

    def focusNextPrevChild(self, next_):
        """

        """
        if next_:
            d_widget = self.declaration.next_focus_child()
        else:
            d_widget = self.declaration.previous_focus_child()
        if d_widget is not None:
            reason = Qt.TabFocusReason if next_ else Qt.BacktabFocusReason
            d_widget.proxy.widget.setFocus(reason)
            return True
        target = self.target
        return type(target).focusNextPrevChild(target, next_)
