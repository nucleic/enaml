#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from textwrap import dedent

from enaml.core.declarative_function import (DeclarativeFunction,
                                             BoundDeclarativeMethod)
from utils import compile_source


def test_declarative_function():
    """Test the descriptors and repr of DeclarativeFunction.

    """
    def test(a, b=1):
        pass

    dfunc = DeclarativeFunction(test, '_scope_key')
    assert dfunc.__func__ is test
    assert dfunc.__key__ == '_scope_key'
    assert dfunc._d_func
    assert 'declarative function' in repr(dfunc)


def test_bound_declarative_method():
    """Test the descriptors and repr of BoundDeclarativeMethod.

    """
    def test(a, b=1):
        pass

    SELF = object()

    bdmethod = DeclarativeFunction(test, '_scope_key').__get__(SELF, None)
    assert bdmethod.__func__ is test
    assert bdmethod.__key__ == '_scope_key'
    assert bdmethod.__self__ is SELF
    assert 'bound declarative method' in repr(bdmethod)


def test_declarative_function_get_and_call():
    """Test calling DeclarativeFunction and BoundDeclarativeMethod.

    """
    source = dedent("""\
    from enaml.widgets.window import Window

    enamldef MyWindow(Window): main:

        func call(arg, kwarg=1):
            assert main is self
            return main

        func call2():
            return main

    """)
    tester = compile_source(source, 'MyWindow')()
    bdmethod = tester.call
    assert isinstance(bdmethod, BoundDeclarativeMethod)
    assert bdmethod(1) is tester
    assert bdmethod(1) is tester
    func = type(tester).call
    assert isinstance(func, DeclarativeFunction)
    assert func(tester, 1) is tester
    assert func(tester, 1) is tester
    func = type(tester).call2
    assert isinstance(func, DeclarativeFunction)
    assert func(tester) is tester
    assert func(tester) is tester

if __name__ == '__main__':
    test_bound_declarative_method()
    test_declarative_function()
    test_declarative_function_get_and_call()
