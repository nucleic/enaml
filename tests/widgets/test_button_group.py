#------------------------------------------------------------------------------
# Copyright (c) 2019, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
"""Test the button group widget.

"""
import pytest

from utils import is_qt_available, compile_source, wait_for_window_displayed


SOURCE ="""
from enaml.widgets.api import RadioButton, ButtonGroup, Container, Window

enamldef Main(Window):

    alias rad1: rd1
    alias rad2: rd2
    alias rad3: rd3
    alias rad4: rd4
    alias rad5: rd5
    alias rad6: rd6
    alias group1: gr1
    alias group2: gr2

    ButtonGroup: gr1:
        exclusive = True
    ButtonGroup: gr2:
        exclusive = False
    Container:
        Container:
            RadioButton: rd1:
                group = gr1
                checked = True
            RadioButton: rd2:
                group = gr2
                checked = True
        Container:
            RadioButton: rd3:
                group = gr1
            RadioButton: rd4:
                group = gr2
        Container:
            RadioButton: rd5:
                checked = False
            RadioButton: rd6:
                checked = False

"""


def test_tracking_group_members():
    """Test that we track properly which buttons belongs to a group.

    """
    win = compile_source(SOURCE, 'Main')()
    assert win.group1.group_members == set((win.rad1, win.rad3))
    assert win.group2.group_members == set((win.rad2, win.rad4))

    win.rad5.group = win.group1
    assert win.group1.group_members == set((win.rad1, win.rad3, win.rad5))

    win.rad5.group = win.group2
    assert win.group1.group_members == set((win.rad1, win.rad3))
    assert win.group2.group_members == set((win.rad2, win.rad4, win.rad5))

    win.rad5.group = None
    assert win.group2.group_members == set((win.rad2, win.rad4))


@pytest.mark.skipif(not is_qt_available(), reason='Requires a Qt binding')
def test_group_exclusivity(enaml_qtbot, enaml_sleep):
    """Test that we properly enforce exclusivity within a group.

    """
    win = compile_source(SOURCE, 'Main')()
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)

    # Check that group 1 is exclusive
    win.rad3.checked = True
    enaml_qtbot.wait(enaml_sleep)
    assert win.rad3.checked is True
    assert win.rad1.checked is False

    # Check that group 2 is non-exclusive
    win.rad4.checked = True
    enaml_qtbot.wait(enaml_sleep)
    assert win.rad2.checked is True
    assert win.rad4.checked is True

    # Check that dynamically added members are part of the right group
    win.rad5.group = win.group1
    assert win.rad3.checked is True
    assert win.rad1.checked is False
    assert win.rad5.checked is False
    win.rad5.checked = True
    enaml_qtbot.wait(enaml_sleep)
    assert win.rad3.checked is False
    assert win.rad1.checked is False
    assert win.rad5.checked is True
