#------------------------------------------------------------------------------
# Copyright (c) 2020, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import gc

import pytest

from enaml.weakmethod import WeakMethod

class CObj:
    def __init__(self):
        self.counter = 0
        self.last_args = ()
        self.last_kwargs = {}

    def meth(self, *args, **kwargs):
        self.counter += 1
        self.last_args = args
        self.last_kwargs = kwargs
        return 1


def test_weakmethod_lifetime():
    """Test WeakMethod lifetime.

    """
    obj = CObj()
    wm = WeakMethod(obj.meth)
    assert wm is WeakMethod(obj.meth)
    assert wm(1, 2, a=2, b=3) == 1
    assert obj.counter == 1
    assert obj.last_args == (1, 2)
    assert obj.last_kwargs == dict(a=2, b=3)

    del obj
    gc.collect()
    assert wm() is None


def test_handling_bad_arguments():
    """Test handling bad arguments to WeakMethod.

    """
    with pytest.raises(TypeError) as exc:
        WeakMethod(a=1)
    assert "keyword" in exc.value.args[0]

    with pytest.raises(TypeError) as exc:
        WeakMethod(1, 2)
    assert "1 argument" in exc.value.args[0]

    with pytest.raises(TypeError) as exc:
        WeakMethod()
    assert "1 argument" in exc.value.args[0]

    with pytest.raises(TypeError) as exc:
        WeakMethod(CObj.meth)
    assert "MethodType" in exc.value.args[0]
