#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtGui import QFileDialog

from atom.api import Typed

from enaml.widgets.file_dialog import ProxyFileDialog

from .q_deferred_caller import deferredCall
from .qt_toolkit_object import QtToolkitObject


class QtFileDialog(QtToolkitObject, ProxyFileDialog):
    """ A Qt implementation of an Enaml ProxyFileDialog.

    The handling of file dialogs is a bit special. A QFileDialog is only
    created when not using the native file dialog methods. Those methods
    always block, so opening a native dialog in non-blocking mode means
    is must be executed in a deferred fashion.

    """
    #: A reference to the widget created by the proxy. This is only used
    #: when using non-native file dialogs.
    widget = Typed(QFileDialog)

    def create_non_native_dialog(self):
        """ Create a non-native QFileDialog.

        This will use the current state of the declaration object to
        populate the state of the new dialog.

        """
        widget = QFileDialog(self.parent_widget())
        d = self.declaration
        if d.mode == 'open_file':
            widget.setAcceptMode(QFileDialog.AcceptOpen)
            widget.setFileMode(QFileDialog.ExistingFile)
        elif d.mode == 'open_files':
            widget.setAcceptMode(QFileDialog.AcceptOpen)
            widget.setFileMode(QFileDialog.ExistingFiles)
        elif d.mode == 'save_file':
            widget.setAcceptMode(QFileDialog.AcceptSave)
            widget.setFileMode(QFileDialog.AnyFile)
        else:
            widget.setAcceptMode(QFileDialog.AcceptOpen)
            widget.setFileMode(QFileDialog.Directory)
            widget.setOption(QFileDialog.ShowDirsOnly, True)
        if d.title:
            widget.setWindowTitle(d.title)
        widget.setDirectory(d.path)
        widget.setNameFilters(d.filters)
        widget.selectNameFilter(d.selected_filter)
        return widget

    def open_non_native_dialog(self):
        """ Create and open a non-native QFileDialog.

        This call will return immediately. The created dialog will be
        stored in the 'widget' attribute and the processing of the
        results will occur when its 'connect' signal is emitted.

        """
        self.widget = dialog = self.create_non_native_dialog()
        dialog.finished.connect(self.on_non_native_finished)
        dialog.open()

    def on_non_native_finished(self, result):
        """ The handler for the 'finished' signal on a QFileDialog.

        This handler will process the results of the dialog and then
        call the 'handle_close' method.

        """
        dialog = self.widget
        if result and dialog:
            paths = dialog.selectedFiles()
            selected_filter = dialog.selectedNameFilter()
            dialog.setParent(None)
            del self.widget
        else:
            paths = []
            selected_filter = u''
        self.handle_close(paths, selected_filter)

    def exec_non_native_dialog(self):
        """ Create and exec a non-native QFileDialog.

        This call blocks. When the dialog is closed, this method will
        invoke the 'handle' close method.

        """
        self.widget = dialog = self.create_non_native_dialog()
        if dialog.exec_():
            paths = dialog.selectedFiles()
            selected_filter = dialog.selectedNameFilter()
        else:
            paths = []
            selected_filter = u''
        dialog.setParent(None)
        del self.widget
        self.handle_close(paths, selected_filter)

    def open_native_dialog(self):
        """ Open a native file dialog in a non-blocking fashion.

        Native file dialogs always block, so this method will dispatch
        the execution of the call to the next cycle of the event loop.

        """
        # Native dialogs always block. Open them "non blocking" by
        # using a deferred closure
        def closure():
            paths, selected_filter = self.exec_native_dialog()
            self.handle_close(paths, selected_filter)
        deferredCall(closure)

    def exec_native_dialog(self):
        """ Exec a native file dialog.

        This call blocks. When the dialog is closed, this method will
        invoke the 'handle' close method.

        """
        parent = self.parent_widget()
        d = self.declaration
        path = d.path
        caption = d.title
        filters = ';;'.join(d.filters)
        selected_filter = d.selected_filter
        if d.mode == 'open_file':
            path, selected_filter = QFileDialog.getOpenFileNameAndFilter(
                parent, caption, path, filters, selected_filter
            )
            paths = [path] if path else []
        elif d.mode == 'open_files':
            paths, selected_filter = QFileDialog.getOpenFileNamesAndFilter(
                parent, caption, path, filters, selected_filter
            )
            path = paths[0] if path else u''
        elif d.mode == 'save_file':
            path, selected_filter = QFileDialog.getSaveFileNameAndFilter(
                parent, caption, path, filters, selected_filter
            )
            paths = [path] if path else []
        else:
            path = QFileDialog.getExistingDirectory(parent, caption, path)
            paths = [path] if path else []
        self.handle_close(paths, selected_filter)

    def handle_close(self, paths, selected_filter):
        """ Handle the close results of a dialog.

        This method will update the state of the declaration based on
        the results of the dialog and then calls the '_handle_close'
        method of the declaration.

        """
        d = self.declaration
        if paths:
            d.result = 'accepted'
            d.paths = paths
            d.path = paths[0]
            d.selected_filter = selected_filter
        else:
            d.result = 'rejected'
        d._handle_close()

    #--------------------------------------------------------------------------
    # ProxyFileDialog API
    #--------------------------------------------------------------------------
    def open(self):
        """ Run the dialog in a non-blocking fashion.

        This call will return immediately.

        """
        d = self.declaration
        if d.native_dialog:
            self.open_native_dialog()
        else:
            self.open_non_native_dialog()

    def exec_(self):
        """ Run the dialog in a blocking fashion.

        This call will block until the user closes the dialog.

        """
        if self.declaration.native_dialog:
            self.exec_native_dialog()
        else:
            self.exec_non_native_dialog()

    def accept(self):
        """ Accept the current selection and close the dialog.

        """
        if self.widget:
            self.widget.accept()

    def reject(self):
        """ Reject the current selection and close the dialog.

        """
        if self.widget:
            self.widget.reject()
