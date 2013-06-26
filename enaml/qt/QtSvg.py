#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from . import QT_API


if QT_API == 'pyqt':
    from PyQt4.QtSvg import *
else:
    from PySide.QtSvg import *
