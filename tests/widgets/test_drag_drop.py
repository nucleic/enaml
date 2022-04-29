# ------------------------------------------------------------------------------
# Copyright (c) 2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ------------------------------------------------------------------------------
"""Test the drag drop feature.

Qt block the event loop while dragging making it impossible to assert transient
states during the drag. (at least on Windows)

"""
import threading

from utils import compile_source, wait_for_window_displayed


SOURCE = """
from enaml.drag_drop import DragData, DropAction
from enaml.layout.api import hbox, vbox
from enaml.widgets.api import Container, Feature, Label, MultilineField, Window


def create_drag_data(dtype, data):
    drag = DragData()
    drag.supported_actions = DropAction.Copy
    drag.mime_data.set_data(dtype, data)
    return drag


enamldef DragLabel(Label):
    attr dtype: str
    attr data: bytes
    attr dragging: bool = False
    attr success = False
    style_class << 'success' if success else 'fail'
    features = Feature.DragEnabled
    drag_start => ():
        print("start")
        self.dragging = True
        return create_drag_data(dtype, data)
    drag_end => (drag_data, result):
        print("end", result)
        self.dragging = False
        self.success = result == DropAction.Copy


enamldef DropField(MultilineField):
    attr dtype: str
    attr awaiting_drop: bool = False
    features = Feature.DropEnabled
    drag_enter => (event):
        print("enter")
        if event.mime_data().has_format(dtype):
            self.awaiting_drop = True
            event.accept_proposed_action()
    drag_leave => ():
        print("leave")
        self.awaiting_drop = False
    drop => (event):
        print("dropped")
        self.awaiting_drop = False
        self.text = event.mime_data().data(dtype).decode('utf-8')
        event.accept()


enamldef Main(Window):

    alias s1: lbl1
    alias s2: lbl2
    alias dt: target
    always_on_top = True

    Container:
        constraints = [
            hbox(vbox(lbl1, lbl2), target),
        ]
        DragLabel: lbl1:
            text = 'Drag Me 1'
            dtype = "text"
            data = b"1"
        DragLabel: lbl2:
            text = 'Drag Me 2'
            dtype = "fake"
            data = b"2"
        DropField: target:
            dtype = "text"
            hug_width = 'strong'
            read_only = True

"""


def test_valid_drop(enaml_qtbot, enaml_sleep, capsys):
    """Test performing a drag and drop operation."""
    win = compile_source(SOURCE, "Main")()
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)

    # Perform the drag (Qt block the event till the drag end which is why
    # we use a thread.)
    def perform_drag():

        enaml_qtbot.move_to_and_press(enaml_qtbot.get_global_pos(win.s1), "left")

        # Enter drop target
        enaml_qtbot.move_to(
            enaml_qtbot.get_global_pos(win.dt), button="left",
        )

        # Drop
        enaml_qtbot.release_mouse("left")

    t = threading.Thread(target=perform_drag)
    t.start()
    enaml_qtbot.wait_until(lambda: not t.is_alive())

    enaml_qtbot.wait_until(lambda: win.dt.text == "1")
    steps = iter(["start", "enter", "dropped", "end", "__xxx__"])
    step = next(steps)
    for line in capsys.readouterr().out.split("\n"):
        if step in line:
            step = next(steps)
    assert step == "__xxx__"
    assert win.dt.text == "1"
    assert not win.dt.awaiting_drop
    assert win.s1.success
    assert not win.s1.dragging


def test_drag_leave(enaml_qtbot, enaml_sleep, capsys):
    """Test leaving a drop target after entering it."""
    win = compile_source(SOURCE, "Main")()
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)
    win.s1.success = True

    # Perform the drag (Qt block the event till the drag end which is why
    # we use a thread.)
    def perform_drag():

        enaml_qtbot.move_to_and_press(enaml_qtbot.get_global_pos(win.s1), "left")

        # Enter drop target
        enaml_qtbot.move_to(
            enaml_qtbot.get_global_pos(win.dt), button="left",
        )

        # Leave drop target
        enaml_qtbot.move_to(
            enaml_qtbot.get_global_pos(win.s2), button="left",
        )

        # Abort drag
        enaml_qtbot.release_mouse("left")

    t = threading.Thread(target=perform_drag)
    t.start()
    enaml_qtbot.wait_until(lambda: not t.is_alive())

    enaml_qtbot.wait_until(lambda: not win.s1.success)
    # For some reason I cannot get the enter and leave events in auto testing
    steps = iter(["start", "end", "__xxx__"])
    step = next(steps)
    out = capsys.readouterr().out.split("\n")
    for line in out:
        if step in line:
            step = next(steps)
    assert step == "__xxx__"
    assert win.dt.text == ""
