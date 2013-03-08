#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod, abstractproperty

from atom.api import (
    Member, Validate, DefaultValue, ReadOnly, Value, Event, List, Str, null
)

#from .dynamic_scope import DynamicAttributeError
from .exceptions import DeclarativeNameError, OperatorLookupError
from .object import Object, flag_generator, flag_property
from .operator_context import OperatorContext


class DeclarativeProperty(Member):
    """ A custom member which enables data binding in Enaml.

    A declarative property is used to wrap another member on an Atom
    subclass to enable that member to be bound by Enaml syntax. The
    declarative property will compute the default value using a bound
    expression. If that fails, the wrapped member will be used to get
    the default value. Validation is performed by the wrapped member
    unless overridden by the user.

    """
    __slots__ = 'delegate'

    def __init__(self, delegate):
        """ Initialize a DeclarativeProperty.

        Parameters
        ----------
        delegate : Member
            The Atom Member which provides the behavior for the property.
            The member should use standard slot behavior semantics.

        """
        self.delegate = delegate
        self.set_validate_mode(Validate.Delegate, delegate)
        super(DeclarativeProperty, self).set_default_value_mode(
            DefaultValue.MemberMethod_Object, "default_value"
        )

    def set_name(self, name):
        """ Assign the name to this member.

        This method keeps the name of the delegate member in sync.

        """
        super(DeclarativeProperty, self).set_name(name)
        self.delegate.set_name(name)

    def set_index(self, index):
        """ Assign the index to this member.

        This method keeps the index of the delegate member in sync.

        """
        super(DeclarativeProperty, self).set_index(index)
        self.delegate.set_index(index)

    def set_default_value_mode(self, mode, context):
        """ Set the default value mode for the member.

        The default value mode of a DeclarativeProperty cannot be
        changed. This method proxies the call to the internal delegate
        which will be used for the default value if there is no bound
        expression for the property.

        """
        self.delegate.set_default_value_mode(mode, context)

    def clone(self):
        """ Create a clone of the declarative property.

        This method also creates a clone of the internal delegate.

        """
        clone = super(DeclarativeProperty, self).clone()
        delegate = self.delegate
        clone.delegate = delegate_clone = delegate.clone()
        mode, old = clone.validate_mode
        if old is delegate:
            clone.set_validate_mode(mode, delegate_clone)
        return clone

    def default_value(self, owner):
        """ Compute the default value for the declarative property.

        The default is retrieved from a bound expression first,
        followed by the internal delegate.

        """
        value = owner.evaluate_expression(self.name)
        if value is null:
            value = self.delegate.do_default_value(owner)
        return value


#: Export the DeclarativeProperty class as something easier to type.
d_ = DeclarativeProperty


class DeclarativeExpression(object):
    """ An interface for defining declarative expressions.

    Then Enaml operators are responsible for assigning an expression to
    the data struct of the relevant `DeclarativeProperty`.

    """
    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        """ Get the name to which the expression is bound.

        """
        raise NotImplementedError

    @abstractmethod
    def evaluate(self, owner):
        """ Evaluate and return the results of the expression.

        Parameters
        ----------
        owner : Declarative
            The declarative object which owns the expression.

        """
        raise NotImplementedError


class ExpressionNotifier(object):
    """ A simple notifier object used by Declarative.

    DeclarativeExpression objects which are bound to a declarative will
    use this notifier to notify the declarative when their expression
    is invalid and should be recomputed.

    """
    __slots__ = 'owner'

    def __init__(self, owner):
        """ Initialize an ExpressionNotifier.

        Parameters
        ----------
        owner : Declarative
            The declarative object which owns this notifier.

        """
        # The strong internal reference cycle is deliberate. It will be
        # cleared during the `destroy` method of the Declarative.
        self.owner = owner

    def __call__(self, name):
        """ Notify the declarative owner that the expression is invalid.

        Parameters
        ----------
        name : str
            The name of the expression which is invalid.

        """
        owner = self.owner
        if owner is not None:
            setattr(owner, name, owner.evaluate_expression(name))


def scope_lookup(name, scope, description):
    """ A function which retrieves a name from a scope.

    If the lookup fails, a DeclarativeNameError is raised. This can
    be used to lookup names for a description dict from a global scope
    with decent error reporting when the lookup fails.

    Parameters
    ----------
    name : str
        The name to retreive from the scope.

    scope : mapping
        A mapping object.

    description : dict
        The description dictionary associated with the lookup.

    """
    try:
        item = scope[name]
    except KeyError:
        lineno = description['lineno']
        filename = description['filename']
        block = description['block']
        raise DeclarativeNameError(name, filename, lineno, block)
    return item


#: The flag indicating that the Declarative object has been initialized.
INITIALIZED_FLAG = flag_generator.next()


class Declarative(Object):
    """ The most base class of the Enaml declarative objects.

    This class provides the core functionality required of declarative
    Enaml types. It can be used directly in a declarative Enaml object
    tree to store and react to state changes. It has no concept of a
    visual representation; that functionality is added by subclasses.

    """
    #: Redefine `name` as a declarative property.
    name = d_(Str())

    #: The operator context used to build out this instance. This is
    #: assigned during object instantiation.
    operators = ReadOnly()

    #: A property which gets and sets the initialized flag. This should
    #: not be manipulated directly by user code.
    is_initialized = flag_property(INITIALIZED_FLAG)

    #: An event fired when an object is initialized. It is triggered
    #: once during the object lifetime, at the end of the initialize
    #: method.
    initialized = Event()

    #: The list of value-providing subscription expressions for the
    #: object. The operators will append expressions to this list
    #: as-needed.
    _expressions = List()

    #: An object which is used by the operators to notify this object
    #: when a bound expression has been invalidated. This should not
    #: be manipulated by user code.
    _expression_notifier = Value()
    def _default__expression_notifier(self):
        return ExpressionNotifier(self)

    #: Seed the class heirarchy with an empty descriptions tuple. The
    #: enaml compiler machinery will populate this for each enamldef.
    __declarative_descriptions__ = ()

    def __init__(self, parent=None, **kwargs):
        """ Initialize a declarative component.

        Parameters
        ----------
        parent : Object or None, optional
            The Object instance which is the parent of this object, or
            None if the object has no parent. Defaults to None.

        **kwargs
            Additional keyword arguments needed for initialization.

        """
        self.operators = OperatorContext.active_context()
        super(Declarative, self).__init__(parent, **kwargs)
        descriptions = self.__declarative_descriptions__
        if len(descriptions) > 0:
            # Each description is an independent `enamldef` block
            # which gets its own independent identifiers scope.
            for description, f_globals in descriptions:
                identifiers = {}
                self.populate(description, identifiers, f_globals)

    def initialize(self):
        pass

    def destroy(self):
        """ An overridden destructor method for declarative cleanup.

        """
        del self._expressions
        self._expression_notifier.owner = None  # break the ref cycle
        del self._expression_notifier
        super(Declarative, self).destroy()

    def populate(self, description, identifiers, f_globals):
        """ Populate this declarative instance from a description.

        This method is called when the object was created from within
        a declarative context. In particular, there are two times when
        it may be called:

            - The first is when a type created from the `enamldef`
              keyword is instatiated; in this case, the method is
              invoked by the Declarative constructor.

            - The second occurs when the object is instantiated by
              its parent from within its parent's `populate` method.

        In the first case, the description dict will contain the key
        `enamldef: True`, indicating that the object is being created
        from a "top-level" `enamldef` block.

        In the second case, the dict will have the key `enamldef: False`
        indicating that the object is being populated as a declarative
        child of some other parent.

        Subclasses may reimplement this method to gain custom control
        over how the children for its instances are created.

        *** This method may be called multiple times ***

        Consider the following sample:

        enamldef Foo(PushButton):
            text = 'bar'

        enamldef Bar(Foo):
            fgcolor = 'red'

        enamldef Main(Window):
            Container:
                Bar:
                    bgcolor = 'blue'

        The instance of `Bar` which is created as the `Container` child
        will have its `populate` method called three times: the first
        to populate the data from the `Foo` block, the second to populate
        the data from the `Bar` block, and the third to populate the
        data from the `Main` block.

        Parameters
        ----------
        description : dict
            The description dictionary for the instance.

        identifiers : dict
            The dictionary of identifiers to use for the bindings.

        f_globals : dict
            The dictionary of globals for the scope in which the object
            was declared.

        """
        ident = description['identifier']
        if ident:
            identifiers[ident] = self
        bindings = description['bindings']
        if len(bindings) > 0:
            self.setup_bindings(bindings, identifiers, f_globals)
        children = description['children']
        if len(children) > 0:
            for child in children:
                cls = scope_lookup(child['type'], f_globals, child)
                instance = cls(self)
                instance.populate(child, identifiers, f_globals)

    def setup_bindings(self, bindings, identifiers, f_globals):
        """ Setup the expression bindings for the object.

        Parameters
        ----------
        bindings : list
            A list of binding dicts created by the enaml compiler.

        identifiers : dict
            The identifiers scope to associate with the bindings.

        f_globals : dict
            The globals dict to associate with the bindings.

        """
        operators = self.operators
        for binding in bindings:
            opname = binding['operator']
            try:
                operator = operators[opname]
            except KeyError:
                filename = binding['filename']
                lineno = binding['lineno']
                block = binding['block']
                raise OperatorLookupError(opname, filename, lineno, block)
            operator(self, binding['name'], binding['func'], identifiers)

    def evaluate_expression(self, name):
        """ Evaluate an expression bound to this declarative object.

        Parameters
        ----------
        name : str
            The name of the declarative property to which the expression
            is bound.

        Returns
        -------
        result : object or null
            The result of the evaluated expression, or null if there
            is no expression bound for the given name.

        """
        # The operators will append all expressions to this list, so
        # the list is iterated in reverse order to use the expression
        # which was most recently bound.
        for expression in reversed(self._expressions):
            if expression.name == name:
                return expression.evaluate(self)
        return null
