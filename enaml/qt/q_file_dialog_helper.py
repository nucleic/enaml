#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from qtpy.compat import (getexistingdirectory, getopenfilename,
                         getopenfilenames, getsavefilename)


# A mapping from the Enaml dialog modes to the name of the qtpy compatibility
# function which will launch the appropriate native dialog.
_STATIC_METHOD_NAMES = {
    'open_file': getopenfilename,
    'open_files': getopenfilenames,
    'save_file': getsavefilename,
    'directory': getexistingdirectory,
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
    return _STATIC_METHOD_NAMES[mode]
