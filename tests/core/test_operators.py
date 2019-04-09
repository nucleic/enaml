#------------------------------------------------------------------------------
# Copyright (c) 2019, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from textwrap import dedent

import pytest

from enaml.core.alias import Alias
from utils import compile_source


SUBSCRIPTION_BLOCK_TESTS = {
    # What should not work
    'leftshift newline in func': (SyntaxError, """
        enamldef Main(Window):
            Container:
                Label:
                    func test():
                        x = 1 <<
                            8
                        return str(x)
                    text = test()
        """),
    'leftshfit newline in attr': (SyntaxError, """
        enamldef Main(Window):
            Container:
                Label:
                    attr x = 1 <<
                                8
                    text = str(x)
        """),
    'leftshift newline in if': (SyntaxError, """
        enamldef Main(Window):
            Container:
                Label:
                    func test():
                        if 1 <<
                            8:
                            return 'this is bad'
                    text = str(test())
        """),
    'yield in sub block': (SyntaxError, """
        enamldef Main(Window):
            Container:
                Label:
                    text <<
                        for i in range(10):
                            yield i
        """),
    # What should still work
    'leftshift newline in parenthesis': (None, """
        enamldef Main(Window):
            Container:
                Label:
                    text = str(1 <<
                            8)
        """),
    'leftshift token in func': (None, """
        enamldef Main(Window):
            Container:
                Label:
                    func test():
                        x = 1 << 8
                        return str(x)
                    text = test()
        """),
    'leftshift token in attr': (None, """
        enamldef Main(Window):
            Container:
                Label:
                    attr x = 1 << 8
                    text = str(x)
        """),
    'leftshift newline update attr': (None, """
        enamldef Main(Window):
            Container:
                Label:
                    text <<
                        return str(1 << 8)
        """),
    'leftshift update attr': (None, """
        enamldef Main(Window):
            Container:
                Label:
                    text << str(1 << 8)
        """),
    'sub block var': (None, """
        enamldef Main(Window):
            Container:
                Label:
                    text <<
                        x = 10
                        if x:
                            return 'ten'
                        return 'not ten'
        """),
}


@pytest.mark.parametrize('name', SUBSCRIPTION_BLOCK_TESTS.keys())
def test_subscription_block(name):
    """Test a subscription block operator does not interfere with the leftshift
    operator.

    """
    error, code = SUBSCRIPTION_BLOCK_TESTS[name]
    source = dedent("""
    from enaml.widgets.api import *
    %s
    """ % code.lstrip())
    if error is not None:
        with pytest.raises(error):
            Main = compile_source(source, 'Main')
            window = Main()
    else:
        Main = compile_source(source, 'Main')
        window = Main()

def test_subscription_block_observers():
    """Test a subscription block operator.

    """
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Main(Window):
        alias label
        attr a = 1
        attr b = 2
        Label: label:
            text <<
                if a & 1:
                    return 'a'
                elif b & 1:
                    return 'b'
                return 'none'

    """)
    Main = compile_source(source, 'Main')
    window = Main()
    label = window.label
    assert label.text == 'a'
    window.a = 2
    assert label.text == 'none'  # 2 and 2
    window.b = 1
    assert label.text == 'b'
    window.a = 1
    assert label.text == 'a'

