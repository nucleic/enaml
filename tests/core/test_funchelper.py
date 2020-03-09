#------------------------------------------------------------------------------
# Copyright (c) 2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from textwrap import dedent

import pytest

from enaml.core.funchelper import call_func
from utils import compile_source

source = dedent("""\
from enaml.widgets.window import Window

enamldef MyWindow(Window): main:

    func call(*args, **kwargs):
        return kwargs.get('a') or a

""")
tester = compile_source(source, 'MyWindow')()

func = tester.call.__func__


def test_calling_function():
    """Test calling a function with locals.

    """
    assert call_func(func, (), {}, {'a': 1}) == 1
    assert call_func(func, (1,), {}, {'a': 1}) == 1


def test_calling_function_kwarg():
    """Test calling a function with kwargs.

    """
    assert call_func(func, (), {'b': 2}, {'a': 1}) == 1


def test_handling_none_as_locals():
    """Test passing None as locals.

    """
    assert call_func(func, (), {'a': 1}, None) == 1


def test_handling_wrong_arguments():
    """Test handling incorrect arguments.

    """
    with pytest.raises(TypeError) as excinfo:
        call_func(None, None, None, None)
    assert 'Python function' in excinfo.exconly()

    with pytest.raises(TypeError) as excinfo:
        call_func(func, None, None, None)
    assert 'tuple' in excinfo.exconly()

    with pytest.raises(TypeError) as excinfo:
        call_func(func, (), None, None)
    assert 'dict' in excinfo.exconly()

    with pytest.raises(TypeError) as excinfo:
        call_func(func, (), {}, 1)
    assert 'mapping' in excinfo.exconly()
