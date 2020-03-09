#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import pytest
from utils import compile_source, wait_for_window_displayed,is_qt_available

pytestmark = pytest.mark.skipif(not is_qt_available(),
                                reason='Requires a Qt binding')

MANUAL_REPARENTING = \
"""from enaml.core.api import Conditional
from enaml.widgets.api import (Window, Container, ObjectCombo, PushButton,
                               ScrollArea, GroupBox, Label)


enamldef Displayable(GroupBox): cont:

    attr sp_children = []
    alias btn_clicked : btn.clicked

    func refresh():
        for c in sp_children:
            c.set_parent(self)
            c.show()

    initialized ::
        refresh()

    PushButton: btn:
        text = 'Add label'
        clicked ::
            Label(text='Dummy').set_parent(cont)

C2 = Displayable(title='C2')

C1 = Displayable(title='C1', sp_children=[C2])


enamldef Main(Window):

    attr displayables = {'C1': C1, 'C2': C2}
    alias selected_disp : cb.selected

    initialized::
        C1.set_parent(scroll)
        C1.show()

    Container:
        ObjectCombo: cb:
            items = sorted(displayables)
            selected ::
                view = displayables[change['value']]
                view.set_parent(scroll)
                view.refresh()
                view.show()

        ScrollArea: scroll:
            pass
"""


def test_manual_reparenting(enaml_qtbot):
    """Test manually reparenting widgets which are previously child and parent.

    """
    win = compile_source(MANUAL_REPARENTING, 'Main')()
    win.show()
    win.send_to_front()
    wait_for_window_displayed(enaml_qtbot, win)
    win.selected_disp = 'C2'
    win.displayables['C2'].btn_clicked = True
