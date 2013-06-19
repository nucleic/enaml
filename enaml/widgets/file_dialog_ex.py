#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Enum, List, Unicode, Typed, ForwardTyped, observe

from enaml.core.declarative import d_

from .toolkit_dialog import ToolkitDialog, ProxyToolkitDialog


class ProxyFileDialogEx(ProxyToolkitDialog):
    """ The abstract defintion of a proxy FileDialogEx object.

    """
    #: A reference to the FileDialog declaration.
    declaration = ForwardTyped(lambda: FileDialogEx)

    def set_accept_mode(self, accept_mode):
        raise NotImplementedError

    def set_file_mode(self, file_mode):
        raise NotImplementedError

    def set_show_dirs_only(self, show):
        raise NotImplementedError

    def set_current_path(self, path):
        raise NotImplementedError

    def set_name_filters(self, filters):
        raise NotImplementedError

    def set_selected_name_filter(self, selected):
        raise NotImplementedError

    def exec_native(self):
        raise NotImplementedError


class FileDialogEx(ToolkitDialog):
    """ A toolkit dialog for getting file and directory names.

    This dialog supercedes the FileDialog class. New code you should
    use this dialog in lieu of the older version.

    """
    #: The accept mode of the dialog.
    accept_mode = d_(Enum('open', 'save'))

    #: The file mode of the dialog.
    file_mode = d_(Enum(
        'any_file', 'existing_file', 'existing_files', 'directory'))

    #: Whether or not to only show directories. This is only valid when
    #: the file_mode is set to 'directory'.
    show_dirs_only = d_(Bool(False))

    #: The currently selected path in the dialog.
    current_path = d_(Unicode())

    #: The paths selected by the user when the dialog is accepted.
    #: This value is output only.
    selected_paths = List(Unicode())

    #: The name filters used to restrict the available files.
    name_filters = d_(List(Unicode()))

    #: The selected name filter from the list of name filters.
    selected_name_filter = d_(Unicode())

    #: A reference to the ProxyFileDialog object.
    proxy = Typed(ProxyFileDialogEx)

    @staticmethod
    def get_existing_directory(parent=None, **kwargs):
        """ Get an existing directory on the filesystem.

        Parameters
        ----------
        parent : ToolkitObject or None
            The parent toolkit object for this dialog.

        **kwargs
            Additional data to pass to the dialog constructor.

        Returns
        -------
        result : unicode
            The user selected directory path. This will be an empty
            string if no directory was selected.

        """
        kwargs['accept_mode'] = 'open'
        kwargs['file_mode'] = 'directory'
        kwargs['show_dirs_only'] = True
        dialog = FileDialogEx(parent, **kwargs)
        if dialog.exec_native():
            if dialog.selected_paths:
                return dialog.selected_paths[0]
        return u''

    @staticmethod
    def get_open_file_name(parent=None, **kwargs):
        """ Get the file name for an open file dialog.

        Parameters
        ----------
        parent : ToolkitObject or None
            The parent toolkit object for this dialog.

        **kwargs
            Additional data to pass to the dialog constructor.

        Returns
        -------
        result : unicode
            The user selected file name. This will be an empty
            string if no file name was selected.

        """
        kwargs['accept_mode'] = 'open'
        kwargs['file_mode'] = 'existing_file'
        dialog = FileDialogEx(parent, **kwargs)
        if dialog.exec_native():
            if dialog.selected_paths:
                return dialog.selected_paths[0]
        return u''

    @staticmethod
    def get_open_file_names(parent=None, **kwargs):
        """ Get the file names for an open files dialog.

        Parameters
        ----------
        parent : ToolkitObject or None
            The parent toolkit object for this dialog.

        **kwargs
            Additional data to pass to the dialog constructor.

        Returns
        -------
        result : list
            The user selected file names. This will be an empty
            list if no file names were selected.

        """
        kwargs['accept_mode'] = 'open'
        kwargs['file_mode'] = 'existing_files'
        dialog = FileDialogEx(parent, **kwargs)
        if dialog.exec_native():
            return dialog.selected_paths
        return []

    @staticmethod
    def get_save_file_name(parent=None, **kwargs):
        """ Get the file name for a save file dialog.

        Parameters
        ----------
        parent : ToolkitObject or None
            The parent toolkit object for this dialog.

        **kwargs
            Additional data to pass to the dialog constructor.

        Returns
        -------
        result : unicode
            The user selected file name. This will be an empty
            string if no file name was selected.

        """
        kwargs['accept_mode'] = 'save'
        kwargs['file_mode'] = 'any_file'
        dialog = FileDialogEx(parent, **kwargs)
        if dialog.exec_native():
            if dialog.selected_paths:
                return dialog.selected_paths[0]
        return u''

    def exec_native(self):
        """ Open the dialog using a native OS dialog if available.

        Returns
        -------
        result : bool
            Whether or not the dialog was accepted.

        """
        if not self.is_initialized:
            self.initialize()
        if not self.proxy_is_active:
            self.activate_proxy()
        self._prepare()
        self.proxy.exec_native()
        return self.result

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('accept_mode', 'file_mode', 'show_dirs_only', 'current_path',
        'name_filters', 'selected_name_filter'))
    def _update_proxy(self, change):
        """ An observer which updates the proxy when the data changes.

        """
        # The superclass implementation is sufficient.
        super(FileDialogEx, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def _prepare(self):
        """ A reimplemented preparation method.

        This method resets the selected paths and filters.

        """
        super(FileDialogEx, self)._prepare()
        self.selected_paths = []
        self.selected_name_filter = u''
