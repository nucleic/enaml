#------------------------------------------------------------------------------
# Copyright (c) 2013-2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import gc
from textwrap import dedent

import pytest

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

    with pytest.raises(TypeError) as excinfo:
        DeclarativeFunction(1, 1)
    assert 'function' in excinfo.exconly()


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
    assert bdmethod(arg=2) is tester
    assert bdmethod(1, kwarg=1) is tester
    func = type(tester).call
    assert isinstance(func, DeclarativeFunction)
    assert func(tester, 1) is tester
    assert func(tester, arg=1) is tester
    assert func(tester, arg=1, kwarg=2) is tester
    func = type(tester).call2
    assert isinstance(func, DeclarativeFunction)
    assert func(tester) is tester
    assert func(tester) is tester

    with pytest.raises(TypeError) as excinfo:
        type(tester).call2()
    assert 'DeclarativeFunction.__call__()' in excinfo.exconly()
    assert '1 argument' in excinfo.exconly()


def test_calling_super():
    """Test calling a declarative function using super.

    """
    source = dedent("""\
    from enaml.widgets.window import Window

    enamldef MyWindow(Window): main:

        func call(arg, kwarg=1):
            return super()

    """)
    tester = compile_source(source, 'MyWindow')()
    with pytest.raises(TypeError) as excinfo:
        tester.call(1)
    assert 'super()' in excinfo.exconly()


@pytest.mark.parametrize('attribute',
                         ['__builtins__', '_d_storage'])
def test_invoking_broken_dfunc(attribute):
    """Test invoking a declarative function whose one key attribute is missing.

    """
    source = dedent("""\
    from enaml.widgets.window import Window

    enamldef MyWindow(Window): main:

        func call(arg, kwarg=1):
            return 1

    """)
    tester = compile_source(source, 'MyWindow')()
    if attribute == '__builtins__':
        del tester.call.__func__.__globals__['__builtins__']
        obj = tester
    elif attribute == '_d_storage':
        del tester.call.__self__._d_storage
        obj = object()
    else:
        raise RuntimeError('wrong parameter')
    exc = KeyError if attribute == '__builtins__' else AttributeError
    with pytest.raises(exc) as excinfo:
        type(tester).call(obj, 1)
    assert attribute in excinfo.exconly()


def test_traversing_bound_method():
    """Test traversing a bound method.

    """
    source = dedent("""\
    from enaml.widgets.window import Window

    enamldef MyWindow(Window): main:

        func call(arg, kwarg=1):
            return super()

    """)
    tester = compile_source(source, 'MyWindow')()
    assert (gc.get_referents(tester.call) ==
            [tester.call.__func__, tester, tester.call.__key__])


if __name__ == '__main__':
    test_bound_declarative_method()
    test_declarative_function()
    test_declarative_function_get_and_call()
