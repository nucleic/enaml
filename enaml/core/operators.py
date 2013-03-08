#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
""" The default Enaml operators.

The operator functions are called by the Enaml runtime to implement the
expression binding semantics of the Enaml operators. The functions are
passed a number of arguments in order to perform their work:

Parameters
----------
obj : Declarative
    The Declarative object which owns the expression which is being
    bound.

name : string
    The name of the attribute on the object which is being bound.

func : types.FunctionType
    A function with bytecode that has been patched by the Enaml compiler
    for semantics specific to the operator. The docs for each operator
    given a more complete description of this function, since it varies
    for each operator.

identifiers : dict
    The dictionary of identifiers available to the expression. This dict
    is shared amongst all expressions within a given lexical scope. It
    should therefore not be modified or copied since identifiers may
    continue to be added to this dict as runtime execution continues.

"""
from collections import namedtuple

from .declarative import DeclarativeExpression, DeclarativeProperty
from .dynamic_scope import DynamicScope, Nonlocals
from .funchelper import call_func
from .standard_inverter import StandardInverter
from .standard_tracer import StandardTracer


class OperatorBase(object):
    """ The base class of the standard Enaml operator implementations.

    """
    __slots__ = ('func', 'f_locals')

    def __init__(self, func, f_locals):
        """ Initialize a BaseExpression.

        Parameters
        ----------
        func : types.FunctionType
            A function created by the Enaml compiler with bytecode that
            has been patched to support the semantics required of the
            expression.

        f_locals : dict
            The dictionary of local identifiers for the function.

        """
        self.func = func
        self.f_locals = f_locals

    @property
    def name(self):
        """ Get the name to which the operator is bound.

        """
        return self.func.__name__


class OpSimple(OperatorBase):
    """ A class which implements the `=` operator.

    This class implements the `DeclarativeExpression` interface.

    """
    __slots__ = ()

    def evaluate(self, owner):
        """ Evaluate and return the expression value.

        """
        overrides = {'nonlocals': Nonlocals(owner, None), 'self': owner}
        scope = DynamicScope(owner, self.f_locals, overrides, None)
        with owner.operators:
            return call_func(self.func, (), {}, scope)


DeclarativeExpression.register(OpSimple)


NotificationEvent = namedtuple('NotificationEvent', 'obj name old new')


class OpNotify(OperatorBase):
    """ A class which implements the `::` operator.

    Instances of this class can be used as Atom observers.

    """
    __slots__ = ()

    def __call__(self, change):
        """ Called when the attribute on the owner has changed.

        """
        owner = change['object']
        nonlocals = Nonlocals(owner, None)
        event = NotificationEvent(
            owner, change['name'], change['oldvalue'], change['newvalue']
        )
        overrides = {
            'event': event,  # backwards compatibility
            'change': change, 'nonlocals': nonlocals, 'self': owner
        }
        scope = DynamicScope(owner, self.f_locals, overrides, None)
        with owner.operators:
            call_func(self.func, (), {}, scope)


class OpUpdate(OperatorBase):
    """ A class which implements the `>>` operator.

    Instances of this class can be used as Atom observers.

    """
    __slots__ = ()

    def __call__(self, change):
        """ Called when the attribute on the owner has changed.

        """
        owner = change['object']
        nonlocals = Nonlocals(owner, None)
        overrides = {'nonlocals': nonlocals, 'self': owner}
        inverter = StandardInverter(nonlocals)
        scope = DynamicScope(owner, self.f_locals, overrides, None)
        with owner.operators:
            call_func(self.func, (inverter, change['newvalue']), {}, scope)


class SubscriptionNotifier(object):
    """ A simple object used for attaching notification handlers.

    """
    __slots__ = ('notifier', 'name')

    def __init__(self, notifier, name):
        """ Initialize a SubscriptionNotifier.

        Parameters
        ----------
        notifier : callable
            A callable object provided by the Declarative owner which
            should be invoked when the expression is invalid. The name
            of the bound expression is passed as an argument.

        name : str
            The name to which the expression is bound.

        keyval : object
            An object to use for testing equivalency of notifiers.

        """
        self.notifier = notifier  # will be reset to None by OpSubscribe
        self.name = name

    def __nonzero__(self):
        """ The notifier is valid when it has an internal notifier.

        The atom observer mechanism will remove the observer when it
        tests boolean False. This removes the need to keep a weakref
        to the notifier.

        """
        return self.notifier is not None

    def __call__(self, change):
        """ The handler for the notification event.

        This will be invoked by the Atom observer mechanism when the
        item which is being observed changes.

        """
        self.notifier(self.name)


class OpSubscribe(OperatorBase):
    """ A class which implements the `<<` operator.

    This class implements the `DeclarativeExpression` interface.

    """
    __slots__ = 'notifier'

    def __init__(self, func, f_locals):
        """ Initialize a SubscriptionExpression.

        """
        super(OpSubscribe, self).__init__(func, f_locals)
        self.notifier = None

    def evaluate(self, owner):
        """ Evaluate and return the expression value.

        """
        tracer = StandardTracer()
        overrides = {'nonlocals': Nonlocals(owner, tracer), 'self': owner}
        scope = DynamicScope(owner, self.f_locals, overrides, tracer)
        with owner.operators:
            result = call_func(self.func, (tracer,), {}, scope)

        notifier = self.notifier
        if notifier is not None:
            notifier.notifier = None # invalidate the old notifier
        onotifier = owner._expression_notifier
        notifier = SubscriptionNotifier(onotifier, self.func.__name__)
        self.notifier = notifier
        for obj, name in tracer.traced_items:
            obj.observe(name, notifier)

        return result


DeclarativeExpression.register(OpSubscribe)


class OpDelegate(OpSubscribe):
    """ An expression and listener implementation for the `:=` operator.

    Instances of this class can by used at Atom notifiers.

    """
    __slots__ = ()

    def __call__(self, change):
        """ Called when the attribute on the owner has changed.

        """
        owner = change['object']
        nonlocals = Nonlocals(owner, None)
        inverter = StandardInverter(nonlocals)
        overrides = {'nonlocals': nonlocals, 'self': owner}
        scope = DynamicScope(owner, self.f_locals, overrides, None)
        with owner.operators:
            func = self.func._update
            call_func(func, (inverter, change['newvalue']), {}, scope)


# XXX generate a pseudo line number traceback for binding failures

def op_simple(obj, name, func, identifiers):
    """ The default Enaml operator function for `=` bindings.

    """
    member = obj.get_member(name)
    if not isinstance(member, DeclarativeProperty):
        msg = "Cannot bind expression. '%s' is not a declarative property "
        msg += "on a '%s' object."
        raise TypeError(msg % (name, type(obj).__name__))
    obj._expressions.append(OpSimple(func, identifiers))


def op_notify(obj, name, func, identifiers):
    """ The default Enaml operator function for `::` bindings.

    """
    member = obj.get_member(name)
    if member is None:
        msg = "Cannot bind expression. '%s' is not an observable member "
        msg += "on the '%s' object."
        raise TypeError(msg % (name, type(obj).__name__))
    obj.observe(name, OpNotify(func, identifiers))


def op_update(obj, name, func, identifiers):
    """ The default Enaml operator function for `>>` bindings.

    """
    member = obj.get_member(name)
    if member is None:
        msg = "Cannot bind expression. '%s' is not an observable member "
        msg += "on the '%s' object."
        raise TypeError(msg % (name, type(obj).__name__))
    obj.observe(name, OpUpdate(func, identifiers))


def op_subscribe(obj, name, func, identifiers):
    """ The default Enaml operator function for `<<` bindings.

    """
    member = obj.get_member(name)
    if not isinstance(member, DeclarativeProperty):
        msg = "Cannot bind expression. '%s' is not a declarative property "
        msg += "on a '%s' object."
        raise TypeError(msg % (name, type(obj).__name__))
    obj._expressions.append(OpSubscribe(func, identifiers))


def op_delegate(obj, name, func, identifiers):
    """ The default Enaml operator function for `:=` bindings.

    """
    member = obj.get_member(name)
    if not isinstance(member, DeclarativeProperty):
        msg = "Cannot bind expression. '%s' is not a declarative property "
        msg += "on a '%s' object."
        raise TypeError(msg % (name, type(obj).__name__))
    expr = OpDelegate(func, identifiers)
    obj._expressions.append(expr)
    obj.observe(name, expr)


OPERATORS = {
    '__operator_Equal__': op_simple,
    '__operator_LessLess__': op_subscribe,
    '__operator_ColonEqual__': op_delegate,
    '__operator_ColonColon__': op_notify,
    '__operator_GreaterGreater__': op_update,
}

