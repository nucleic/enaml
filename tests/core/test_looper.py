#------------------------------------------------------------------------------
# Copyright (c) 2019, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import pytest
import random
from textwrap import dedent
from utils import compile_source, is_qt_available, wait_for_window_displayed

from enaml.core.api import Looper
from enaml.widgets.api import Label


@pytest.mark.skipif(not is_qt_available(), reason='Requires a Qt binding')
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

