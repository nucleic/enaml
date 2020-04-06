#------------------------------------------------------------------------------
# Copyright (c) 2020, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
"""Test the focus traversal functionalities

"""
import os

import pytest

from utils import is_qt_available, compile_source, wait_for_window_displayed


SOURCE ="""
from enaml.widgets.api import Window, GroupBox, Field, Container, Feature, FocusTracker


enamldef LinkField(Field):
    attr next_field
    attr prev_field


enamldef Main(Window):
    title = 'Focus Traversal'

    alias tracker
    alias f1
    alias f2
    alias f3
    alias f4
    alias f5
    alias f6
    alias f7

    FocusTracker: tracker:
        pass

    Container:
        features = Feature.FocusTraversal

        next_focus_child => (current):      # triggered on Tab
            child = getattr(current, 'next_field', None)
            return child

        previous_focus_child => (current):  # triggered on Shift+Tab
            child = getattr(current, 'prev_field', None)
            return child

        GroupBox:
            title = 'First Group'
            LinkField: f1:
                placeholder = '1'
                next_field = f4
                prev_field = f5
            LinkField: f2:
                placeholder = '5'
                next_field = f7
                prev_field = f6
            LinkField: f3:
                placeholder = '3'
                next_field = f6
                prev_field = f4
            LinkField: f4:
                placeholder = '2'
                next_field = f3
                prev_field = f1
        GroupBox:
            title = 'Second Group'
            LinkField: f5:
                placeholder = '7'
                next_field = f1
                prev_field = f7
            LinkField: f6:
                placeholder = '4'
                next_field = f2
                prev_field = f3
            LinkField: f7:
                placeholder = '6'
                next_field = f5
                prev_field = f2

"""


@pytest.mark.skipif("TRAVIS" in os.environ, reason='Skip on Travis')
@pytest.mark.skipif(not is_qt_available(), reason='Requires a Qt binding')
@pytest.mark.parametrize("widgets, mods",
                         [(["f4", "f3", "f6", "f2", "f7", "f5", "f1"], [False]*7),
                          (["f5", "f7", "f2", "f6", "f3", "f4", "f1"], [True]*7),
                          (["f4", "f1", "f5", "f7", "f5", "f1", "f4", "f3", "f4"],
                           [False, True, True, True, False, False, False, False, True]
                           )
                         ]
                        )
def test_focus_traversal(enaml_qtbot, enaml_sleep, widgets, mods):
    """Test moving the focus forward in the presence of a custom focus traversal.

    """
    from enaml.qt import QtCore

    win = compile_source(SOURCE, 'Main')()
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)

    enaml_qtbot.mouseClick(win.f1.proxy.widget, QtCore.Qt.LeftButton)
    assert win.tracker.focused_widget is win.f1

    for w, mod in zip(widgets, mods):
        # If we do not send the key press to the focused widget we can get aberrant
        # behavior, typically if we send the key press to the window the custom
        # behavior of enaml will be bypassed.
        enaml_qtbot.keyClick(
            win.tracker.focused_widget.proxy.widget,
            QtCore.Qt.Key_Tab,
            QtCore.Qt.ShiftModifier if mod else QtCore.Qt.NoModifier
        )
        assert win.tracker.focused_widget is getattr(win, w)

