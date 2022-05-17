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

from utils import compile_source, wait_for_window_displayed, is_qt_available


pytestmark = pytest.mark.skipif(not is_qt_available(),
                                reason='Requires a Qt binding')


def test_error_during_init(enaml_qtbot):
    source = dedent("""\
    from enaml.core.api import Conditional
    from enaml.widgets.api import Window, Container, Label

    enamldef MyWindow(Window): main:
        Container:
            Conditional:
                condition = None
                Label:
                    text = "True"

    """)
    tester = compile_source(source, 'MyWindow')()
    with pytest.raises(DeclarativeError) as excinfo:
        tester.show()
    assert 'line 4, in MyWindow' in excinfo.exconly()
    assert 'line 5, in Container' in excinfo.exconly()
    assert 'line 6, in Conditional' in excinfo.exconly()


def test_error_during_event(enaml_qtbot):
    from enaml.qt.QtCore import Qt, QObject, Signal
    source = dedent("""\
    from enaml.core.api import Conditional
    from enaml.widgets.api import Window, Container, Label, PushButton

    enamldef MyWidget(Container):
        alias button
        PushButton: button:
            clicked :: cond.condition = "invalid"
        Conditional: cond:
            condition = False
            Label:
                text = "Shown"

    enamldef MyWindow(Window): main:
        alias widget
        Label:
            text = "Title"
        MyWidget: widget:
            pass
    """)
    tester = compile_source(source, 'MyWindow')()

    tester.show()
    wait_for_window_displayed(enaml_qtbot, tester)

    with pytest.raises(DeclarativeError) as excinfo:
        tester.widget.button.clicked(True)

    assert 'line 13, in MyWindow' in excinfo.exconly()
    assert 'line 17, in MyWidget' in excinfo.exconly()
    assert 'line 6, in PushButton' in excinfo.exconly()
    assert 'line 7, in clicked' in excinfo.exconly()


def test_error_during_manual_set(enaml_qtbot):
    source = dedent("""\
    from enaml.core.api import Looper
    from enaml.widgets.api import Window, Container, Label

    enamldef MyWindow(Window): main:
        alias items: looper.iterable
        Container:
            Looper: looper:
                iterable = []
                Label:
                    text = loop.item

    """)
    tester = compile_source(source, 'MyWindow')()
    tester.show()
    wait_for_window_displayed(enaml_qtbot, tester)
    with pytest.raises(DeclarativeError) as excinfo:
        tester.items = [False]  # not a stringiterable
    print(excinfo.exconly())
    assert 'line 4, in MyWindow' in excinfo.exconly()
    assert 'line 6, in Container' in excinfo.exconly()
    # Unfortunately Looper is not there...
    assert 'line 9, in Label' in excinfo.exconly()
