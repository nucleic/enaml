#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from . import QT_API
from .QtGui import QFileDialog


# A mapping from the Enaml dialog modes to the name of the static method
# on QFileDialog which will launch the appropriate native dialog.
if QT_API == 'pyqt':
    _STATIC_METHOD_NAMES = {
        'open_file': 'getOpenFileNameAndFilter',
        'open_files': 'getOpenFileNamesAndFilter',
        'save_file': 'getSaveFileNameAndFilter',
        'directory': 'getExistingDirectory',
    }
else:
    _STATIC_METHOD_NAMES = {
        'open_file': 'getOpenFileName',
        'open_files': 'getOpenFileNames',
        'save_file': 'getSaveFileName',
        'directory': 'getExistingDirectory',
    }


def get_file_dialog_exec_func(mode):
    """ Get the appropriate static method for exec'ing a QFileDialog.

    Parameters
    ----------
    mode : str
        The target dialog mode. Must be one of: 'open_file',
        'open_files', 'save_file', or 'directory'.

    """
    if mode not in _STATIC_METHOD_NAMES:
        raise ValueError("Unknown file dialog mode: '%s'" % mode)
    return getattr(QFileDialog, _STATIC_METHOD_NAMES[mode])
