# ------------------------------------------------------------------------------
# Copyright (c) 2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ------------------------------------------------------------------------------
from qtpy.QtCore import QEvent

from . import QT_API, PYQT6_API, QT_VERSION


if QT_VERSION[0] == '6':
    def global_pos_from_event(event):
        return event.globalPosition().toPoint()
else:
    def global_pos_from_event(event):
        return event.globalPos()
