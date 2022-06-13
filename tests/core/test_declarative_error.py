#------------------------------------------------------------------------------
# Copyright (c) 2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import sys

from textwrap import dedent

import pytest

from enaml.core.declarative_meta import DeclarativeError
from enaml.widgets.api import Window

from utils import compile_source, wait_for_window_displayed, is_qt_available


pytestmark = pytest.mark.skipif(not is_qt_available(),
                                reason='Requires a Qt binding')


def destroy_windows():
    # Cleanup windows that do not call destroy due to an "unclean" shutdown
    for w in list(Window.windows):
        w.destroy()


def test_error_during_init(enaml_qtbot):
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
    with pytest.raises(DeclarativeError) as excinfo:
        tester.show()
    assert 'line 4, in Main' in excinfo.exconly()
    assert 'line 5, in Container' in excinfo.exconly()
    assert 'line 6, in Conditional' in excinfo.exconly()


def test_error_template_init(enaml_qtbot):
    source = dedent("""\
    from enaml.widgets.api import Window, Container, Html

    template Panel(Content):
        Container:
            Content:
                pass

    enamldef HtmlContent(Html):
        source = False

    enamldef Main(Window): main:
        Panel(HtmlContent):
            pass
    """)
    tester = compile_source(source, 'Main')()

    try:
        with pytest.raises(DeclarativeError) as excinfo:
            tester.show()
    finally:
        destroy_windows()

    assert 'line 11, in Main' in excinfo.exconly()
    # TODO: How can it determine the template name?
    assert 'line 12, in Panel' in excinfo.exconly()
    assert 'line 3, in Panel' in excinfo.exconly()
    assert 'line 4, in Container' in excinfo.exconly()
    assert 'line 5, in HtmlContent' in excinfo.exconly()


def test_error_during_read_expr(qt_app, qtbot):
    source = dedent("""\
    from enaml.widgets.api import Window, Container, Label

    enamldef Main(Window):
        Container:
            Label:
                text = undefined_variable
    """)
    tester = compile_source(source, 'Main')()
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

    try:
        with pytest.raises(DeclarativeError) as excinfo:
            tester.widget.button.clicked(True)
    finally:
        destroy_windows()

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
    try:
        with pytest.raises(DeclarativeError) as excinfo:
            tester.items = [False]  # not a string iterable
    finally:
        destroy_windows()
    assert 'line 4, in Main' in excinfo.exconly()
    assert 'line 6, in Container' in excinfo.exconly()
    assert 'line 7, in Looper' in excinfo.exconly()
    assert 'line 9, in Label' in excinfo.exconly()
