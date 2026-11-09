#------------------------------------------------------------------------------
# Copyright (c) 2013-2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import asyncio
import gc
from textwrap import dedent
from collections import Counter

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

        func call2() -> Window:
            return main

    """)
    tester = compile_source(source, 'MyWindow')()
    bdmethod = tester.call
    assert isinstance(bdmethod, BoundDeclarativeMethod)
    for i in range(100):
        assert bdmethod(1) is tester
        assert bdmethod(arg=2) is tester
        assert bdmethod(1, kwarg=1) is tester
    func = type(tester).call
    assert isinstance(func, DeclarativeFunction)
    for i in range(100):
        assert func(tester, 1) is tester
        assert func(tester, arg=1) is tester
        assert func(tester, arg=1, kwarg=2) is tester
    func = type(tester).call2
    assert isinstance(func, DeclarativeFunction)
    for i in range(100):
        assert func(tester) is tester
        assert func(tester) is tester

    with pytest.raises(TypeError) as excinfo:
        type(tester).call2()
    assert 'DeclarativeFunction.__call__()' in excinfo.exconly()
    assert '1 argument' in excinfo.exconly()


def test_async_declarative_function_get_and_call():
    """Test calling an async declarative function and awaiting the result.

    """
    source = dedent("""\
    from enaml.widgets.window import Window

    enamldef MyWindow(Window): main:

        async func call(arg, kwarg=1):
            assert main is self
            return main, arg, kwarg

    """)
    tester = compile_source(source, 'MyWindow')()
    bdmethod = tester.call
    assert isinstance(bdmethod, BoundDeclarativeMethod)
    for i in range(3):
        assert asyncio.run(bdmethod(1)) == (tester, 1, 1)
        assert asyncio.run(bdmethod(arg=2)) == (tester, 2, 1)
        assert asyncio.run(bdmethod(1, kwarg=1)) == (tester, 1, 1)


def test_declarative_function_defaults():
    """Test calling DeclarativeFunction and BoundDeclarativeMethod.

    """
    source = dedent("""\
    from enaml.widgets.window import Window

    enamldef MyWindow(Window): main:

        func call(arg, kwarg=1):
            return arg, kwarg
    """)
    tester = compile_source(source, 'MyWindow')()
    r = tester.call(2)
    assert r == (2, 1)
    r = tester.call(2, 3)
    assert r == (2, 3)


def test_async_declarative_function_defaults():
    """Test default arguments for async declarative methods.

    """
    source = dedent("""\
    from enaml.widgets.window import Window

    enamldef MyWindow(Window): main:

        async func call(arg, kwarg=1):
            return arg, kwarg
    """)
    tester = compile_source(source, 'MyWindow')()
    r = asyncio.run(tester.call(2))
    assert r == (2, 1)
    r = asyncio.run(tester.call(2, 3))
    assert r == (2, 3)


def test_declarative_function_argument_variants_and_annotations():
    """Exercise the full declarative-function argument surface.

    """
    source = dedent("""\
    from enaml.widgets.window import Window

    enamldef MyWindow(Window): main:

        func call(a: int, b: str = "x", *rest: int, flag: bool = False, **meta: object) -> tuple[int, str, tuple[int, ...], bool, dict[str, object]]:
            return a, b, rest, flag, meta

        func result(value: int, label: str = "x") -> str:
            return f"{label}:{value}"

        async func fetch(path: str, /, *, timeout: float = 1.5, **extra: object) -> tuple[str, float, dict[str, object]]:
            return path, timeout, extra
    """)
    tester = compile_source(source, 'MyWindow')()

    result = tester.call(1, "y", 2, 3, flag=True, mode="fast")
    assert result == (1, "y", (2, 3), True, {"mode": "fast"})

    annotations = type(tester).call.__func__.__annotations__
    assert annotations["a"] is int
    assert annotations["b"] is str
    assert annotations["rest"] is int
    assert annotations["flag"] is bool
    assert annotations["meta"] is object
    assert annotations["return"] == tuple[int, str, tuple[int, ...], bool, dict[str, object]]

    assert tester.result(7) == "x:7"
    result_annotations = type(tester).result.__func__.__annotations__
    assert result_annotations["value"] is int
    assert result_annotations["label"] is str
    assert result_annotations["return"] is str
    assert tester.result(7) == "x:7"

    r = asyncio.run(tester.fetch("demo", timeout=2.5, mode="fast"))
    assert r == ("demo", 2.5, {"mode": "fast"})


def test_declarative_function_eq_and_hash():
    """Test that BoundDeclarativeMethod eq works.

    """
    source = dedent("""\
    from enaml.widgets.window import Window

    enamldef MyWindow(Window): main:

        func foo(arg):
            return arg

        func bar():
            return main

    """)
    MyWindow = compile_source(source, 'MyWindow')
    tester = MyWindow()
    foo = tester.foo
    assert tester.foo == foo
    assert tester.foo != tester.bar
    assert foo != tester.bar
    assert hash(foo) == hash(tester.foo)

    tester2 = MyWindow()
    assert tester2.foo != tester.foo
    assert hash(foo) != hash(tester2.foo)


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
    assert (Counter(gc.get_referents(tester.call)) ==
        Counter([tester.call.__func__, tester, tester.call.__key__] +
                ([type(tester.call)]))
    )


if __name__ == '__main__':
    test_bound_declarative_method()
    test_declarative_function()
    test_declarative_function_get_and_call()
