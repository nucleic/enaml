#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import DefaultValue, Event, Instance

from .construct_node import ConstructNode
from .declarative import Declarative, d_
from .enamldef_meta import EnamlDefMeta
from .operators import __get_operators


def __add_storage(klass, name, store_type, kind):
    """ A compiler helper which adds user storage to a class.

    Parameters
    ----------
    klass : type
        The Declarative subclass to which storage is being added.

    name : str
        The name of the attribute or event to add to the class.

    store_type : type or None
        The type of values to allow on the attribute.

    kind : 'attr' or 'event'
        The kind of storage to add to the class.

    """
    if store_type is None:
        store_type = object
    elif not isinstance(store_type, type):
        raise TypeError("'%s' is not a type" % type(store_type).__name__)
    members = klass.members()
    m = members.get(name)
    if m is not None:
        if m.metadata is None or not m.metadata.get('d_member'):
            msg = "cannot override non-declarative member '%s'"
            raise TypeError(msg % name)
        if m.metadata.get('d_final'):
            msg = "cannot override the final member '%s'"
            raise TypeError(msg % name)
    if kind == 'event':
        new = d_(Event(store_type), writable=False, final=False)
    else:
        new = d_(Instance(store_type), final=False)
    if m is not None:
        new.set_index(m.index)
        new.copy_static_observers(m)
    else:
        new.set_index(len(members))
    new.set_name(name)
    members[name] = new
    setattr(klass, name, new)


def __construct_node(klass, identifier, scope_key):
    """ Create and return a ConstructNode for the given klass.

    Parameters
    ----------
    klass : type
        The resolved declarative class for the node.

    identifier : str
        The local string identifier to associate with instances.

    scope_key : object
        The key for the local scope in the local storage map.

    Returns
    -------
    result : ConstructNode
        A construct node for the given class.

    """
    node = ConstructNode()
    node.klass = klass
    node.identifier = identifier
    node.scope_key = scope_key

    # Copy the info from the superclass node, if any.
    super_node = getattr(klass, '__node__', None)
    if super_node is not None:
        node.supers = super_node.supers + [super_node]
        node.engine = super_node.engine.copy()

    return node


def __make_enamldef(name, bases, dct):
    """ Make an enamldef class for the given data.

    Parameters
    ----------
    name : str
        The name of the new enamldef.

    bases : tuple
        The tuple of base classes.

    dct : dict
        The class dictionary.

    """
    return EnamlDefMeta(name, bases, dct)


def __assert_d_member(klass, name, readable, writable):
    """ Assert binding points to a valid declarative member.

    Parameters
    ----------
    klass : Declarative
        The declarative class which owns the binding.

    name : str
        The name of the member on the class.

    readable : bool
        Whether the member should have the 'd_readable' metadata flag.

    writable : bool
        Whether the member should have the 'd_writable' metadata flag.

    """
    m = klass.members().get(name)
    if m is None or m.metadata is None or not m.metadata.get('d_member'):
        raise TypeError("'%s' is not a declarative member" % name)
    if readable and not m.metadata.get('d_readable'):
        raise TypeError("'%s' is not readable from enaml" % name)
    if writable and not m.metadata.get('d_writable'):
        raise TypeError("'%s' is not writable from enaml" % name)


def __read_op_dispatcher(owner, name):
    """ A default value handler which reads from a declarative engine.

    """
    return owner._d_engine.read(owner, name)


def __write_op_dispatcher(change):
    """ An observer which writes to a declarative engine.

    """
    t = change['type']
    if t == 'update' or t == 'event':
        owner = change['object']
        name = change['name']
        import time
        t1 = time.clock()
        owner._d_engine.write(owner, name, change)
        print time.clock() - t1

def __run_operator(node, name, op, code, f_globals):
    """ Run the operator for a given node.

    Parameters
    ----------
    node : ConstructNode
        The construct node holding the declarative class.

    name : str
        The name being bound for the class.

    op : str
        The operator string which should be run to create the handlers.

    code : CodeType
        The code object for the RHS expression.

    f_globals : dict
        The globals dictionary to pass to the operator.

    """
    operators = __get_operators()
    if op not in operators:
        raise TypeError("failed to load operator '%s'" % op)
    read, write = operators[op](code, node.scope_key, f_globals)
    # The read and write semantics are reversed here. In the context of
    # a declarative member, d_readable means that an attribute can be
    # *read* and it's value *written* to the expression, d_writable means
    # that an expression can be *read* and its value *written* to the
    # declarative attribute. This means that a write handler attempt to
    # read from the declarative attribute, and a read handler attempts to
    # write to the declarative attribute.
    __assert_d_member(node.klass, name, write is not None, read is not None)
    member = node.klass.members()[name]
    if read is not None:
        node.engine.read_handlers[name] = read
        mode = (DefaultValue.CallObject_ObjectName, __read_op_dispatcher)
        if member.default_value_mode != mode:
            clone = member.clone()
            clone.set_default_value_mode(*mode)
            node.klass.members()[name] = clone
            setattr(node.klass, name, clone)
    if write is not None:
        handlers = node.engine.write_handlers.get(name)
        if handlers is None:
            handlers = node.engine.write_handlers[name] = []
        handlers.append(write)
        if not member.has_observer(__write_op_dispatcher):
            clone = member.clone()
            clone.add_static_observer(__write_op_dispatcher)
            node.klass.members()[name] = clone
            setattr(node.klass, name, clone)


def __validate_type(klass):
    """ Validate that an object is a Declarative type.

    Parameters
    ----------
    klass : object
        The object to validate.

    """
    if not isinstance(klass, type):
        raise TypeError("%s is not a type" % klass)
    if not issubclass(klass, Declarative):
        raise TypeError("'%s' is not a Declarative type" % klass.__name__)
