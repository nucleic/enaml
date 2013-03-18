#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import DefaultValue

from .dynamic_scope import DynamicScope, Nonlocals
from .exceptions import DeclarativeError
from .funchelper import call_func
from .standard_inverter import StandardInverter
from .standard_tracer import StandardTracer


class OperatorBase(object):
    """ The base class of the standard Enaml operator implementations.

    """
    __slots__ = 'binding'

    def __init__(self, binding):
        """ Initialize an OperatorBase.

        Parameters
        ----------
        binding : dict
            The dict created by the compiler which represents the
            operator binding.

        """
        self.binding = binding

    def get_locals(self, owner):
        """ Get the local scope for this operator and owner.

        Parameters
        ----------
        owner : Declarative
            The declarative object of interest.

        """
        scopename = self.binding['scopename']
        if scopename:
            return getattr(owner, scopename)
        return {}

    def release(self, owner):
        """ Release any resources held for the given owner.

        This method is called by a declarative object when it is being
        destroyed. It provides an opportunity for the operator to clean
        up any owner-specific state it may be holding. By default, this
        method is a no-op.

        Parameters
        ----------
        owner : Declarative
            The declarative object being destroyed.

        """
        pass


class OpSimple(OperatorBase):
    """ An operator class which implements the `=` operator semantics.

    """
    __slots__ = ()

    def eval(self, owner):
        """ Evaluate and return the expression value.

        This method is called by the '_run_eval_operator()' method on
        a Declarative instance.

        Parameters
        ----------
        owner : Declarative
            The declarative object requesting the evaluation.

        """
        overrides = {'nonlocals': Nonlocals(owner, None), 'self': owner}
        f_locals = self.get_locals(owner)
        func = self.binding['func']
        scope = DynamicScope(
            owner, f_locals, overrides, func.func_globals, None
        )
        return call_func(func, (), {}, scope)


class OpNotify(OperatorBase):
    """ An operator class which implements the `::` operator semantics.

    """
    __slots__ = ()

    def notify(self, change):
        """ Run the notification code bound to the operator.

        This method is called by the '_run_notify_operator()' method on
        a Declarative instance.

        Parameters
        ----------
        change : dict
            The change dict for the change on the requestor.

        """
        owner = change['object']
        nonlocals = Nonlocals(owner, None)
        overrides = {'change': change, 'nonlocals': nonlocals, 'self': owner}
        f_locals = self.get_locals(owner)
        func = self.binding['func']
        scope = DynamicScope(
            owner, f_locals, overrides, func.func_globals, None
        )
        call_func(func, (), {}, scope)


class OpUpdate(OperatorBase):
    """ An operator class which implements the `>>` operator semantics.

    """
    __slots__ = ()

    def notify(self, change):
        """ Run the notification code bound to the operator.

        This method is called by the '_run_notify_operator()' method on
        a Declarative instance.

        Parameters
        ----------
        change : dict
            The change dict for the change on the requestor.

        """
        owner = change['object']
        nonlocals = Nonlocals(owner, None)
        overrides = {'nonlocals': nonlocals, 'self': owner}
        inverter = StandardInverter(nonlocals)
        f_locals = self.get_locals(owner)
        func = self.binding['func']
        scope = DynamicScope(
            owner, f_locals, overrides, func.func_globals, None
        )
        if change['type'] == 'event':
            value = change['value']
        else:
            value = change['newvalue']
        call_func(func, (inverter, value), {}, scope)


class SubscriptionObserver(object):
    """ An observer used to listen for changes in "<<" expressions.

    Instances of this class are created and managed by the OpSubscribe
    class when the operator is evaluated and traced.

    """
    __slots__ = ('owner', 'name')

    def __init__(self, owner, name):
        """ Initialize a SubscriptionObserver.

        Parameters
        ----------
        owner : Declarative
            The declarative owner of interest.

        name : str
            The name to which the operator is bound.

        """
        self.owner = owner  # will be reset to None by OpSubscribe
        self.name = name

    def __nonzero__(self):
        """ The notifier is valid when it has an internal owner.

        The atom observer mechanism will remove the observer when it
        tests boolean False. This removes the need to keep a weakref
        to the owner.

        """
        return self.owner is not None

    def __call__(self, change):
        """ The handler for the change notification.

        This will be invoked by the Atom observer mechanism when the
        item which is being observed changes.

        """
        owner = self.owner
        if owner is not None:
            name = self.name
            setattr(owner, name, owner._run_eval_operator(name))


class OpSubscribe(OperatorBase):
    """ An operator class which implements the `<<` operator semantics.

    """
    __slots__ = 'observers'

    def __init__(self, binding):
        """ Initialize a subscription operator.

        """
        super(OpSubscribe, self).__init__(binding)
        self.observers = {}

    def release(self, owner):
        """ Release the resources held for the given owner.

        """
        observer = self.observers.pop(owner, None)
        if observer is not None:
            observer.owner = None

    def eval(self, owner):
        """ Evaluate and return the expression value.

        """
        tracer = StandardTracer()
        overrides = {'nonlocals': Nonlocals(owner, tracer), 'self': owner}
        f_locals = self.get_locals(owner)
        func = self.binding['func']
        scope = DynamicScope(
            owner, f_locals, overrides, func.func_globals, tracer
        )
        result = call_func(func, (tracer,), {}, scope)

        # Invalidate the old observer and create a new observer which
        # is subscribed to the traced dependencies in the expression.
        observers = self.observers
        if owner in observers:
            observers[owner].owner = None
        observer = SubscriptionObserver(owner, self.binding['name'])
        observers[owner] = observer
        for obj, name in tracer.traced_items:
            obj.observe(name, observer)

        return result


class OpDelegate(OpSubscribe):
    """ An operator class which implements the `:=` operator semantics.

    """
    __slots__ = ()

    def notify(self, change):
        """ Run the notification code bound to the operator.

        This method is called by the '_run_notify_operator()' method on
        a Declarative instance.

        Parameters
        ----------
        change : dict
            The change dict for the change on the requestor.

        """
        owner = change['object']
        nonlocals = Nonlocals(owner, None)
        inverter = StandardInverter(nonlocals)
        overrides = {'nonlocals': nonlocals, 'self': owner}
        f_locals = self.get_locals(owner)
        func = self.binding['func2']
        scope = DynamicScope(
            owner, f_locals, overrides, func.func_globals, None
        )
        call_func(func, (inverter, change['newvalue']), {}, scope)


def assert_d_member(klass, binding, readable, writable):
    """ Assert binding points to a valid declarative member.

    Parameters
    ----------
    klass : Declarative
        The declarative class which owns the binding.

    binding : dict
        The binding dict created by the enaml compiler.

    readable : bool
        Whether the member should have the 'd_readable' metadata flag.

    writable : bool
        Whether the member should have the 'd_writable' metadata flag.

    Returns
    -------
    result : tuple
        A 2-tuple of (name, member) on which the binding should operate.

    Raises
    ------
    DeclarativeError
        This will be raised if the member is not valid for the spec.

    """
    members = klass.members()
    name = binding['name']
    m = members.get(name)
    if m is None or m.metadata is None or not m.metadata.get('d_member'):
        message = "'%s' is not a declarative member" % name
        raise DeclarativeError(message, binding)
    if readable and not m.metadata.get('d_readable'):
        message = "'%s' is not readable from enaml" % name
        raise DeclarativeError(message, binding)
    if writable and not m.metadata.get('d_writable'):
        message = "'%s' is not writable from enaml" % name
        raise DeclarativeError(message, binding)
    return (name, m)


def bind_read_operator(klass, binding, operator):
    """ Bind a readable operator for the binding to the given klass.

    Parameters
    ----------
    klass : Declarative
        The declarative class which owns the binding.

    binding : dict
        The binding dict created by the enaml compiler.

    operator : object
        The operator to bind to the class.

    """
    name, member = assert_d_member(klass, binding, True, False)
    klass._notify_operators().setdefault(name, []).append(operator)
    member.add_static_observer('_run_notify_operator')


def bind_write_operator(klass, binding, operator):
    """ Bind a writable operator for the binding to the given klass.

    Parameters
    ----------
    klass : Declarative
        The declarative class which owns the binding.

    binding : dict
        The binding dict created by the enaml compiler.

    operator : object
        The operator to bind to the class.

    """
    name, member = assert_d_member(klass, binding, False, True)
    klass._eval_operators()[name] = operator
    mode = (DefaultValue.ObjectMethod_Name, '_run_eval_operator')
    if member.default_value_mode != mode:
        clone = member.clone()
        clone.set_default_value_mode(*mode)
        klass.members()[name] = clone
        setattr(klass, name, clone)


def op_simple(klass, binding):
    """ The default Enaml operator function for the `=` operator.

    """
    bind_write_operator(klass, binding, OpSimple(binding))


def op_notify(klass, binding):
    """ The default Enaml operator function for the `::` operator.

    """
    bind_read_operator(klass, binding, OpNotify(binding))


def op_update(klass, binding):
    """ The default Enaml operator function for the `>>` operator.

    """
    bind_read_operator(klass, binding, OpUpdate(binding))


def op_subscribe(klass, binding):
    """ The default Enaml operator function for the `<<` operator.

    """
    bind_write_operator(klass, binding, OpSubscribe(binding))


def op_delegate(klass, binding):
    """ The default Enaml operator function for the `:=` operator.

    """
    operator = OpDelegate(binding)
    bind_read_operator(klass, binding, operator)
    bind_write_operator(klass, binding, operator)


DEFAULT_OPERATORS = {
    '=': op_simple,
    '::': op_notify,
    '>>': op_update,
    '<<': op_subscribe,
    ':=': op_delegate,
}
