#------------------------------------------------------------------------------
# Copyright (c) 2013-2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from .. import QT_VERSION


def hover_event_pos(event):
    if QT_VERSION[0] == "6":
        return event.position().toPoint()
    return event.pos()
