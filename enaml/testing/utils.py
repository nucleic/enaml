#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
"""Generic utility functions for testing.

"""
from time import sleep
from contextlib import contextmanager

import enaml
from ..application import timed_call
from ..widgets.api import Window, Dialog, PopupView
with enaml.imports():
    from ..stdlib.message_box import MessageBox


def get_window(app, cls=Window):
    """Convenience function running the event loop and returning the first
    window found in the set of active windows.

    Parameters
    ----------
    cls : type, optional
        Type of the window which should be returned.

    Returns
    -------
    window : Window or None
        Return the first window found matching the specified class or None if
        no window was found

    """
    app.process_events()
    for w in Window.windows:
        if isinstance(w, cls):
            return w
    for w in PopupView.popup_views:
        if isinstance(w, cls):
            return w


@contextmanager
def close_all_windows(app):
    """Close all opened windows.

    This should be used by all tests creating windows in a teardown step.

    """
    yield
    app.process_events()
    sleep(0.1)
    while Window.windows:
        windows = list(Window.windows)
        # First close non top level windows to avoid a window/popup to lose its
        # parent and not remove itself from the set of windows.
        non_top_level_windows = [w for w in windows if w.parent is not None]
        for window in non_top_level_windows:
            window.close()
        app.process_events()
        for window in windows:
            window.close()
        app.process_events()
        sleep(0.02)


@contextmanager
def close_all_popups(app):
    """Close all opened popups.

    """
    yield
    app.process_events()
    sleep(0.1)
    while PopupView.popup_views:
        popups = list(PopupView.popup_views)
        # First close non top level popups to avoid a up/window to lose its
        # parent and not remove itself from the set of windows.
        non_top_level_popups = [p for p in popups if p.parent is not None]
        for popup in non_top_level_popups:
            popup.close()
        app.process_events()
        for popup in popups:
            popup.close()
        app.process_events()
        sleep(0.02)
        app.process_events()


class ScheduledClosing(object):
    """Scheduled closing of dialog.

    """

    def __init__(self, app, cls, handler, op, skip_answer):
        self.called = False
        self.cls = cls
        self.handler = handler
        self.op = op
        self.app = app
        self.skip_answer = skip_answer

    def __call__(self):
        i = 0
        while True:
            dial = get_window(self.app, self.cls)
            if dial is not None:
                break
            elif i > 10:
                raise Exception('Dialog timeout')
            sleep(0.1)
            i += 1

        try:
            self.handler(self.app, dial)
        finally:
            self.app.process_events()
            from .fixtures import DIALOG_SLEEP
            sleep(DIALOG_SLEEP)
            if not self.skip_answer:
                getattr(dial, self.op)()
            self.app.process_events()
            self.called = True


@contextmanager
def handle_dialog(app, op='accept', handler=lambda app, window: window,
                  cls=Dialog, time=100, skip_answer=False):
    """Automatically close a dialog opened during the context.

    Parameters
    ----------
    op : {'accept', 'reject'}, optional
        Whether to accept or reject the dialog.

    handler : callable, optional
        Callable taking as only argument the dialog, called before accepting
        or rejecting the dialog.

    cls : type, optional
        Dialog class to identify.

    time : float, optional
        Time to wait before handling the dialog in ms.

    skip_answer : bool, optional
        Skip answering to the dialog. If this is True the handler should handle
        the answer itself.

    """
    sch = ScheduledClosing(app, cls, handler, op, skip_answer)
    timed_call(time, sch)
    try:
        yield
    except Exception:
        raise
    else:
        while not sch.called:
            app.process_events()


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
