#------------------------------------------------------------------------------
# Copyright (c) 2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import gc

import pytest

from atom.datastructures.api import sortedmap
from enaml.core.dynamicscope import UserKeyError, DynamicScope


@pytest.fixture
def dynamicscope():
    """Dynamic used for testing.

    """
    class Owner(): # XXX will need a real class with descriptor and non descriptors
        pass
    owner = Owner()
    owner._parent = Owner()
    owner._parent._parent = None
    locs = sortedmap()
    locs['a'] = 1
    globs = {'b': 2}
    builtins = {'c': 3}
    change = {'d': 4}
    tracer = object()  # XXX will need a real tracer
    dynamicscope = DynamicScope(owner, locs, globs, builtins, change, tracer)
    dynamicscope['e'] = 5  # Add an entry in the f_writes

    return dynamicscope, (owner, locs, globs, builtins, change, tracer)


def test_dynamic_scope_creation():
    """Test handling bad arguments when creating dnamic scope.

    """
    owner = object()
    locs = sortedmap()
    globs = {}
    builtins = {}
    change = {}
    tracer = object()

    dynamicscope = DynamicScope(owner, locs, globs, builtins, change, tracer)
    for referrent, obj in zip(gc.get_referents(dynamicscope),
                              [owner, change, tracer, locs, globs, builtins,
                               None, None]):
        assert referrent is obj

    with pytest.raises(TypeError) as excinfo:
        DynamicScope(owner, None, globs, builtins)
    assert 'mapping' in excinfo.exconly()

    with pytest.raises(TypeError) as excinfo:
        DynamicScope(owner, locs, None, builtins)
    assert 'dict' in excinfo.exconly()

    with pytest.raises(TypeError) as excinfo:
        DynamicScope(owner, locs, globs, None)
    assert 'dict' in excinfo.exconly()

    del dynamicscope
    gc.collect()


def test_dynamicscope_contains(dynamicscope):
    """Test the contains method.

    """
    dynamicscope, _ = dynamicscope
    for key in ('a', 'b', 'c', 'e',
                'self', 'change', 'nonlocals', '__scope__', '_[tracer]'):
        assert key in dynamicscope

    assert 'z' not in dynamicscope


def test_dynamicscope_get(dynamicscope):
    """Test the get method.

    """
    dynamicscope, args = dynamicscope
    nlocals = dynamicscope['nonlocals']
    for key, value in zip(['a', 'b', 'c', 'e', 'self', 'change',
                           'nonlocals', '__scope__', '_[tracer]'],
                          [1, 2, 3, 5,
                           args[0], args[-2],
                           nlocals, dynamicscope, args[-1]]):
        assert dynamicscope[key] == value

    with pytest.raises(KeyError):
        dynamicscope['z']

    with pytest.raises(TypeError) as excinfo:
        dynamicscope[1]
    assert 'str' in excinfo.exconly()


def test_dynamicscope_set(dynamicscope):
    """Test the set method.

    """
    dynamicscope, _ = dynamicscope
    for key, value in zip(['a', 'b', 'c', 'e'],
                          [1, 2, 3, 5]):
        dynamicscope[key] += 1
        assert dynamicscope[key] == value + 1

    with pytest.raises(TypeError) as excinfo:
        dynamicscope[1] = 1
    assert 'str' in excinfo.exconly()


def test_dynamicscope_del(dynamicscope):
    """Test the del method.

    """
    dynamicscope, args = dynamicscope
    del dynamicscope['e']
    assert 'e' not in dynamicscope

    with pytest.raises(KeyError):
        del dynamicscope['z']

    dynamicscope = DynamicScope(*args)
    # Test the absence of f_writes
    with pytest.raises(KeyError):
        del dynamicscope['z']

    with pytest.raises(TypeError) as excinfo:
        del dynamicscope[1]
    assert 'str' in excinfo.exconly()


@pytest.fixture
def nonlocals(dynamicscope):
    """Access the nonlocals of a dynamic scope.

    """
    return dynamicscope[0]['nonlocals']


# XXX test nonlocals (from nonlocals in a dynamic scope)
# - getitem
# - getattr
# - setitem
# - setattr
# - delitem
# - contains
# - traverse
# - clear
# - repr
# - call (bad level)
