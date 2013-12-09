#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.dialog import ProxyDialog

from .QtCore import Qt, Signal, QSize
from .QtGui import QDialog, QLayout

from .q_window_base import QWindowBase, QWindowLayout
from .qt_window import QtWindow

from . import QT_API 

class QWindowDialog(QDialog, QWindowBase):
    """ A window base subclass which implements dialog behavior.

    """
    # This signal must be redefined, or the QtWindow base class will
    # not be able to connect to it. This is a quirk of using multiple
    # inheritance with PyQt. Note that this signal is never emitted
    # it is here only for API compatibility with the base class.
    closed = Signal()

    def __init__(self, parent=None, flags=Qt.Widget):
        """ Initialize a QWindowDialog.

        Parameters
        ----------
        parent : QWidget, optional
            The parent of the dialog.

        """
        super(QWindowDialog, self).__init__(parent, flags)
        #Pyside's mro goes off the rails and the QWindowBase.__init__ method does not get called.
        #Copy in the necessary layout code here. 
        if QT_API == 'pyside':
            self._expl_min_size = QSize()
            self._expl_max_size = QSize()
            layout = QWindowLayout()
            layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
            self.setLayout(layout)


class QtDialog(QtWindow, ProxyDialog):
    """ A Qt implementation of an Enaml ProxyDialog.

    """
    widget = Typed(QWindowDialog)

    def create_widget(self):
        """ Create the underlying QFileDialog widget.

        """
        flags = self.creation_flags()
        self.widget = QWindowDialog(self.parent_widget(), flags)

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtDialog, self).init_widget()
        self.widget.finished.connect(self.on_finished)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_finished(self):
        """ Handle the 'finished' signal on the dialog.

        """
        result = bool(self.widget.result())
        d = self.declaration
        d.result = result
        d.finished(result)
        if result:
            d.accepted()
        else:
            d.rejected()
        d._handle_close()

    #--------------------------------------------------------------------------
    # ProxyDialog API
    #--------------------------------------------------------------------------
    def exec_(self):
        """ Launch the dialog as a modal window.

        """
        return bool(self.widget.exec_())

    def done(self, result):
        """ Close the dialog and set the result code.

        """
        q_result = QDialog.Accepted if result else QDialog.Rejected
        self.widget.done(q_result)
