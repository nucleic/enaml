#------------------------------------------------------------------------------
# Copyright (c) 2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
"""Test the re-ordering of the Notebook tabs."""
import random

from utils import compile_source, wait_for_window_displayed


SOURCE = """
from enaml.widgets.api import MainWindow, Container, PushButton, Notebook, Label, Page
from enaml.core.api import Looper

enamldef Main(MainWindow): mw:

    attr tabs = ["Tab 1", "Tab 2", "Tab 3", "Tab 4"]
    alias notebook: nb

    Container:
        Looper:
            iterable << mw.tabs
            Label:
                text << loop.item

        Notebook: nb:
            Looper:
                iterable << mw.tabs
                Page:
                    closable = False
                    title << loop.item
                    name << loop.item
                    Container:
                        Label:
                            text << loop.item
"""


def get_qt_tab_order(qt_notebook):
    # Assumes QTabWidget-like API
    return [qt_notebook.tabText(i) for i in range(qt_notebook.count())]

def test_tab_order_matches_declaration_after_reorder(enaml_qtbot, enaml_sleep):

    win = compile_source(SOURCE, "Main")()
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)

    assert win.tabs == get_qt_tab_order(win.notebook.proxy.widget)

    new_order = random.sample(win.tabs, len(win.tabs))
    win.tabs = new_order
    enaml_qtbot.wait(enaml_sleep)

    assert win.tabs == get_qt_tab_order(win.notebook.proxy.widget)
