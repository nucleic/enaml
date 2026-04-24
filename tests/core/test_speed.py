# --------------------------------------------------------------------------------------
# Copyright (c) 2026, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# --------------------------------------------------------------------------------------
from textwrap import dedent

import pytest

from atom.api import Atom, Int

from utils import compile_source

pytest.importorskip("pytest_benchmark")

@pytest.mark.benchmark(group="standard-read")
@pytest.mark.parametrize("fn", ("enaml-attr", "py-attr"))
def test_bench_standard_read(benchmark, fn):
    """Test speed of the standard read handler"""
    source = dedent("""\
    from enaml.widgets.window import Window

    enamldef MyWindow(Window): main:
        attr value: int = 1

    """)
    if fn == "enaml-attr":
        tester = compile_source(source, "MyWindow")()
    else:

        class Tester(Atom):
            value = Int(1)

        tester = Tester()

    def task():
        assert tester.value == 1

    benchmark(task)


@pytest.mark.benchmark(group="standard-write")
@pytest.mark.parametrize("fn", ("enaml-attr", "py-attr"))
def test_bench_standard_write(benchmark, fn):
    """Test speed of the standard write handler"""
    source = dedent("""\
    from enaml.widgets.window import Window

    enamldef MyWindow(Window): main:
        attr value: int = 1

    """)
    if fn == "enaml-attr":
        tester = compile_source(source, "MyWindow")()
    else:

        class Tester(Atom):
            value = Int(1)

        tester = Tester()

    def task():
        tester.value += 1

    benchmark(task)


@pytest.mark.benchmark(group="standard-traced-read")
@pytest.mark.parametrize("fn", ("enaml-attr", "py-attr"))
def test_bench_standard_traced_read(benchmark, fn):
    """Test speed of the standard traced read handler"""
    source = dedent("""\
    from enaml.widgets.window import Window

    enamldef MyWindow(Window): main:
        attr model
        attr value: int << model.value

    """)

    class Model(Atom):
        value = Int(1)

    model = Model()

    if fn == "enaml-attr":
        tester = compile_source(source, "MyWindow")(model=model)
    else:

        class Tester(Atom):
            @property
            def value(self):
                return model.value

        tester = Tester()

    def task():
        assert tester.value == model.value
        model.value += 1

    benchmark(task)


@pytest.mark.benchmark(group="call-func")
@pytest.mark.parametrize("fn", ("enaml-func", "py-func"))
def test_bench_call_func_noargs(benchmark, fn):
    """Test speed of the calling a func with no arguments"""
    source = dedent("""\
    from enaml.widgets.window import Window

    enamldef MyWindow(Window): main:
        func f():
            return 1

    """)
    if fn == "enaml-func":
        tester = compile_source(source, "MyWindow")()
    else:

        class Tester(Atom):
            def f(self):
                return 1

        tester = Tester()

    def task():
        assert tester.f() == 1

    benchmark(task)


@pytest.mark.benchmark(group="call-func-args")
@pytest.mark.parametrize("fn", ("enaml-func", "py-func"))
def test_bench_call_func_args(benchmark, fn):
    """Test speed of calling a func with arguments"""
    source = dedent("""\
    from enaml.widgets.window import Window

    enamldef MyWindow(Window): main:
        func f(a):
            return a

    """)
    if fn == "enaml-func":
        tester = compile_source(source, "MyWindow")()
    else:

        class Tester(Atom):
            def f(self, a):
                return a

        tester = Tester()

    def task():
        assert tester.f(1) == 1

    benchmark(task)


@pytest.mark.benchmark(group="call-func-kwargs")
@pytest.mark.parametrize("fn", ("enaml-func", "py-func"))
def test_bench_call_func_kwargs(benchmark, fn):
    """Test speed of calling a func with kwargs"""
    source = dedent("""\
    from enaml.widgets.window import Window

    enamldef MyWindow(Window): main:
        func f(a):
            return a

    """)
    if fn == "enaml-func":
        tester = compile_source(source, "MyWindow")()
    else:

        class Tester(Atom):
            def f(self, a):
                return a

        tester = Tester()

    def task():
        assert tester.f(a=1) == 1

    benchmark(task)
