#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int, Typed

from enaml.widgets.dialog import ProxyDialog

from .QtGui import QDialog

from .qt_window import QtWindow, QWindowLayout


class QCustomDialog(QDialog):
    """ A custom QDialog which uses a QWindowLayout to manage its
    central widget.

    The window layout computes the min/max size of the window based
    on its central widget, unless the user explicitly changes them.

    """
    def __init__(self, parent=None):
        """ Initialize a QWindow.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a QFrame.

        """
        super(QWindow, self).__init__(parent, Qt.Window)
        self._central_widget = None
        self._expl_min_size = QSize()
        self._expl_max_size = QSize()
        layout = QWindowLayout()
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)


class QtDialog(QtWindow, ProxyDialog):
    """ A Qt implementation of an Enaml ProxyDialog.

    """
    widget = Typed(QDialog)

    def create_widget(self):
        """ Create the underlying QFileDialog widget.

        """
        self.widget = QDialog(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtDialog, self).init_widget()
        d = self.declaration
        self.set_accept_mode(d.accept_mode)
        self.set_file_mode(d.file_mode)
        self.set_show_dirs_only(d.show_dirs_only)
        self.set_current_path(d.current_path)
        self.set_name_filters(d.name_filters)
        self.set_selected_name_filter(d.selected_name_filter)
        widget = self.widget
        widget.currentChanged.connect(self.on_current_changed)
        widget.filesSelected.connect(self.on_files_selected)
        widget.filterSelected.connect(self.on_filter_selected)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def get_default_title(self):
        """ Get the default window title for the file dialog.

        """
        widget = self.widget
        if widget.acceptMode() == QFileDialog.AcceptOpen:
            if widget.fileMode() == QFileDialog.Directory:
                return 'Find Directory'
            return 'Open'
        return 'Save As'

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_current_changed(self, path):
        """ Handle the 'currentChanged' signal from the dialog.

        """
        d = self.declaration
        if d is not None:
            self._guard |= PATH_GUARD
            try:
                d.current_path = path
            finally:
                self._guard &= ~PATH_GUARD

    def on_files_selected(self, paths):
        """ Handle the 'filesSelected' signal from the dialog.

        """
        d = self.declaration
        if d is not None:
            d.selected_paths = paths

    def on_filter_selected(self, selected):
        """ Handle the 'filterSelected' signal from the dialog.

        """
        d = self.declaration
        if d is not None:
            self._guard |= FILTER_GUARD
            try:
                d.selected_name_filter = selected
            finally:
                self._guard &= ~FILTER_GUARD

    #--------------------------------------------------------------------------
    # ProxyFileDialogEx API
    #--------------------------------------------------------------------------
    def set_accept_mode(self, mode):
        """ Set the accept mode of the underlying widget.

        """
        self.widget.setAcceptMode(ACCEPT_MODE[mode])

    def set_file_mode(self, mode):
        """ Set the file mode of the underlying widget.

        """
        self.widget.setFileMode(FILE_MODE[mode])

    def set_show_dirs_only(self, show):
        """ Set the show dirs only state of the underlying widget.

        """
        self.widget.setOption(QFileDialog.ShowDirsOnly, show)

    def set_current_path(self, path):
        """ Set the current path for the underlying widget.

        """
        if not self._guard & PATH_GUARD:
            self.widget.selectFile(path)

    def set_name_filters(self, filters):
        """ Set the name filters on the underlying widget.

        """
        self.widget.setNameFilters(filters)

    def set_selected_name_filter(self, selected):
        """ Set the selected name filter on the underlying widget.

        """
        if not self._guard & FILTER_GUARD:
            self.widget.selectNameFilter(selected)

    def exec_native(self):
        """ Exec a native file dialog for the declaration state.

        """
        d = self.declaration
        path = d.current_path
        caption = d.title
        filters = ';;'.join(d.name_filters)
        selected_filter = d.selected_name_filter
        parent = self.parent_widget()
        if d.file_mode == 'directory':
            path = QFileDialog.getExistingDirectory(parent, caption, path)
            paths = [path] if path else []
        elif d.accept_mode == 'save':
            path, selected_filter = QFileDialog.getSaveFileNameAndFilter(
                parent, caption, path, filters, selected_filter
            )
            paths = [path] if path else []
        elif d.file_mode == 'existing_files':
            paths, selected_filter = QFileDialog.getOpenFileNamesAndFilter(
                parent, caption, path, filters, selected_filter
            )
        else:
            path, selected_filter = QFileDialog.getOpenFileNameAndFilter(
                parent, caption, path, filters, selected_filter
            )
            paths = [path] if path else []
        if paths:
            self.on_current_changed(paths[0])
            self.on_filter_selected(selected_filter)
            self.on_files_selected(paths)
        d._proxy_finished(bool(paths))
