# ------------------------------------------------------------------------------
# Copyright (c) 2022-2024, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ------------------------------------------------------------------------------
from . import QT_VERSION


if QT_VERSION[0] == '6':
    def global_pos_from_event(event):
        return event.globalPosition().toPoint()

    def mouse_event_pos(event):
        return event.position().toPoint()
else:
    def global_pos_from_event(event):
        return event.globalPos()

    def mouse_event_pos(event):
        return event.pos()
