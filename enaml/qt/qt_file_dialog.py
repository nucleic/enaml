#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt import qt_api
from .qt.QtGui import QFileDialog
from .qt_object import QtObject


# A mapping from the Enaml dialog modes to the name of the static method
# on QFileDialog which will launch the appropriate native dialog.
if qt_api == 'pyqt':
    _NATIVE_METHOD_NAMES = {
        'open_file': 'getOpenFileNameAndFilter',
        'open_files': 'getOpenFileNamesAndFilter',
        'save_file': 'getSaveFileNameAndFilter',
        'directory': 'getExistingDirectory',
    }
else:
    _NATIVE_METHOD_NAMES = {
        'open_file': 'getOpenFileName',
        'open_files': 'getOpenFileNames',
        'save_file': 'getSaveFileName',
        'directory': 'getExistingDirectory',
    }


class QtFileDialog(QtObject):
    """ A Qt implementation of an Enaml FileDialog.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying widget.

        The file dialog widget is created on-demand when the open action
        is received. There is no persistent widget created for the file
        dialog.

        """
        return None

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_open(self, content):
        """ Handle the 'open' action from the Enaml widget.

        """
        if content['native_dialog']:
            result = self._open_native(content)
        else:
            result = self._open_non_native(content)
        self.send_action('closed', result)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _open_native(self, content):
        """ Open a native dialog for the given configuration.

        Parameters
        ----------
        content : dict
            The content dict sent by the Enaml widget for the `open`
            action.

        Returns
        -------
        result : dict
            The content dict for the `closed` action to be sent back
            to the Enaml widget.

        """
        mode = content['mode']
        assert mode in ('open_file', 'open_files', 'save_file', 'directory')

        def unpack_content():
            parent = self.parent_widget()
            caption = content['title']
            path = content['path']
            filters = u';;'.join(content['filters'])
            selected_filter = content['selected_filter']
            if mode == 'directory':
                args = (parent, caption, path)
            else:
                args = (parent, caption, path, filters, selected_filter)
            return args

        def pack_result(result):
            if mode == 'directory':
                paths = [result] if result else []
                selected_filter = u''
            elif mode == 'open_files':
                paths, selected_filter = result
            else:
                p, selected_filter = result
                paths = [p] if p else []
            content = {}
            if paths:
                content['result'] = 'accepted'
                content['paths'] = paths
                content['selected_filter'] = selected_filter
            else:
                content['result'] = 'rejected'
            return content

        method = getattr(QFileDialog, _NATIVE_METHOD_NAMES[mode])
        return pack_result(method(*unpack_content()))

    def _open_non_native(self, content):
        """ Open a non-native dialog for the given configuration.

        Parameters
        ----------
        content : dict
            The content dict sent by the Enaml widget for the `open`
            action.

        Returns
        -------
        result : dict
            The content dict for the `closed` action to be sent back
            to the Enaml widget.

        """
        mode = content['mode']
        assert mode in ('open_file', 'open_files', 'save_file', 'directory')

        dlg = QFileDialog(self.parent_widget())
        if mode == 'open_file':
            dlg.setAcceptMode(QFileDialog.AcceptOpen)
            dlg.setFileMode(QFileDialog.ExistingFile)
        elif mode == 'open_files':
            dlg.setAcceptMode(QFileDialog.AcceptOpen)
            dlg.setFileMode(QFileDialog.ExistingFiles)
        elif mode == 'save_file':
            dlg.setAcceptMode(QFileDialog.AcceptSave)
            dlg.setFileMode(QFileDialog.AnyFile)
        else:
            dlg.setAcceptMode(QFileDialog.AcceptOpen)
            dlg.setFileMode(QFileDialog.Directory)
            dlg.setOption(QFileDialog.ShowDirsOnly, True)

        caption = content['title']
        path = content['path']
        filters = content['filters']
        selected_filter = content['selected_filter']

        if caption:
            dlg.setWindowTitle(caption)
        dlg.setDirectory(path)
        dlg.setNameFilters(filters)
        dlg.selectNameFilter(selected_filter)

        result = {}
        if dlg.exec_():
            result['result'] = 'accepted'
            result['paths'] = dlg.selectedFiles()
            result['selected_filter'] = dlg.selectedNameFilter()
        else:
            result['result'] = 'rejected'

        return result

