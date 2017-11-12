#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from qtpy import QT_VERSION
from . import QT_API, PYQT4_API, PYQT5_API

__version__ = QT_VERSION
__version_info__ = tuple(map(int, QT_VERSION.split('.')))
from qtpy.QtCore import *

if QT_API in PYQT4_API or QT_API in PYQT5_API:
    QDateTime.toPython = QDateTime.__dict__['toPyDateTime']
    QDate.toPython = QDate.__dict__['toPyDate']
    QTime.toPython = QTime.__dict__['toPyTime']
    # Remove the input hook or pdb.set_trace() will infinitely recurse
    pyqtRemoveInputHook()
