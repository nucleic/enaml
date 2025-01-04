# ------------------------------------------------------------------------------
# Copyright (c) 2025, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ------------------------------------------------------------------------------
import pytest
from atom.api import Atom, Value
from enaml.widgets.api import Label
from enaml.core.subscription_observer import SubscriptionObserver


def test_subscription_observer_ref():
    label = Label()
    observer = SubscriptionObserver(label, "text")
    assert bool(observer)
    assert observer.name == "text"
    assert observer.ref() is label
    observer.ref = None
    assert not bool(observer)


def test_subscription_observer_new():
    label = Label()
    with pytest.raises(TypeError):
        observer = SubscriptionObserver(label, 0)

    with pytest.raises(TypeError):
        observer = SubscriptionObserver(None, "")


def test_subscription_observer_compare():
    label = Label()
    observer = SubscriptionObserver(label, "text")
    assert observer != SubscriptionObserver(label, "style")
    assert observer == SubscriptionObserver(label, "text")


def test_subscription_observer_update():
    class Engine(Atom):
        owner = Value()
        name = Value()

        def update(self, owner, name):
            self.owner = owner
            self.name = name

    class Owner(Atom):
        _d_engine = Value()

    engine = Engine()
    owner = Owner(_d_engine=engine)

    observer = SubscriptionObserver(owner, "text")
    observer()
    assert engine.owner is owner
    assert engine.name is "text"
