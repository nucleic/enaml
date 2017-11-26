#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.compat import IS_PY3

from utils import compile_source

OPERATOR_TEMPLATE =\
"""from enaml.widgets.window import Window

enamldef Main(Window):
    event ev
    attr called : bool = False
    ev ::
        a = {}
        if RUN_CHECK:
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
        a = {}
        if RUN_CHECK:
            try:
                b = i
            except NameError:
                pass
            else:
                raise AssertionError('i leaked out of the comprehension')
        return True

"""


def test_list_comprehension_operator():
    """Test running a list comprehension in an operator handler.

    """
    source = OPERATOR_TEMPLATE.format('[self for i in range(10)]')
    win = compile_source(source, 'Main', namespace={'RUN_CHECK': IS_PY3})()
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


def test_list_comprehension_func():
    """Test running a list comprehension in a declarative function.

    """
    source = FUNCTION_TEMPLATE.format('[self for i in range(10)]')
    win = compile_source(source, 'Main', namespace={'RUN_CHECK': IS_PY3})()
    assert win.call()


def test_dict_comprehension_operator():
    """Test running a dict comprehension in an operator handler.

    """
    source = OPERATOR_TEMPLATE.format('{i: self for i in range(10)}')
    win = compile_source(source, 'Main', namespace={'RUN_CHECK': True})()
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


def test_dict_comprehension_func():
    """Test running a dict comprehension in a declarative function.

    """
    source = FUNCTION_TEMPLATE.format('{i: self for i in range(10)}')
    win = compile_source(source, 'Main', namespace={'RUN_CHECK': True})()
    assert win.call()


def test_set_comprehension_operator():
    """Test running a set comprehension in an operator handler.

    """
    source = OPERATOR_TEMPLATE.format('{self for i in range(10)}')
    win = compile_source(source, 'Main', namespace={'RUN_CHECK': True})()
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


def test_set_comprehension_func():
    """Test running a set comprehension in a declarative function.

    """
    source = FUNCTION_TEMPLATE.format('{self for i in range(10)}')
    win = compile_source(source, 'Main', namespace={'RUN_CHECK': True})()
    assert win.call()


def test_handling_nested_comprehension():
    """Test handling nested comprehensions.

    """
    source = FUNCTION_TEMPLATE.format('{self for i in {j for j in range(10)}}')
    win = compile_source(source, 'Main', namespace={'RUN_CHECK': True})()
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
