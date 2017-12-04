# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import pytest

from enaml.layout.api import HSplitLayout, DockLayoutWarning
from enaml.widgets.api import DockArea, DockItem

from utils import compile_source, wait_for_window_displayed

DOCK_AREA_TEMPLATE =\
"""from enaml.widgets.api import Window, Container, DockArea, DockItem
from enaml.layout.api import VSplitLayout

enamldef Main(Window):

    alias area: dock_area

    Container:
        DockArea: dock_area:
            layout = VSplitLayout('item1', 'item2')

            DockItem:
                name = 'item1'
            DockItem:
                name = 'item2'

"""


@pytest.mark.filterwarnings('error')
def test_validation_dock_layout1(enaml_qtbot, enaml_sleep):
    """Test that the validation of a layout.

    We check in particular that the proper warnings are raised and that doing
    so does not corrupt the globals.

    """
    win = compile_source(DOCK_AREA_TEMPLATE, 'Main')()
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)
    enaml_qtbot.wait(enaml_sleep)
    win.area.layout = HSplitLayout('item1', 'item2')
    enaml_qtbot.wait(enaml_sleep)


def test_validation_dock_layout2(enaml_qtbot, enaml_sleep):
    """Test that the validation of a layout.

    We check in particular that the proper warnings are raised and that doing
    so does not corrupt the globals.

    """
    win = compile_source(DOCK_AREA_TEMPLATE, 'Main')()
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)
    enaml_qtbot.wait(enaml_sleep)
    glob = globals().copy()
    with pytest.warns(DockLayoutWarning):
        win.area.layout = HSplitLayout('item1', 'item2', 'item3')
    assert globals() == glob
    enaml_qtbot.wait(enaml_sleep)
