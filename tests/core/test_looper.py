#------------------------------------------------------------------------------
# Copyright (c) 2019-2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import pytest
from textwrap import dedent
from utils import compile_source, wait_for_window_displayed

from enaml.core.api import Looper
from enaml.widgets.api import Label


def test_looper_refresh(enaml_qtbot, enaml_sleep):
    """ Test that the loop index is valid when items are reordered.

    """
    source = dedent("""\
    from enaml.core.api import Looper
    from enaml.widgets.api import Window, Container, Label, PushButton


    enamldef Main(Window): window:
        attr data: list = []
        alias container
        Container: container:
            Looper:
                iterable << window.data
                Label:
                    text << '{} {}'.format(loop.index, loop.item)


    """)
    tester = compile_source(source, 'Main')()
    tester.show()
    wait_for_window_displayed(enaml_qtbot, tester)

    for data in (
                # Set initial
                ['a', 'b', 'c'],

                # Resort order data and ensure it matches
                ['b', 'c', 'a'],

                # Remove and resort ensure it still matches
                ['a', 'b']
            ):
        enaml_qtbot.wait(enaml_sleep)
        tester.data = data
        expected = ['{} {}'.format(*it) for it in enumerate(data)]
        assert [c.text for c in tester.container.children
                if isinstance(c, Label)] == expected


def test_looper_refresh_iterator(enaml_qtbot, enaml_sleep):
    """ Test that a looper properly refreshes when given an iterator.

    """
    source = dedent("""\
    from enaml.core.api import Looper, Conditional
    from enaml.widgets.api import Window, Container, Label, ObjectCombo


    enamldef Main(Window): window:
        attr data: list = []
        attr flag: str = 'a'
        attr show_more: bool << flag == 'b' or flag == 'c'
        alias container
        Container: container:
            ObjectCombo: combo:
                items = ['a', 'b', 'c']
                selected := window.flag
            Conditional:
                condition << show_more
                # Nested loop forces re-eval twice
                Conditional:
                    condition << flag == 'c'
                    Looper:
                        iterable << reversed(data)
                        Label:
                            text << '{} {}'.format(loop.index, loop.item)

    """)
    tester = compile_source(source, 'Main')()
    tester.show()
    wait_for_window_displayed(enaml_qtbot, tester)

    enaml_qtbot.wait(enaml_sleep)
    data = [1, 2, 3]
    tester.data = data

    # Conditional is still hiding it
    assert not any(
        c for c in tester.container.children if isinstance(c, Label))

    # Now they should all be shown
    tester.flag = 'c'
    enaml_qtbot.wait(enaml_sleep)
    expected = ['{} {}'.format(*it) for it in enumerate(reversed(data))]
    assert [c.text for c in tester.container.children
            if isinstance(c, Label)] == expected


def test_looper_iterable():
    """ Test that a looper validates the iterator properly.

    """
    looper = Looper()
    looper.iterable = {1, 2, 3}
    looper.iterable = {'a': 1, 'b': 2}
    looper.iterable = 'abc'

    with pytest.raises(TypeError):
        looper.iterable = 1

    with pytest.raises(TypeError):
        looper.iterable = None
