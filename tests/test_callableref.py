# ------------------------------------------------------------------------------
# Copyright (c) 2020, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ------------------------------------------------------------------------------
import gc
from weakref import ref

import pytest

from enaml.callableref import CallableRef
from enaml.weakmethod import WeakMethod

class CObj:
    def __init__(self):
        self.counter = 0
        self.last_args = None
        self.last_kwargs = None

    def __call__(self, *args, **kwargs):
        self.counter += 1
        self.last_args = args
        self.last_kwargs = kwargs
        return 1


def test_callableref_lifetime():
    """Test creating a callable ref and calling it before and after the object death.

    """
    obj = CObj()
    cr = CallableRef(obj)
    assert cr(1, 2, a=1, b=2) == 1
    assert obj.counter == 1
    assert obj.last_args == (1, 2)
    assert obj.last_kwargs == dict(a=1, b=2)

    del obj
    gc.collect()
    assert cr() is None


def test_callableref_call():
    """Test calling a callable ref with different args/kwargs.

    """
    obj = CObj()
    cr = CallableRef(obj)
    cr()
    assert obj.counter == 1
    assert obj.last_args == ()
    assert obj.last_kwargs == {}

    cr(1, 2)
    assert obj.counter == 2
    assert obj.last_args == (1, 2)
    assert obj.last_kwargs == {}

    cr(a=1, b=2)
    assert obj.counter == 3
    assert obj.last_args == ()
    assert obj.last_kwargs == dict(a=1, b=2)


def test_callableref_call_weakmethod():
    """Test calling a callable ref with different args/kwargs.

    """
    obj = CObj()
    cr = CallableRef(WeakMethod(obj.__call__))
    cr()
    assert obj.counter == 1
    assert obj.last_args == ()
    assert obj.last_kwargs == {}

    cr(1, 2)
    assert obj.counter == 2
    assert obj.last_args == (1, 2)
    assert obj.last_kwargs == {}

    cr(a=1, b=2)
    assert obj.counter == 3
    assert obj.last_args == ()
    assert obj.last_kwargs == dict(a=1, b=2)


def test_callableref_callback():
    """Test that callback are properly sets.

    """
    obj = CObj()
    cb = CObj()
    cr = CallableRef(obj, cb)

    del obj
    gc.collect()
    assert cr() is None
    assert cb.counter == 1


def test_callableref_comparison():
    """Test comparison of CallableRef.

    """
    obj1 = CObj()
    obj2 = CObj()
    cr1 = CallableRef(obj1)
    cr1_2 = CallableRef(obj1)
    cr2 = CallableRef(obj2)

    assert cr1 == cr1_2
    assert cr1 != cr2
    assert cr1 == ref(obj1)
    assert cr1 != ref(obj2)
    assert cr1 != None

    with pytest.raises(TypeError):
        cr1 > cr2
