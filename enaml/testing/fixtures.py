#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
"""Pytest fixtures.

"""
from traceback import format_exc
import pytest

from .utils import close_all_windows, close_all_popups

#: Global variable linked to the --ecpy-sleep cmd line option.
DIALOG_SLEEP = 0

pytest_plugins = (str('pytest_catchlog'), str('pytest-qt'))


def pytest_addoption(parser):
    """Add command line options.

    """
    parser.addoption("--enaml-sleep", action='store', type=float,
                     help="Time to sleep after handling a ui event")


def pytest_configure(config):
    """Turn the --enaml-sleep command line into a global variable.

    """
    s = config.getoption('--enaml-sleep')
    if s is not None:
        global DIALOG_SLEEP
        DIALOG_SLEEP = s


@pytest.fixture
def enaml_sleep():
    """Return the time to sleep as set by the --enaml-sleep option.

    """
    return DIALOG_SLEEP


@pytest.yield_fixture(scope='session')
def qt_app():
    """Make sure a QtApplication is active.

    """
    try:
        from enaml.qt.qt_application import QtApplication
    except ImportError:
        pytest.skip('No Qt binding found: %s' % format_exc())

    app = QtApplication.instance()
    if app is None:
        app = QtApplication()
        yield app
        app.stop()
    else:
        yield app


@pytest.yield_fixture
def enaml_qtbot(qt_app, qtbot):
    qtbot.enaml_app = qt_app
    with close_all_windows(qtbot), close_all_popups(qtbot):
        yield qtbot
