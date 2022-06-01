#------------------------------------------------------------------------------
# Copyright (c) 2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
"""Test the date selector widget.

"""
import datetime

from utils import compile_source, wait_for_window_displayed

SOURCE = """
from enaml.drag_drop import DragData, DropAction
from enaml.layout.api import hbox, vbox
from enaml.widgets.api import Container, DateSelector, Window


enamldef Main(Window):

    alias ds: date

    Container:
        DateSelector: date:
            pass

"""


def test_date_selector(enaml_qtbot):
    win = compile_source(SOURCE, "Main")()
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)

    w = win.ds
    w.proxy.widget.setDate(datetime.date(2021, 12, 5))
    assert w.date == datetime.date(2021, 12, 5)
