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
from .expression_engine import ExpressionEngine
from .operators import __get_operators


def __add_storage(klass, name, store_type, kind):
    """ Add user storage to a Declarative subclass.

    Parameters
    ----------
    klass : type
        The Declarative subclass to which storage should be added.

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
        raise TypeError("%s is not a type" % store_type)

    members = klass.members()
    member = members.get(name)
    if member is not None:
        if member.metadata is None or not member.metadata.get('d_member'):
            msg = "cannot override non-declarative member '%s'"
            raise TypeError(msg % name)
        if member.metadata.get('d_final'):
            msg = "cannot override the final member '%s'"
            raise TypeError(msg % name)

    if kind == 'event':
        new = d_(Event(store_type), writable=False, final=False)
    else:
        new = d_(Instance(store_type), final=False)

    if member is not None:
        new.set_index(member.index)
        new.copy_static_observers(member)
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
    # copy over the superclass nodes, if any
    s_node = getattr(klass, '__node__', None)
    if s_node is not None:
        node.super_nodes = s_node.super_nodes + [s_node]
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


def __make_engine(klass):
    """ Make the expression engine for the class.

    Parameters
    ----------
    klass : type
        The Declarative class which should be given an engine.

    """
    engine = getattr(klass, '__engine__', None)
    if engine is not None:
        return engine.copy()
    return ExpressionEngine()


def __read_op_dispatcher(owner, name):
    """ A default value handler which reads from a declarative engine.

    """
    return type(owner).__engine__.read(owner, name)


def __write_op_dispatcher(change):
    """ An observer which writes to a declarative engine.

    """
    change_t = change['type']
    if change_t == 'update' or change_t == 'event':
        owner = change['object']
        type(owner).__engine__.write(owner, change['name'], change)


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
    scope_key = node.scope_key
    read, write = operators[op](code, scope_key, f_globals)

    # The read and write semantics are reversed here. In the context of
    # a declarative member, d_readable means that an attribute can be
    # *read* from enaml and it's value *written* to the expression,
    # d_writable means that an expression can be *read* and its value
    # *written* to the attribute attribute.
    klass = node.klass
    member = klass.members().get(name)
    if (member is None or
        member.metadata is None or
        not member.metadata.get('d_member')):
        raise TypeError("'%s' is not a declarative member" % name)
    if write is not None and not member.metadata.get('d_readable'):
        raise TypeError("'%s' is not readable from enaml" % name)
    if read is not None and not member.metadata.get('d_writable'):
        raise TypeError("'%s' is not writable from enaml" % name)

    engine = klass.__engine__
    if read is not None:
        engine.read_handlers[name] = read
        mode = (DefaultValue.CallObject_ObjectName, __read_op_dispatcher)
        if member.default_value_mode != mode:
            member = member.clone()
            member.set_default_value_mode(*mode)
            klass.members()[name] = member
            setattr(klass, name, member)

    if write is not None:
        handlers = engine.write_handlers.get(name)
        if handlers is None:
            handlers = engine.write_handlers[name] = []
        handlers.append(write)
        if not member.has_observer(__write_op_dispatcher):
            member = member.clone()
            member.add_static_observer(__write_op_dispatcher)
            klass.members()[name] = member
            setattr(klass, name, member)


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
