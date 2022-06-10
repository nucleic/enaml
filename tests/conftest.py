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

from enaml.application import Application
from enaml.widgets.api import Window
from enaml.widgets.widget import Widget

from utils import wait_for_window_displayed, close_window_or_popup

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


import pytest
from utils import close_all_windows, close_all_popups

#: Global variable linked to the --enaml-sleep cmd line option.
DIALOG_SLEEP = 0


def pytest_addoption(parser):
    """Add command line options."""
    parser.addoption(
        "--enaml-sleep",
        action="store",
        type=int,
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

    qtbot.enaml_app = qt_app
    pixel_ratio = QtGui.QGuiApplication.primaryScreen().devicePixelRatio()

    def get_global_pos(widget: Widget) -> QtCore.QPoint:
        assert widget.proxy
        qw = widget.proxy.widget
        # Take into account the pixel ratio so that PyQt and PyAutoGUI agree on
        # the coordinates
        return qw.mapToGlobal(qw.rect().center()) * pixel_ratio

    qtbot.get_global_pos = get_global_pos

    def post_event(widget, event):
        qt_app._qapp.postEvent(widget, event)

    qtbot.post_event = post_event

    with close_all_windows(qtbot), close_all_popups(qtbot):
        yield qtbot


@pytest.fixture
def enaml_run(enaml_qtbot, monkeypatch):
    """Patches the QtApplication to allow using the qtbot when the
    enaml application is started. It also patches QApplication.exit as
    recommended in the pytest-qt docs.

    Yields
    -------
    handler: object
        an object with a `run` attribute that can be set to a callback that
        will be invoked with the application and first window shown.

    References
    ----------
    1. https://pytest-qt.readthedocs.io/en/latest/app_exit.html

    """
    from enaml.qt.qt_application import QtApplication, QApplication

    app = Application.instance()
    if app:
        Application._instance = None

    class Runner:
        # Set this to a callback
        run = None

    runner = Runner()

    def start(self):
        for window in Window.windows:
            wait_for_window_displayed(enaml_qtbot, window)
            if callable(runner.run):
                runner.run(self, window)
            else:
                close_window_or_popup(enaml_qtbot, window)
            break

    try:
        with monkeypatch.context() as m:
            m.setattr(QtApplication, "start", start)
            m.setattr(QApplication, "exit", lambda self: None)
            yield runner
    finally:
        Application._instance = app
