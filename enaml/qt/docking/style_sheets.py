#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from future.builtins import str

#: The global dict of registered stylesheets. This dict should never be
#: modified directly. Use the functions 'register_style_sheet' and
#: 'get_style_sheet' instead.
_style_sheets = {}


def get_style_sheet(name):
    """ This is a deprecated function.

    """
    return _style_sheets.get(name, u'')


def register_style_sheet(name, sheet):
    """ This is a deprecated function.

    """
    import warnings
    msg = "Toolkit specific styling for the DockArea is deprecated "
    msg += "and will be removed in Enaml version 1.0. Use stylesheets "
    msg += "to style the Dock Area instead."
    warnings.warn(msg, FutureWarning, stacklevel=2)

    assert isinstance(sheet, str), 'style sheet must be a string'
    if name in _style_sheets:
        raise ValueError("'%s' style is already registered" % name)
    _style_sheets[name] = sheet
