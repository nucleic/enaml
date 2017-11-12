#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, atomref

from enaml.widgets.dialog import ProxyDialog
from enaml.widgets.window import CloseEvent

from .QtCore import Qt
from .QtWidgets import QDialog

from .q_deferred_caller import deferredCall
from .q_window_base import QWindowBase
from .qt_window import QtWindow, finalize_close


class QWindowDialog(QDialog, QWindowBase):
    """ A window base subclass which implements dialog behavior.

    """
    def __init__(self, proxy, parent=None, flags=Qt.Widget):
        """ Initialize a QWindowDialog.

        Parameters
        ----------
        proxy : QtDialog
            The proxy object which owns this dialog. Only an atomref
            will be maintained to this object.

        parent : QWidget, optional
            The parent of the dialog.

        flags : Qt.WindowFlags, optional
            The window flags to pass to the parent constructor.

        """
        super(QWindowDialog, self).__init__(parent, flags)
        self._proxy_ref = atomref(proxy)

    def closeEvent(self, event):
        """ Handle the close event for the dialog.

        """
        event.accept()
        if not self._proxy_ref:
            return
        proxy = self._proxy_ref()
        d = proxy.declaration
        d_event = CloseEvent()
        d.closing(d_event)
        if d_event.is_accepted():
            super(QWindowDialog, self).closeEvent(event)
        else:
            event.ignore()


class QtDialog(QtWindow, ProxyDialog):
    """ A Qt implementation of an Enaml ProxyDialog.

    """
    widget = Typed(QWindowDialog)

    def create_widget(self):
        """ Create the underlying QFileDialog widget.

        """
        flags = self.creation_flags()
        self.widget = QWindowDialog(self, self.parent_widget(), flags)

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
        deferredCall(finalize_close, d)

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
