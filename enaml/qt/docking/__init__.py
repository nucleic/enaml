#------------------------------------------------------------------------------
# Copyright (c) 2013-2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from .. import QT_VERSION


if QT_VERSION[0] == "6":
    def hover_event_pos(event):
        return event.position().toPoint()
else:
    def hover_event_pos(event):
        return event.pos()
