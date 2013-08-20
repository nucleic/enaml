#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Event, Instance
from atom.datastructures.api import sortedmap

from .construct_node import ConstructNode
from .declarative import Declarative, d_
from .enamldef_meta import EnamlDefMeta
from .expression_engine import ExpressionEngine
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
    node.engine = ExpressionEngine(sortedmap(), sortedmap())
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
    engine = node.engine
    if read is not None:
        engine.read_handlers[name] = read
    if write is not None:
        handlers = engine.write_handlers.get(name)
        if handlers is None:
            handlers = engine.write_handlers[name] = []
        handlers.append(write)


def __validate_type(klass):
    """ Validate that an object is a Declarative subclass.

    Parameters
    ----------
    klass : object
        The object to validate.

    """
    if not isinstance(klass, type):
        raise TypeError("%s is not a type" % klass)
    if not issubclass(klass, Declarative):
        raise TypeError("'%s' is not a Declarative subclass" % klass.__name__)
