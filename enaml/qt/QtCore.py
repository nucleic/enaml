#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from . import QT_API 


if QT_API == 'pyqt':
    from PyQt4.QtCore import *
    Property = pyqtProperty
    Signal = pyqtSignal
    Slot = pyqtSlot
    QDateTime.toPython = QDateTime.__dict__['toPyDateTime']
    QDate.toPython = QDate.__dict__['toPyDate']
    QTime.toPython = QTime.__dict__['toPyTime']
    __version__ = QT_VERSION_STR
    __version_info__ = tuple(map(int, QT_VERSION_STR.split('.')))
    # Remove the input hook or pdb.set_trace() will infinitely recurse
    pyqtRemoveInputHook()
else:
    from PySide import __version__, __version_info__
    from PySide.QtCore import *
