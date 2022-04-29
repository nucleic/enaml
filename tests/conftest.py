# ------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ------------------------------------------------------------------------------
"""Pytest fixtures.

"""
import os
from traceback import format_exc
from typing import Literal, Union

from enaml.widgets.widget import Widget

# Make sure enaml already imported qt to avoid issues with pytest
try:
    from enaml.qt import QT_API, PYQT5_API, PYSIDE2_API, PYQT6_API, PYSIDE6_API

    if QT_API in PYQT5_API:
        os.environ.setdefault("PYTEST_QT_API", "pyqt5")
    elif QT_API in PYSIDE2_API:
        os.environ.setdefault("PYTEST_QT_API", "pyside2")
    elif QT_API in PYQT6_API:
        os.environ.setdefault("PYTEST_QT_API", "pyqt6")
    elif QT_API in PYSIDE6_API:
        os.environ.setdefault("PYTEST_QT_API", "pyside6")

    from enaml.qt import QtCore, QtGui

    pytest_plugins = (str("pytest-qt"),)
    QT_AVAILABLE = True

except Exception:
    QT_AVAILABLE = False

try:
    import pyautogui
    AUTO_AVAILABLE = True
except ImportError:
    AUTO_AVAILABLE = False


import pytest
from utils import close_all_windows, close_all_popups

#: Global variable linked to the --enaml-sleep cmd line option.
DIALOG_SLEEP = 0


def pytest_addoption(parser):
    """Add command line options."""
    parser.addoption(
        "--enaml-sleep",
        action="store",
        type=float,
        help="Time to sleep after handling a ui event",
    )


def pytest_configure(config):
    """Turn the --enaml-sleep command line into a global variable."""
    s = config.getoption("--enaml-sleep")
    if s is not None:
        global DIALOG_SLEEP
        DIALOG_SLEEP = s

@pytest.fixture
def enaml_sleep():
    """Return the time to sleep in s as set by the --enaml-sleep option."""
    return DIALOG_SLEEP


@pytest.fixture(scope="session")
def qt_app():
    """Make sure a QtApplication is active."""
    if not QT_AVAILABLE:
        pytest.skip("Requires a Qt binding")
    try:
        from enaml.qt.qt_application import QtApplication
    except Exception:
        pytest.skip("No Qt binding found: %s" % format_exc())

    app = QtApplication.instance()
    if app is None:
        app = QtApplication()
        yield app
        app.stop()
    else:
        yield app


@pytest.fixture
def enaml_qtbot(qt_app, qtbot):
    if not AUTO_AVAILABLE:
        pytest.skip("Requires pyautogui")

    qtbot.enaml_app = qt_app
    pixel_ratio = QtGui.QGuiApplication.primaryScreen().devicePixelRatio()

    # Patch the bot with extra method using pyautogui to workaround QTest limitations
    def get_global_pos(widget: Widget) -> QtCore.QPoint:
        assert widget.proxy
        qw = widget.proxy.widget
        # Take into account the pixel ratio so that PyQt and PyAutoGUI agree on
        # the coordinates
        return qw.mapToGlobal(qw.rect().center()) * pixel_ratio

    qtbot.get_global_pos = get_global_pos

    def move_to(
        destination: QtCore.QPoint,
        button: Union[None, Literal["left"], Literal["middle"], Literal["right"]],
        duration: float = 0.0,
    ):
        """Move in between two points with optionally a button pressed."""
        if button is not None:
            pyautogui.dragTo(
                destination.x(), destination.y(), duration=duration, button="left", mouseDownUp=False
            )
        else:
            pyautogui.moveTo(destination.x(), destination.y(), duration=duration)

    qtbot.move_to = move_to

    def move_to_and_press(
        origin: QtCore.QPoint,
        button: Union[Literal["left"], Literal["middle"], Literal["right"]],
    ) -> None:
        pyautogui.moveTo(origin.x(), origin.y())
        pyautogui.mouseDown(button=button)
        qtbot.wait(1)

    qtbot.move_to_and_press = move_to_and_press

    def release_mouse(
        button: Union[Literal["left"], Literal["middle"], Literal["right"]]
    ) -> None:
        pyautogui.mouseUp(button=button)
        qtbot.wait(1)

    qtbot.release_mouse = release_mouse

    def move_to_and_click(
        origin: QtCore.QPoint,
        button: Union[Literal["left"], Literal["middle"], Literal["right"]],
    ) -> None:
        pyautogui.moveTo(origin.x(), origin.y())
        pyautogui.click(button=button)
        qtbot.wait(1)

    qtbot.move_to_and_click = move_to_and_click

    with close_all_windows(qtbot), close_all_popups(qtbot):
        yield qtbot
