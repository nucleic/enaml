#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from wx.lib.newevent import NewCommandEvent


#: A custom command event that can be posted to request a layout
#: when a widget's geometry has changed. On Qt, this type of event
#: is posted and handled automatically. This fills that gap.
wxEvtLayoutRequested, EVT_COMMAND_LAYOUT_REQUESTED = NewCommandEvent()
