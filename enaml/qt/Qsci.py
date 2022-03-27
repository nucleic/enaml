#------------------------------------------------------------------------------
# Copyright (c) 2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from . import QT_API, PYSIDE2_API, PYQT5_API, PYQT6_API

if QT_API in PYSIDE2_API:
    msg = 'the Qt Scintilla widget is only available when using PyQt'
    raise ImportError(msg)

if QT_API in PYQT6_API:
    from PyQt6.Qsci import *
elif QT_API in PYQT5_API:
    from PyQt5.Qsci import *
else:
    from QScintilla import *
