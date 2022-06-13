# ------------------------------------------------------------------------------
# Copyright (c) 2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ------------------------------------------------------------------------------
"""Test the drag drop feature.

Due to the the limitations of QTest (cannot keep a button pressed during move),
we split the tests between:
- starting a drag using QTest.MoveTo and testing both success drop and failed drop
  through monkeypatching of the exec_ method on QDrag. This allows to avoid issues
  with a possible blocking behavior.
- handling drag enter, leave and drop event through direct call to the relevant
  widget method.

This is not perfect but should catch most regressions.

"""
import pytest

try:
    from enaml.qt.QtCore import QEvent, QPoint, QPointF, Qt
    from enaml.qt.QtGui import (
        QDrag,
        QDragEnterEvent,
        QDragMoveEvent,
        QDragLeaveEvent,
        QDropEvent,
        QMouseEvent,
    )

    actions = [Qt.DropAction.CopyAction, Qt.DropAction.IgnoreAction]
except ImportError:
    # The enaml_qtbot will cause the tests to be skipped
    actions = []

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
    attr dragged: bool = False
    attr drag_ended: bool = False
    attr success = False
    style_class << 'success' if success else 'fail'
    features = Feature.DragEnabled
    drag_start => ():
        print("start")
        self.dragged = True
        return create_drag_data(dtype, data)
    drag_end => (drag_data, result):
        print("end", result)
        self.drag_ended = True
        self.success = result == DropAction.Copy


enamldef DropField(MultilineField):
    attr dtype: str
    attr awaiting_drop = None
    attr drag_moved = False
    features = Feature.DropEnabled
    drag_enter => (event):
        print("enter")
        if event.mime_data().has_format(dtype):
            self.awaiting_drop = True
            event.accept_proposed_action()
        else:
            self.awaiting_drop = False
    drag_move => (event):
        self.drag_moved = True
        print("move")
    drag_leave => ():
        print("leave")
        self.awaiting_drop = None
    drop => (event):
        print("dropped")
        self.awaiting_drop = None
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


@pytest.mark.parametrize("action", actions)
def test_drag_with_valid_drop(enaml_qtbot, monkeypatch, action):
    """Test performing a drag and drop operation."""
    win = compile_source(SOURCE, "Main")()
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)

    monkeypatch.setattr(QDrag, "exec_", lambda *args: action)

    enaml_qtbot.mousePress(win.s1.proxy.widget, Qt.MouseButton.LeftButton)

    # This erroneously release the button causing both the drag to start and end
    # The monkeypatch avoid blocking and dealing with always fail drop since we
    # release before entering the target.
    enaml_qtbot.post_event(
        win.s1.proxy.widget,
        QMouseEvent(
            QEvent.MouseMove,
            QPointF(-1, -1),
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier,
        ),
    )

    enaml_qtbot.wait_until(lambda: win.s1.dragged)
    enaml_qtbot.wait_until(lambda: win.s1.drag_ended)

    assert win.s1.success == (action == Qt.DropAction.CopyAction)


@pytest.mark.parametrize("origin, expected_success", [("s1", True), ("s2", False)])
def test_drag_enter(enaml_qtbot, origin, expected_success):
    """Test handling drag enter.

    We cannot rely on event posting since we do not want to call QDrag.exec which
    can block.

    """
    win = compile_source(SOURCE, "Main")()
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)

    drag_data = getattr(win, origin).drag_start()

    enter_event = QDragEnterEvent(
        QPoint(0, 0),
        Qt.DropAction(drag_data.supported_actions),
        drag_data.mime_data.q_data(),
        Qt.LeftButton,
        Qt.NoModifier,
    )

    win.dt.proxy.widget.dragEnterEvent(enter_event)
    if expected_success:
        assert enter_event.isAccepted()
        assert win.dt.awaiting_drop is True
    else:
        assert not enter_event.isAccepted()
        assert win.dt.awaiting_drop is False


def test_drag_move_and_leave(enaml_qtbot):
    """Test handling drag move and leave."""
    win = compile_source(SOURCE, "Main")()
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)

    drag_data = win.s1.drag_start()

    enter_event = QDragEnterEvent(
        QPoint(0, 0),
        Qt.DropAction(drag_data.supported_actions),
        drag_data.mime_data.q_data(),
        Qt.LeftButton,
        Qt.NoModifier,
    )
    win.dt.proxy.widget.dragEnterEvent(enter_event)
    assert win.dt.awaiting_drop is True

    move_event = QDragMoveEvent(
        QPoint(0, 0),
        Qt.DropAction(drag_data.supported_actions),
        drag_data.mime_data.q_data(),
        Qt.LeftButton,
        Qt.NoModifier,
    )
    win.dt.proxy.widget.dragMoveEvent(move_event)
    assert win.dt.drag_moved

    leave_event = QDragLeaveEvent()
    win.dt.proxy.widget.dragLeaveEvent(leave_event)
    assert win.dt.awaiting_drop is None


def test_drop(enaml_qtbot):
    """Test handling drag move and leave."""
    win = compile_source(SOURCE, "Main")()
    win.show()
    wait_for_window_displayed(enaml_qtbot, win)

    drag_data = win.s1.drag_start()

    drop_event = QDropEvent(
        QPointF(0, 0),
        Qt.DropAction(drag_data.supported_actions),
        drag_data.mime_data.q_data(),
        Qt.LeftButton,
        Qt.NoModifier,
        QEvent.Type.Drop,
    )
    win.dt.proxy.widget.dropEvent(drop_event)
    assert drop_event.isAccepted()
    assert win.dt.text == "1"
