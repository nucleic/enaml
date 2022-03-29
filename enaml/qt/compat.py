# ------------------------------------------------------------------------------
# Copyright (c) 2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ------------------------------------------------------------------------------
from qtpy.QtCore import QEvent

from . import QT_API, PYQT6_API, QT_VERSION

def coerce_to_qevent_type(event_value):
    if QT_API in PYQT6_API:
        return event_value
    return QEvent.Type(event_value)


def global_pos_from_event(event):
    if QT_VERSION[0] == "6":
        return event.globalPosition().toPoint()
    else:
        return event.globalPos()
