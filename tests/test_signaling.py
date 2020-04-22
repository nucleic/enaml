#------------------------------------------------------------------------------
# Copyright (c) 2020, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import gc

import pytest

from enaml.signaling import Signal, BoundSignal


class SignalTester:

    signal = Signal()

    def __init__(self):
        self.counter = 0
        self.last_args = None
        self.last_kwargs = None

    def slot(self, *args, **kwargs):
        self.counter += 1
        self.last_args = args
        self.last_kwargs = kwargs


def test_signal_bound_method():
    """Test creating, connecting, emitting and disconnecting a signal.

    """
    s = SignalTester()
    bs1 = s.signal
    bs2 = s.signal
    assert bs1 is not bs2
    assert isinstance(bs1, BoundSignal)

    s.signal.connect(s.slot)
    bs1.connect(s.slot)
    bs2.connect(s.slot)

    s.signal.emit(1, 2, 3)
    assert s.counter == 3
    assert s.last_args == (1, 2, 3)
    assert s.last_kwargs == {}

    s.signal.disconnect(s.slot)

    s.signal(4, 5, c=5, h=6)
    assert s.counter == 5
    assert s.last_args == (4, 5)
    assert s.last_kwargs == dict(c=5, h=6)

    s.signal.disconnect(s.slot)
    s.signal(a=1)
    assert s.counter == 6
    assert s.last_args == ()
    assert s.last_kwargs == dict(a=1)

    s.signal.disconnect(s.slot)
    s.signal()
    assert s.counter == 6


def test_signal_disconnect_all():
    """Test disconnecting all slots connected the bound signals.

    """
    c = 0
    last_args = ()
    last_kwargs = {}
    def dummy_slot(*args, **kwargs):
        nonlocal c, last_args, last_kwargs
        c += 1
        last_args = args
        last_kwargs = kwargs

    s = SignalTester()
    s.signal.connect(s.slot)
    s.signal(4, 5, c=5, h=6)
    assert s.counter == 1

    s.signal.connect(dummy_slot)
    s.signal.emit()
    assert s.counter == 2
    assert c == 1
    assert last_args == ()
    assert last_kwargs == dict()

    s.signal.emit(1, 2)
    assert s.counter == 3
    assert c == 2
    assert last_args == (1, 2)
    assert last_kwargs == dict()

    s.signal.emit(a=1)
    assert s.counter == 4
    assert c == 3
    assert last_args == ()
    assert last_kwargs == dict(a=1)

    s.signal.emit(1, a=1)
    assert s.counter == 5
    assert c == 4
    assert last_args == (1,)
    assert last_kwargs == dict(a=1)

    SignalTester.signal.disconnect_all(s)
    s.signal.emit()
    assert s.counter == 5
    assert c == 4


def test_signal_bad_creation():
    """Test handling bad arguments to Signal.

    """
    with pytest.raises(TypeError):
        Signal(1)

    with pytest.raises(TypeError):
        Signal(a=1)


def test_signal_set_del():
    """Test setting/deleting a signal

    """
    s = SignalTester()
    with pytest.raises(AttributeError):
        s.signal = 1

    s = SignalTester()
    s.signal.connect(s.slot)
    s.signal(4, 5, c=5, h=6)
    assert s.counter == 1

    del s.signal
    s.signal.emit()
    assert s.counter == 1


def test_bound_signal_comparison():
    """Test comparing different bound signals.

    """
    s = SignalTester()
    assert s.signal == s.signal


def test_manual_bound_signal_creation():
    """Test creating manually a BoundSignal.

    """
    s = SignalTester()
    with pytest.raises(TypeError):
        sb = BoundSignal(SignalTester.signal, s)

    import weakref
    sb = BoundSignal(SignalTester.signal, weakref.WeakMethod(s.slot))
