#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
"""Generic utility functions for testing.

"""
import os
import sys
from contextlib import contextmanager

from atom.api import Atom, Bool

import enaml
from enaml.application import timed_call
from enaml.core.enaml_compiler import EnamlCompiler
from enaml.core.parser import parse
from enaml.widgets.api import Window, Dialog, PopupView
with enaml.imports():
    from enaml.stdlib.message_box import MessageBox

# Timeout for qtbot wait (the value used is large due to Travis being sometimes
# very slow).
TIMEOUT = 2000


def compile_source(source, item, filename='<test>', namespace=None):
    """ Compile Enaml source code and return the target item.

    Parameters
    ----------
    source : str
        The Enaml source code string to compile.

    item : str
        The name of the item in the resulting namespace to return.

    filename : str, optional
        The filename to use when compiling the code. The default
        is '<test>'.

    namespace : dict
        Namespace in which to execute the code

    Returns
    -------
    result : object
        The named object from the resulting namespace.

    """
    ast = parse(source, filename)
    code = EnamlCompiler.compile(ast, filename)
    namespace = namespace or {}
    exec(code, namespace)
    return namespace[item]


def run_pending_tasks(qtbot, timeout=1000):
    """Run all enaml pending tasks.

    WARNING: this may not run the Qt event loop if no task is pending.
    This will only deal with tasks scheduled through the schedule function
    (or Application method)

    Parameters
    ----------
    timeout : int, optional
        Timeout after which the operation should fail in ms

    """
    def check_pending_tasks():
        assert not qtbot.enaml_app.has_pending_tasks()
    qtbot.wait_until(check_pending_tasks, timeout=TIMEOUT)


def get_window(qtbot, cls=Window, timeout=1000):
    """Convenience function running the event loop and returning the first
    window found in the set of active windows.

    Parameters
    ----------
    cls : type, optional
        Type of the window which should be returned.

    timeout : int, optional
        Timeout after which the operation should fail in ms

    Returns
    -------
    window : Window or None
        Return the first window found matching the specified class

    Raises
    ------
    AssertionError : raised if no window is found in the given time

    """
    def check_window_presence():
        assert [w for w in Window.windows if isinstance(w, cls)]

    qtbot.wait_until(check_window_presence, timeout=TIMEOUT)
    for w in Window.windows:
        if isinstance(w, cls):
            return w


def get_popup(qtbot, cls=PopupView, timeout=1000):
    """Convenience function running the event loop and returning the first
    popup found in the set of active popups.

    Parameters
    ----------
    cls : type, optional
        Type of the window which should be returned.

    timeout : int, optional
        Timeout after which the operation should fail in ms

    Returns
    -------
    popup : PopupView or None
        Return the first window found matching the specified class

    Raises
    ------
    AssertionError : raised if no popup is found in the given time

    """
    def check_popup_presence():
        assert [p for p in PopupView.popup_views if isinstance(p, cls)]

    qtbot.wait_until(check_popup_presence, timeout=TIMEOUT)
    for p in PopupView.popup_views:
        if isinstance(p, cls):
            return p


def wait_for_window_displayed(qtbot, window, timeout=1000):
    """Wait for a window to be displayed.

    This method should be called on already activated windows (the show method
    should have been called).

    """
    if not window.proxy_is_active or not window.proxy.widget:
        msg = 'Window must be activated before waiting for display'
        raise RuntimeError(msg)
    qtbot.wait_exposed(window.proxy.widget, timeout=timeout)


class EventObserver(Atom):
    """Simple observer registering the fact it was called once.

    """
    called = Bool()

    def callback(self, change):
        self.called = True

    def assert_called(self):
        assert self.called


def wait_for_destruction(qtbot, widget):
    """Wait for a widget to get destroyed.

    """
    if widget.is_destroyed:
        return
    obs = EventObserver()
    widget.observe('destroyed', obs.callback)
    qtbot.wait_until(obs.assert_called, timeout=TIMEOUT)


def close_window_or_popup(qtbot, window_or_popup):
    """Close a window/popup and run the event loop to make sure the closing
    complete.

    """
    if window_or_popup.is_destroyed:
        return
    obs = EventObserver()
    window_or_popup.observe('destroyed', obs.callback)
    window_or_popup.close()
    qtbot.wait_until(obs.assert_called, timeout=TIMEOUT)


@contextmanager
def close_all_windows(qtbot):
    """Close all opened windows.

    """
    yield
    run_pending_tasks(qtbot)
    while Window.windows:
        windows = list(Window.windows)
        # First close non top level windows to avoid a window to lose its
        # parent and not remove itself from the set of windows.
        non_top_level_windows = [w for w in windows if w.parent is not None]
        for window in non_top_level_windows:
            close_window_or_popup(qtbot, window)
        for window in windows:
            close_window_or_popup(qtbot, window)


@contextmanager
def close_all_popups(qtbot):
    """Close all opened popups.

    """
    yield
    run_pending_tasks(qtbot)
    while PopupView.popup_views:
        popups = list(PopupView.popup_views)
        # First close non top level popups to avoid a up/window to lose its
        # parent and not remove itself from the set of windows.
        non_top_level_popups = [p for p in popups if p.parent is not None]
        for popup in non_top_level_popups:
            close_window_or_popup(qtbot, popup)
        for popup in popups:
            close_window_or_popup(qtbot, popup)


class ScheduledClosing(object):
    """Scheduled closing of dialog.

    """

    def __init__(self, bot, cls, handler, op, skip_answer):
        self.cls = cls
        self.handler = handler
        self.op = op
        self.bot = bot
        self.skip_answer = skip_answer
        self.called = False

    def __call__(self):
        self.called = True
        from conftest import DIALOG_SLEEP
        dial = get_window(self.bot, cls=self.cls)
        wait_for_window_displayed(self.bot, dial)
        self.bot.wait(DIALOG_SLEEP*1000)
        obs = EventObserver()
        dial.observe('finished', obs.callback)

        try:
            self.handler(self.bot, dial)
        finally:
            if not self.skip_answer:
                getattr(dial, self.op)()
            self.bot.wait_until(obs.assert_called, timeout=TIMEOUT)

    def was_called(self):
        """Assert the scheduler was called.

        """
        assert self.called


@contextmanager
def handle_dialog(qtbot, op='accept', handler=lambda qtbot, window: window,
                  cls=Dialog, time=100, skip_answer=False):
    """Automatically close a dialog opened during the context.

    Parameters
    ----------
    op : {'accept', 'reject'}, optional
        Whether to accept or reject the dialog.

    handler : callable, optional
        Callable taking as arguments the bot and the dialog, called before
        accepting or rejecting the dialog.

    cls : type, optional
        Dialog class to identify.

    time : float, optional
        Time to wait before handling the dialog in ms.

    skip_answer : bool, optional
        Skip answering to the dialog. If this is True the handler should handle
        the answer itself.

    """
    sch = ScheduledClosing(qtbot, cls, handler, op, skip_answer)
    timed_call(time, sch)
    try:
        yield
    except Exception:
        raise
    else:
        qtbot.wait_until(sch.was_called, timeout=TIMEOUT)


@contextmanager
def handle_question(app, answer):
    """Handle question dialog.

    """
    def answer_question(app, dial):
        """Mark the right button as clicked.

        """
        dial.buttons[0 if answer == 'yes' else 1].was_clicked = True

    with handle_dialog(app, 'accept' if answer == 'yes' else 'reject',
                       handler=answer_question, cls=MessageBox):
        yield


@contextmanager
def cd(path, add_to_sys_path=False):
    """ cd to the directory then return to the cwd

    """
    cwd = os.getcwd()
    if add_to_sys_path:
        abspath = os.path.abspath(path)
        sys.path.append(abspath)
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)
        if add_to_sys_path:
            sys.path.remove(abspath)
