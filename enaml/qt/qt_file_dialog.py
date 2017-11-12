#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.widgets.file_dialog import ProxyFileDialog

from .q_deferred_caller import deferredCall
from .q_file_dialog_helper import get_file_dialog_exec_func
from .qt_toolkit_object import QtToolkitObject


class QtFileDialog(QtToolkitObject, ProxyFileDialog):
    """ A Qt implementation of an Enaml ProxyFileDialog.

    """
    def exec_dialog(self):
        """ Exec a native file dialog for the declaration state.

        """
        d = self.declaration
        path = d.path
        caption = d.title
        filters = ';;'.join(d.filters)
        selected_filter = d.selected_filter
        exec_func = get_file_dialog_exec_func(d.mode)
        if d.mode == 'open_file':
            path, selected_filter = exec_func(
                self.parent_widget(), caption, path, filters, selected_filter
            )
            paths = [path] if path else []
        elif d.mode == 'open_files':
            paths, selected_filter = exec_func(
                self.parent_widget(), caption, path, filters, selected_filter
            )
        elif d.mode == 'save_file':
            path, selected_filter = exec_func(
                self.parent_widget(), caption, path, filters, selected_filter
            )
            paths = [path] if path else []
        else:
            path = exec_func(self.parent_widget(), caption, path)
            paths = [path] if path else []
        result = 'accepted' if paths else 'rejected'
        d._handle_close(result, paths, selected_filter)

    #--------------------------------------------------------------------------
    # ProxyFileDialog API
    #--------------------------------------------------------------------------
    def open(self):
        """ Run the dialog in a non-blocking fashion.

        This call will return immediately.

        """
        deferredCall(self.exec_dialog)

    def exec_(self):
        """ Run the dialog in a blocking fashion.

        This call will block until the user closes the dialog.

        """
        self.exec_dialog()
