#------------------------------------------------------------------------------
# Copyright (c) 2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import gc
import sys

import pytest

from atom.datastructures.api import sortedmap
from enaml.core.dynamicscope import UserKeyError, DynamicScope


@pytest.fixture
def dynamicscope():
    """Dynamic used for testing.

    """

    class NonDataDescriptor(object):

        def __init__(self, should_raise=False):
            self.should_raise = should_raise

        def __get__(self, instance, objtype=None):
            if not self.should_raise:
                return instance
            else:
                raise KeyError()

    class ReadOnlyDescriptor(object):

        def __get__(self, instance, objtype=None):
            return 1

        def __set__(self, instance, objtype=None):
            raise AttributeError

    class WriteOnlyDescriptor(object):

        def __set__(self, instance, value, objtype=None):
            instance.value = 1

    class Owner(object):
        def __init__(self):
            self._parent = None
            self.attribute1 = 1
            self._prop2 = 0

        owner = NonDataDescriptor()

        prop1 = ReadOnlyDescriptor()

        @property
        def prop2(self):
            return self._prop2

        @prop2.setter
        def prop2(self, value):
            self._prop2 = value

        @property
        def key_raise(self):
            raise KeyError()

        non_data_key_raise = NonDataDescriptor(True)

        write_only = WriteOnlyDescriptor()

    class TopOwner(Owner):

        @property
        def top(self):
            return self._top

        @top.setter
        def top(self, value):
            self._top = 1

    class Tracer(object):
        """Tracer for testing.

        """
        def __init__(self):
            self.traced = []

        def dynamic_load(self, owner, name, value):
            self.traced.append((owner, name, value))

    owner = Owner()
    owner.attribute1 = 2
    owner._parent = TopOwner()
    owner._parent.attribute2 = 1
    locs = sortedmap()
    locs['a'] = 1
    globs = {'b': 2}
    builtins = {'c': 3}
    change = {'d': 4}
    tracer = Tracer()
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

    with pytest.raises(TypeError):
        1 in dynamicscope


def test_dynamicscope_getitem(dynamicscope):
    """Test the getitem method.

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
        assert dynamicscope.get(key) == value

    assert dynamicscope.get('z') == None
    assert dynamicscope.get('z', 'abc') == 'abc'

    with pytest.raises(TypeError) as excinfo:
        dynamicscope.get(1)

    with pytest.raises(TypeError) as excinfo:
        dynamicscope.get()

    with pytest.raises(TypeError) as excinfo:
        dynamicscope.get("name", "default", "extra")


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


def test_dynamicscope_lifecycle(dynamicscope, nonlocals):
    """Test the repr, traverse, clear etc...

    """
    owner, tracer = dynamicscope[1][0], dynamicscope[1][-1]
    assert 'Nonlocals[' in repr(nonlocals)
    assert gc.get_referents(nonlocals) == [owner, tracer]

    del dynamicscope
    gc.collect()


def test_nonlocals_contains(nonlocals):
    """Test nonlocals contains.

    """
    for key in ('attribute1', 'attribute2', 'owner', 'prop2', 'key_raise'):
        assert key in nonlocals

    with pytest.raises(TypeError):
        1 in nonlocals


def test_nonlocals_get(dynamicscope, nonlocals):
    """Test accessing attribute through getattr and getitem

    """
    tracer = dynamicscope[1][-1]

    assert nonlocals.attribute1 == 2
    assert tracer.traced[-1][1] == 'attribute1'
    assert nonlocals.attribute2 == 1
    assert tracer.traced[-1][1] == 'attribute2'
    assert nonlocals.owner
    assert tracer.traced[-1][1] == 'owner'
    assert nonlocals.prop2 == 0
    assert tracer.traced[-1][1] == 'prop2'

    with pytest.raises(AttributeError):
        nonlocals.unknown

    with pytest.raises(UserKeyError):
        nonlocals.key_raise

    assert nonlocals['attribute1'] == 2
    assert nonlocals['attribute2'] == 1
    assert nonlocals['owner']
    assert nonlocals['prop2'] == 0

    with pytest.raises(AttributeError):
        nonlocals.unknown

    with pytest.raises(UserKeyError):
        nonlocals.key_raise

    with pytest.raises(UserKeyError):
        nonlocals.non_data_key_raise

    with pytest.raises(TypeError):
        nonlocals[1]

    # Test non-readable descriptor
    nonlocals.write_only
    assert tracer.traced[-1][1] == 'write_only'


def test_nonlocals_set(nonlocals):
    """Test setting attribute through setatttr and setitem.

    """
    nonlocals.attribute1 = 3
    assert nonlocals.attribute1 == 3
    nonlocals['attribute1'] = 4
    assert nonlocals.attribute1 == 4

    nonlocals.prop2 = 3
    assert nonlocals.prop2 == 3
    nonlocals['prop2'] = 4
    assert nonlocals.prop2 == 4

    nonlocals.top = 1
    assert nonlocals.top == 1

    nonlocals.write_only = 1

    del nonlocals.attribute1
    assert nonlocals.attribute1 == 1

    with pytest.raises(AttributeError):
        nonlocals.prop1 = 1

    with pytest.raises(AttributeError):
        del nonlocals.unknown

    # write in the absence of an instance dict
    del nonlocals.owner.__dict__
    nonlocals.attribute1 = 3
    assert nonlocals.attribute1 == 3

    with pytest.raises(TypeError):
        nonlocals[1] = 1

    # Test setting a non-data descriptor
    nonlocals.owner = 1
    assert nonlocals.owner == 1


def test_nonlocals_call(dynamicscope, nonlocals):
    """Test calling a nonlocals to go up one level.

    """
    owner = dynamicscope[1][0]
    par_nonlocals = nonlocals(1)
    assert par_nonlocals.owner is owner._parent
    assert par_nonlocals.attribute1 == 1

    with pytest.raises(ValueError):
        nonlocals(level=2)

