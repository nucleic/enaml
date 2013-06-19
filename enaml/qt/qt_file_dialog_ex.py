#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtGui import QFileDialog

from atom.api import Int, Typed

from enaml.widgets.file_dialog_ex import ProxyFileDialogEx

from .qt_toolkit_dialog import QtToolkitDialog


# Guard flags
FILTER_GUARD = 0x1


class QtFileDialogEx(QtToolkitDialog, ProxyFileDialogEx):
    """ A Qt implementation of an Enaml ProxyFileDialogEx.

    """
    widget = Typed(QFileDialog)

    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)

    def create_widget(self):
        """ Create the underlying QFileDialog widget.

        """
        self.widget = QFileDialog(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtFileDialogEx, self).init_widget()

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    # ProxyFileDialogEx API
    #--------------------------------------------------------------------------
    def set_current_path(self, path):
        pass

    def set_name_filters(self, filters):
        pass

    def set_selected_name_filter(self, selected):
        pass

    def exec_native(self):
        """ Exec a native file dialog for the declaration state.

        """
        d = self.declaration
        path = d.path
        caption = d.title
        filters = ';;'.join(d.filters)
        selected_filter = d.selected_filter
        if d.mode == 'open_file':
            path, selected_filter = QFileDialog.getOpenFileNameAndFilter(
                self.parent_widget(), caption, path, filters, selected_filter
            )
            paths = [path] if path else []
        elif d.mode == 'open_files':
            paths, selected_filter = QFileDialog.getOpenFileNamesAndFilter(
                self.parent_widget(), caption, path, filters, selected_filter
            )
        elif d.mode == 'save_file':
            path, selected_filter = QFileDialog.getSaveFileNameAndFilter(
                self.parent_widget(), caption, path, filters, selected_filter
            )
            paths = [path] if path else []
        else:
            path = QFileDialog.getExistingDirectory(
                self.parent_widget(), caption, path
            )
            paths = [path] if path else []
        result = 'accepted' if paths else 'rejected'
        d._handle_close(result, paths, selected_filter)

