#------------------------------------------------------------------------------
# Copyright (c) 2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import sys

from textwrap import dedent
from contextlib import contextmanager

import pytest

from enaml.core.declarative_meta import DeclarativeError
from enaml.widgets.api import Window

from utils import compile_source, wait_for_window_displayed


@contextmanager
def destroy_windows():
    # Cleanup windows that do not call destroy due to an "unclean" shutdown
    try:
        yield
    finally:
        for w in list(Window.windows):
            w.destroy()


def test_error_pattern_node_included_init(enaml_qtbot):
    source = dedent("""\
    from enaml.core.api import Conditional
    from enaml.widgets.api import Window, Container, Label

    enamldef Main(Window): main:
        Container:
            Conditional:
                condition = None
                Label:
                    text = "Text"

    """)
    tester = compile_source(source, 'Main')()
    with destroy_windows():
        with pytest.raises(DeclarativeError) as excinfo:
            tester.show()
    assert 'line 4, in Main' in excinfo.exconly()
    assert 'line 5, in Container' in excinfo.exconly()
    assert 'line 6, in Conditional' in excinfo.exconly()


def test_error_multiple_same_cls_init(enaml_qtbot):
    source = dedent("""\
    from enaml.widgets.api import Window, Container, Label

    enamldef Main(Window): main:
        Container:
            Label: lbl1:
                text = False
            Label: lbl2:
                text = "Ok"
    """)
    tester = compile_source(source, 'Main')()
    with destroy_windows():
        with pytest.raises(DeclarativeError) as excinfo:
            tester.show()
    assert 'line 3, in Main' in excinfo.exconly()
    assert 'line 4, in Container' in excinfo.exconly()
    # Make sure it is not showing the error for Label 2
    assert 'line 5, in Label' in excinfo.exconly()


def test_error_during_read_expr(qt_app, qtbot):
    source = dedent("""\
    from enaml.widgets.api import Window, Container, Label

    enamldef Main(Window):
        Container:
            Label:
                text = undefined_variable
    """)
    tester = compile_source(source, 'Main')()
    with destroy_windows():
        with pytest.raises(DeclarativeError) as excinfo:
            tester.show()

    assert 'line 3, in Main' in excinfo.exconly()
    assert 'line 4, in Container' in excinfo.exconly()
    assert 'line 5, in Label' in excinfo.exconly()
    assert 'line 6, in text' in excinfo.exconly()


def test_error_during_event(qt_app, qtbot):
    from enaml.qt.QtCore import Qt, QObject, Signal
    source = dedent("""\
    from enaml.core.api import Conditional
    from enaml.widgets.api import Window, Container, Label, PushButton

    enamldef MyWidget(Container):
        alias button
        PushButton: button:
            clicked :: cond.condition = "invalid"
        Conditional: cond:
            condition = True
            Label:
                text = "Shown"

    enamldef Main(Window): main:
        alias widget
        Label:
            text = "Title"
        MyWidget: widget:
            pass
    """)
    tester = compile_source(source, 'Main')()

    tester.show()
    wait_for_window_displayed(qtbot, tester)

    with destroy_windows():
        with pytest.raises(DeclarativeError) as excinfo:
            tester.widget.button.clicked(True)

    assert 'line 13, in Main' in excinfo.exconly()
    assert 'line 17, in MyWidget' in excinfo.exconly()
    assert 'line 6, in PushButton' in excinfo.exconly()
    assert 'line 7, in clicked' in excinfo.exconly()


def test_error_during_manual_set(qt_app, qtbot):
    source = dedent("""\
    from enaml.core.api import Looper
    from enaml.widgets.api import Window, Container, Label

    enamldef Main(Window): main:
        alias items: looper.iterable
        Container:
            Looper: looper:
                iterable = []
                Label:
                    text = loop.item

    """)
    tester = compile_source(source, 'Main')()
    tester.show()
    wait_for_window_displayed(qtbot, tester)
    with destroy_windows():
        with pytest.raises(DeclarativeError) as excinfo:
            tester.items = [False]  # not a string iterable
    assert 'line 4, in Main' in excinfo.exconly()
    assert 'line 6, in Container' in excinfo.exconly()
    assert 'line 7, in Looper' in excinfo.exconly()
    assert 'line 9, in Label' in excinfo.exconly()


def test_error_template_init(enaml_qtbot):
    source = dedent("""\
    from enaml.widgets.api import Window, Container, Form, Html

    template Panel(Content):
        Container:
            Content:
                pass

    enamldef HtmlContent(Form):
        Html:
            source = False

    enamldef Main(Window): main:
        Panel(HtmlContent):
            pass
    """)
    tester = compile_source(source, 'Main')()

    with destroy_windows():
        with pytest.raises(DeclarativeError) as excinfo:
            tester.show()

    assert 'line 12, in Main' in excinfo.exconly()
    assert 'line 13, in Panel' in excinfo.exconly()
    assert 'line 3, in Panel' in excinfo.exconly()
    assert 'line 4, in Container' in excinfo.exconly()
    assert 'line 5, in HtmlContent' in excinfo.exconly()
    assert 'line 9, in Html' in excinfo.exconly()


def test_error_during_template_expr(qt_app, qtbot):
    source = dedent("""\
    from enaml.widgets.api import Window, Container, Form, CheckBox, PushButton

    template FormTemplate(Content):
        Container:
            alias submit
            Content: form:
                pass
            PushButton: submit:
                text = "Submit"
                clicked :: form.submit()

    enamldef MyForm(Form):
        func submit():
            checkbox.checked = None
        CheckBox: checkbox:
            text = "Tool"
            checked = True

    enamldef Main(Window): main:
        alias form
        FormTemplate(MyForm): form:
            pass
    """)
    tester = compile_source(source, 'Main')()
    tester.show()
    wait_for_window_displayed(qtbot, tester)
    with destroy_windows():
        with pytest.raises(DeclarativeError) as excinfo:
            tester.form.submit.clicked(True)

    assert 'line 19, in Main' in excinfo.exconly()
    assert 'line 21, in FormTemplate' in excinfo.exconly()
    assert 'line 3, in FormTemplate' in excinfo.exconly()
    assert 'line 4, in Container' in excinfo.exconly()
    assert 'line 8, in PushButton' in excinfo.exconly()
    assert 'line 10, in clicked' in excinfo.exconly()
    # TODO: Include stack from original trace?
    # assert 'line 14, in submit' in excinfo.exconly()
