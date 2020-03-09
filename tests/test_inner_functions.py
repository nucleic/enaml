#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
"""Test the handling of nested functions such as lambda functions and
implicit functions used by comprehensions.

"""
import pytest

from utils import compile_source

OPERATOR_TEMPLATE =\
"""from enaml.widgets.window import Window

enamldef Main(Window):
    event ev
    attr called : bool = False
    ev ::
        test = 1
        a = {}
        try:
            b = i
        except NameError:
            pass
        else:
            raise AssertionError('i leaked out of the comprehension')
        self.called = True

"""


SYNCHRONISATION_TEMPLATE =\
"""from enaml.widgets.api import Window, Container, Field, Label

enamldef Main(Window):

    attr colors = ['red', 'blue', 'yellow', 'green']
    alias search_txt : search.text
    alias formatted_comp : lab.text

    Container: container:

        Field: search:
            placeholder = "Search..."
        Label: lab:
            text << '{{}}'.format({})

"""


FUNCTION_TEMPLATE =\
"""from enaml.widgets.window import Window

enamldef Main(Window):
    func call():
        test = 1
        a = {}
        try:
            b = i
        except NameError:
            pass
        else:
            raise AssertionError('i leaked out of the comprehension')
        return True

"""


def test_lambda():
    """Test that lambda work when used in the context of tracing.

    """
    source = SYNCHRONISATION_TEMPLATE.format(
        'sorted([1, 2, 3], key=lambda x: -x)')
    win = compile_source(source, 'Main')()
    assert win.formatted_comp == '[3, 2, 1]'


def test_tracing_lambda():
    """Test that lambda can be traced.

    """
    source = SYNCHRONISATION_TEMPLATE.format(
        'sorted([1, 2, 3], key=lambda x: colors[x-1][0])')
    win = compile_source(source, 'Main')()
    assert win.formatted_comp == '[2, 1, 3]'
    win.colors = ['yellow', 'red', 'blue', 'green']
    assert win.formatted_comp == '[3, 2, 1]'


# Test that we can access the non local values and the closure variables
@pytest.mark.parametrize('value', ['self', 'test'])
def test_list_comprehension_operator(value):
    """Test running a list comprehension in an operator handler.

    """
    source = OPERATOR_TEMPLATE.format('[%s for i in range(10)]' % value)
    win = compile_source(source, 'Main')()
    win.ev = True
    assert win.called


def test_list_comprehension_synchronization():
    """Test running a list comprehension in a traced read handler.

    """
    source = SYNCHRONISATION_TEMPLATE.format(
        '[c for c in colors if not search.text or search.text in c]')
    win = compile_source(source, 'Main')()
    assert win.formatted_comp == "['red', 'blue', 'yellow', 'green']"
    win.search_txt = 'red'
    assert win.formatted_comp == "['red']"
    win.search_txt = ''
    win.colors = ['red', 'blue', 'yellow']
    assert win.formatted_comp == "['red', 'blue', 'yellow']"


# Test that we can access the non local values and the closure variables
@pytest.mark.parametrize('value', ['self', 'test'])
def test_list_comprehension_func(value):
    """Test running a list comprehension in a declarative function.

    """
    source = FUNCTION_TEMPLATE.format('[%s for i in range(10)]' % value)
    win = compile_source(source, 'Main')()
    assert win.call()


# Test that we can access the non local values and the closure variables
@pytest.mark.parametrize('value', ['self', 'test'])
def test_dict_comprehension_operator(value):
    """Test running a dict comprehension in an operator handler.

    """
    source = OPERATOR_TEMPLATE.format('{i: %s for i in range(10)}' % value)
    win = compile_source(source, 'Main')()
    win.ev = True
    assert win.called


def test_dict_comprehension_synchronisation():
    """Test running a dict comprehension in a traced read handler.

    """
    source = SYNCHRONISATION_TEMPLATE.format(
        '{i: search.text for i in range(3)}')
    win = compile_source(source, 'Main')()
    assert eval(win.formatted_comp) == {0: '', 1: '', 2: ''}
    win.search_txt = 'red'
    assert eval(win.formatted_comp) == {0: 'red', 1: 'red', 2: 'red'}


# Test that we can access the non local values and the closure variables
@pytest.mark.parametrize('value', ['self', 'test'])
def test_dict_comprehension_func(value):
    """Test running a dict comprehension in a declarative function.

    """
    source = FUNCTION_TEMPLATE.format('{i: %s for i in range(10)}' % value)
    win = compile_source(source, 'Main')()
    assert win.call()


# Test that we can access the non local values and the closure variables
@pytest.mark.parametrize('value', ['self', 'test'])
def test_set_comprehension_operator(value):
    """Test running a set comprehension in an operator handler.

    """
    source = OPERATOR_TEMPLATE.format('{%s for i in range(10)}' % value)
    win = compile_source(source, 'Main')()
    win.ev = True
    assert win.called


def test_set_comprehension_synchronization():
    """Test running a set comprehension in a traced read handler.

    """
    source = SYNCHRONISATION_TEMPLATE.format(
        '{search.text for i in range(3)}')
    win = compile_source(source, 'Main')()
    assert eval(win.formatted_comp) == {''}
    win.search_txt = 'red'
    assert eval(win.formatted_comp) == {'red'}


# Test that we can access the non local values and the closure variables
@pytest.mark.parametrize('value', ['self', 'test'])
def test_set_comprehension_func(value):
    """Test running a set comprehension in a declarative function.

    """
    source = FUNCTION_TEMPLATE.format('{%s for i in range(10)}' % value)
    win = compile_source(source, 'Main')()
    assert win.call()


def test_handling_nested_comprehension():
    """Test handling nested comprehensions.

    """
    source = FUNCTION_TEMPLATE.format('{self for i in {j for j in range(10)}}')
    win = compile_source(source, 'Main')()
    assert win.call()


def test_handling_nested_comprehension_synchronization():
    """Test handling nested comprehensions in a traced read.

    """
    source = SYNCHRONISATION_TEMPLATE.format(
        '{search.text for i in {j for j in colors}}')
    win = compile_source(source, 'Main')()
    assert eval(win.formatted_comp) == {''}
    win.search_txt = 'red'
    assert eval(win.formatted_comp) == {'red'}
    win.colors = []
    assert eval(win.formatted_comp) == set()
