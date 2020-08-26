#------------------------------------------------------------------------------
# Copyright (c) 2019, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys
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
def test_subscription_block_syntax(name):
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

# The following tests need to ensure that assignment in subscription block
# (either through a direct assignment or through the use of the walrus
# operator) do not cause issue with the tracer.
# Assignments can target the following scopes:
# - local to the block (only scope that the walrus operator target)
# - global module scope
# - widget and dynamic scope that can only be accessed qualified names (self.)

def test_subscription_block_observers1():
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


def test_subscription_block_observers2():
    """Test that intermediate assignments (local) do not confuse the tracer.

    """
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Main(Window):
        alias label
        attr a = 1
        attr b = 2
        Label: label:
            text <<
                b = a
                if b & 1:
                    return 'a'
                return 'none'

    """)
    Main = compile_source(source, 'Main')
    window = Main()
    label = window.label
    assert label.text == 'a'
    window.a = 2
    assert label.text == 'none'
    window.b = 1
    assert label.text == 'none'
    window.a = 1
    assert label.text == 'a'


def test_subscription_block_observers3():
    """Test that handling recursive behavior works.

    """
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Main(Window): main:
        alias label
        attr a = 1
        attr b = 2
        Label: label:
            text <<
                value = 'none'
                if a & 1:
                    value = 'a'
                elif b & 1:
                    value = 'b'
                main.b = 2
                return value

    """)
    Main = compile_source(source, 'Main')
    window = Main()
    label = window.label
    assert label.text == 'a'
    window.a = 2
    assert label.text == 'none'  # 2 and 2
    window.b = 1
    assert label.text == 'b'
    assert window.b == 2
    window.a = 1
    assert label.text == 'a'


def test_subscription_block_observers4():
    """Test that global variable shadowed by local can be accessed.

    """
    source = dedent("""\
    from enaml.widgets.api import *

    b = 2

    enamldef Main(Window): main:
        alias label
        attr a = 1
        attr b = 2
        attr counter = 0
        Label: label:
            text <<
                global b
                main.counter += 1
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
    assert window.counter == 1
    window.a = 2
    assert label.text == 'none'  # 2 and 2
    assert window.counter == 2
    window.b = 1
    assert label.text == 'none'
    assert window.counter == 2
    window.a = 1
    assert label.text == 'a'
    assert window.counter == 3


def test_subscription_block_observers5():
    """Test that global variable shadowed by local do not block notification
    on qualified name access.

    """
    source = dedent("""\
    from enaml.widgets.api import *

    b = 2

    enamldef Main(Window): main:
        alias label
        attr a = 1
        attr b = 2
        attr counter = 0
        Label: label:
            text <<
                global b
                main.counter += 1
                if a & 1:
                    return 'a'
                elif main.b & 1:
                    return 'b'
                return 'none'

    """)
    Main = compile_source(source, 'Main')
    window = Main()
    label = window.label
    assert label.text == 'a'
    assert window.counter == 1
    window.a = 2
    assert label.text == 'none'  # 2 and 2
    assert window.counter == 2
    window.b = 1
    assert label.text == 'b'
    assert window.counter == 3
    window.a = 1
    assert label.text == 'a'
    assert window.counter == 4


@pytest.mark.skipif(sys.version_info < (3, 8), reason="Require Python 3.8+")
def test_subscription_operator_walrus():
    """Test handling the walrus operator inside a subscription.

    """
    source = dedent("""\
    from enaml.widgets.api import *

    enamldef Main(Window):
        alias label
        alias label2
        attr a = 1
        attr b = 2
        attr c = 5
        Label: label:
            text << f"{a + (c := b + 1)}"
        Label: label2:
            text << f"{c}"

    """)
    Main = compile_source(source, 'Main')
    window = Main()
    label = window.label
    assert label.text == '4'
    # This is the same behavior as everywhere else where access can use a bare name
    # but assignment needs a qualified name.
    assert window.label2.text == '5'