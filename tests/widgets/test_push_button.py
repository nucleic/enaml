# -----------------------------------------------------------------------------
# Copyright (c) 2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test the behavior of the push button.

"""
from utils import compile_source, wait_for_window_displayed


SOURCE = """
from enaml.widgets.api import Container, PushButton, Window

enamldef Main(Window): w:

    attr clicked: bool = False
    alias button: pb

    Container:
        PushButton: pb:
            text = "Click me"
            clicked ::
                w.clicked = True

"""


def test_push_button(enaml_qtbot, enaml_sleep):
    """Check we can click on a push button."""
    win = compile_source(SOURCE, "Main")()
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)

    from enaml.qt import QtCore
    # Click the button
    enaml_qtbot.mouseClick(win.button.proxy.widget, QtCore.Qt.LeftButton)

    enaml_qtbot.wait_until(lambda: win.clicked)
