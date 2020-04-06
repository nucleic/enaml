#------------------------------------------------------------------------------
# Copyright (c) 2020, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
"""Test the focus tracker capabilities.

"""
import os

import pytest

from utils import is_qt_available, compile_source, wait_for_window_displayed


SOURCE ="""
from enaml.widgets.api import Window, Field, Container, Feature, FocusTracker


enamldef Main(Window):
    title = 'Focus Tracker'

    alias tracker
    alias f1
    alias f2
    alias f3
    alias f4

    FocusTracker: tracker:
        pass

    Container:
        Field: f1:
            pass
        Field: f2:
            pass
        Field: f3:
            pass
        Field: f4:
            pass

"""

@pytest.mark.skipif("TRAVIS" in os.environ, reason='Skip on Travis')
@pytest.mark.skipif(not is_qt_available(), reason='Requires a Qt binding')
def test_focus_tracking(enaml_qtbot, enaml_sleep):
    """Test moving the focus forward in the presence of a custom focus traversal.

    """
    from enaml.qt import QtCore

    win = compile_source(SOURCE, 'Main')()
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)

    enaml_qtbot.mouseClick(win.f1.proxy.widget, QtCore.Qt.LeftButton)
    assert win.tracker.focused_widget is win.f1

    for w in (win.f2, win.f3, win.f4, win.f1):
        enaml_qtbot.keyClick(win.proxy.widget, QtCore.Qt.Key_Tab)
        assert win.tracker.focused_widget is w

    for w in (win.f4, win.f3, win.f2, win.f1):
        enaml_qtbot.keyClick(
            win.tracker.focused_widget.proxy.widget,
            QtCore.Qt.Key_Tab,
            QtCore.Qt.ShiftModifier
        )
        assert win.tracker.focused_widget is w
