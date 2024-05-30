#------------------------------------------------------------------------------
# Copyright (c) 2024, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
""" Test the Dialog widget.

"""
from utils import compile_source, wait_for_window_displayed

SOURCE = """
from enaml.widgets.api import Container, Dialog, Label, MainWindow, PushButton

enamldef TestDialog(Dialog): dialog:

    title = "Test Dialog"

    Container:
        PushButton: ok_button:
            text = "Ok"
            clicked::
                dialog.accept()
        PushButton: cancel_button:
            text = "Cancel"
            clicked::
                dialog.reject()

enamldef Main(MainWindow): window:

    title = "Main Test Window"

    attr starting = 0
    attr started  = 0
    attr finished = 0
    attr accepted = 0
    attr rejected = 0

    func do_starting():
        window.starting += 1

    func do_started():
        window.started += 1

    func do_finished():
        window.finished += 1

    func do_accepted():
        window.accepted += 1

    func do_rejected():
        window.rejected += 1

    Container:

        Label:
            text = f"Starting: {window.starting}"
        
        Label:
            text = f"Started:  {window.started}"
        
        Label:
            text = f"Finished: {window.finished}"

        Label:
            text = f"Accepted: {window.accepted}"

        Label:
            text = f"Rejected: {window.rejected}"

        PushButton: async_button
            text = "Launch Dialog Asynchronously"
            clicked::
                window.do_starting()
                dialog = TestDialog(self)
                dialog.finished.bind(lambda e: window.do_finished())
                dialog.accepted.bind(lambda e: window.do_accepted())
                dialog.rejected.bind(lambda e: window.do_rejected())
                dialog.open()
                window.do_started()
"""

def test_dialog_asynchronous(enaml_qtbot):

    from enaml.qt import QtCore

    window = compile_source(SOURCE, "Main")()
    window.show()
    wait_for_window_displayed(enaml_qtbot, window)

    assert len(window.windows) == 1
    assert window.starting == 0
    assert window.started  == 0
    assert window.finished == 0
    assert window.accepted == 0
    assert window.rejected == 0

    # click the button to launch the dialog.
    enaml_qtbot.mouseClick(window.async_button.proxy.widget, QtCore.Qt.LeftButton)

    assert len(window.windows) == 2
    assert window.starting == 1
    assert window.started  == 1
    assert window.finished == 0
    assert window.accepted == 0
    assert window.rejected == 0

    # click the Ok button in the dialog.
    enaml_qtbot.mouseClick(next(otherWindow for otherWindow in window.windows if otherWindow.title == 'Test Dialog').ok_button.proxy.widget, QtCore.Qt.LeftButton)

    assert len(window.windows) == 1
    assert window.starting == 1
    assert window.started  == 1
    assert window.finished == 1
    assert window.accepted == 1
    assert window.rejected == 0

    # click the button to launch the dialog.
    enaml_qtbot.mouseClick(window.async_button.proxy.widget, QtCore.Qt.LeftButton)

    assert len(window.windows) == 2
    assert window.starting == 2
    assert window.started  == 2
    assert window.finished == 1
    assert window.accepted == 1
    assert window.rejected == 0

    # click the Cancel button in the dialog.
    enaml_qtbot.mouseClick(next(otherWindow for otherWindow in window.windows if otherWindow.title == 'Test Dialog').cancel_button.proxy.widget, QtCore.Qt.LeftButton)

    assert len(window.windows) == 1
    assert window.starting == 2
    assert window.started  == 2
    assert window.finished == 2
    assert window.accepted == 1
    assert window.rejected == 1