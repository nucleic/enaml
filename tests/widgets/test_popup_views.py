# -----------------------------------------------------------------------------
# Copyright (c) 2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test the behavior of the popup views.

"""
import pytest

from utils import compile_source, wait_for_window_displayed


SOURCE = """
from enaml.widgets.api import Container, Label, PopupView, PushButton, Window

enamldef Popup(PopupView):
    attr clicked = False
    closed ::
        self.clicked = True
    Container:
        Label:
            text = "Hi !"

enamldef Main(Window): w:

    attr window_type
    attr popup = None
    alias button: pb

    Container:
        PushButton: pb:
            text = "Click me"
            clicked ::
                w.popup = Popup(window_type=w.window_type)
                w.popup.show()

"""


@pytest.mark.parametrize("window_type", ["window", "tool_tip", "popup"])
def test_popup_view(enaml_qtbot, enaml_sleep, window_type):
    """Check we can click on a push button."""
    win = compile_source(SOURCE, "Main")(window_type=window_type)
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)

    from enaml.qt import QtCore

    # Click the button and wait for the popup
    enaml_qtbot.mouseClick(win.button.proxy.widget, QtCore.Qt.LeftButton)
    enaml_qtbot.wait_until(lambda: win.popup is not None)
    enaml_qtbot.wait_exposed(win.popup.proxy.widget)

    enaml_qtbot.wait(enaml_sleep)

    # Click to close the popup
    if window_type == "popup":  # click outside
        enaml_qtbot.mousePress(
            win.popup.proxy.widget, QtCore.Qt.LeftButton, pos=QtCore.QPoint(-1, -1)
        )
    else:
        enaml_qtbot.mousePress(win.popup.proxy.widget, QtCore.Qt.LeftButton)

    enaml_qtbot.wait_until(lambda: win.popup.clicked)
