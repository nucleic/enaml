#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.toolkit_dialog import ProxyToolkitDialog

from .QtWidgets import QDialog

from .qt_toolkit_object import QtToolkitObject


class QtToolkitDialog(QtToolkitObject, ProxyToolkitDialog):
    """ A Qt implementation of an Enaml ProxyToolkitDialog.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QDialog)

    def create_widget(self):
        """ Create the underlying QColorDialog.

        """
        self.widget = QDialog(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtToolkitDialog, self).init_widget()
        self.set_title(self.declaration.title)
        self.widget.finished.connect(self.on_finished)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def get_default_title(self):
        """ Get the default window title for the dialog.

        This can be reimplemented by subclass to provide a default
        window title. The base implementation returns an empty string.

        """
        return u''

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_finished(self, result):
        """ Handle the 'finished' signal from the widget.

        """
        d = self.declaration
        if d is not None:
            d._proxy_finished(bool(result))

    #--------------------------------------------------------------------------
    # ProxyToolkitDialog API
    #--------------------------------------------------------------------------
    def set_title(self, title):
        """ Set the window title for the underlying widget.

        """
        self.widget.setWindowTitle(title or self.get_default_title())

    def show(self):
        """ Open the dialog as non modal.

        """
        self.widget.show()

    def open(self):
        """ Open the dialog as window modal.

        """
        self.widget.open()

    def exec_(self):
        """ Open the dialog as application modal.

        """
        self.widget.exec_()

    def accept(self):
        """ Accept the current state and close the dialog.

        """
        self.widget.accept()

    def reject(self):
        """ Reject the current state and close the dialog.

        """
        self.widget.reject()
