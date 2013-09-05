#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Event, Instance

from .compiler_nodes import DeclarativeNode, EnamlDefNode
from .declarative import Declarative, d_
from .enamldef_meta import EnamlDefMeta
from .expression_engine import ExpressionEngine
from .operators import __get_operators
from .static import Static
from .template import Template


def add_static_attr(klass, name, value):
    """ Add a static attribute to a class.

    Parameters
    ----------
    klass : type
        The declarative class to which the attribute should be added.

    name : str
        The name of the attribute to add.

    value : object
        The value of the static attribute.

    """
    if hasattr(klass, name):
        msg = "cannot override '%s' with static attribute"
        raise TypeError(msg % name)
    setattr(klass, name, Static(name, value))


def add_storage(klass, name, store_type, kind):
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
    elif kind == 'attr':
        new = d_(Instance(store_type), final=False)
    else:
        raise RuntimeError("invalid kind '%s'" % kind)

    if member is not None:
        new.set_index(member.index)
        new.copy_static_observers(member)
    else:
        new.set_index(len(members))

    new.set_name(name)
    members[name] = new
    setattr(klass, name, new)


def declarative_node(klass, identifier, scope_key):
    """ Create and return a DeclarativeNode for the given klass.

    Parameters
    ----------
    klass : type
        The resolved declarative class for the node.

    identifier : str
        The local string identifier to associate with instances.

    scope_key : object
        The key for the local scope in the local storage maps.

    Returns
    -------
    result : DeclarativeNode
        The compiler node for the given klass.

    """
    node = DeclarativeNode()
    node.klass = klass
    node.identifier = identifier
    node.scope_key = scope_key
    # If the class is an enamldef, the engine must be copied
    s_node = getattr(klass, '__node__', None)
    if s_node is not None and s_node.engine is not None:
        node.engine = s_node.engine.copy()
    return node


def enamldef_node(klass, identifier, scope_key):
    """ Create and return an EnamlDefNode for the given class.

    Parameters
    ----------
    klass : type
        The resolved declarative class for the node.

    identifier : str
        The local string identifier to associate with instances.

    scope_key : object
        The key for the local scope in the local storage maps.

    Returns
    -------
    result : EnamlDefNode
        The compiler node for the given class.

    """
    node = EnamlDefNode()
    node.klass = klass
    node.identifier = identifier
    node.scope_key = scope_key
    # Copy over the data from the supernode.
    s_node = getattr(klass, '__node__', None)
    if s_node is not None:
        node.super_nodes = s_node.super_nodes + [s_node]
        if s_node.engine is not None:
            node.engine = s_node.engine.copy()
    return node


def template_node(scope_key, has_locals):
    """ Create and return a template node.

    scope_key : object
        The key for the local scope in the local storage map.

    has_locals : bool
        Whether or not the node has local scope.

    """
    node = TemplateNode()
    node.scope_key = scope_key
    node.has_locals = has_locals
    return node


def make_enamldef(name, bases, dct):
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


def make_object():
    """ Return a new empty object.

    """
    return object()


def make_template(paramspec, func, name, f_globals, template_map):
    """ Return a new template object.

    This method will create a new template if necessary, add the
    specialization, and store the template in the globals and the
    template map. If a template already exists in the template map
    but not in the globals, it indicates an error and an exception
    will be raised.

    Parameters
    ----------
    paramspec : tuple
        The tuple of the parameter specialization arguments.

    func : FunctionType
        The function which implements the template.

    name : str
        The name of the template.

    f_globals : dict
        The globals dictionary for the module.

    template_map : dict
        The mapping of templates already created for the module.

    """
    template = template_map.get(name)
    if template is not None:
        if f_globals.get(name) is not template:
            msg = "template '%s' was deleted before being specialized"
            raise TypeError(msg % name)
    else:
        template = Template()
        template.module = f_globals.get('__name__', '')
        template.name = name
        template_map[name] = template
        f_globals[name] = template
    template.add_specialization(paramspec, func)


def run_operator(node, name, op, code, f_globals):
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
    pair = operators[op](code, node.scope_key, f_globals)

    # The read and write semantics are reversed here. In the context of
    # a declarative member, d_readable means that an attribute can be
    # *read* from enaml and it's value *written* to the expression,
    # d_writable means that an expression can be *read* and its value
    # *written* to the attribute attribute.
    member = node.klass.members().get(name)
    if (member is None or
        member.metadata is None or
        not member.metadata.get('d_member')):
        raise TypeError("'%s' is not a declarative member" % name)
    if pair.writer is not None and not member.metadata.get('d_readable'):
        raise TypeError("'%s' is not readable from enaml" % name)
    if pair.reader is not None and not member.metadata.get('d_writable'):
        raise TypeError("'%s' is not writable from enaml" % name)

    if node.engine is None:
        node.engine = ExpressionEngine()
    node.engine.add_pair(name, pair)


def type_check_expr(value, kind):
    """ Type check the value of an expression.

    Parameters
    ----------
    value : object
        The value to type check.

    kind : type
        The allowed type of the value.

    Returns
    -------
    result : object
        The original value.

    """
    if not isinstance(kind, type):
        raise TypeError("%s is not a type" % kind)
    if not isinstance(value, kind):
        msg = "expression value has invalid type '%s'"
        raise TypeError(msg % type(value).__name__)
    return value


def validate_declarative(klass):
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


def validate_spec(index, spec):
    """ Validate the value for a parameter specialization.

    This validator ensures that the value is hashable and not None.

    Parameters
    ----------
    index : int
        The integer index of the parameter being specialized.

    spec : object
        The parameter specialization.

    Returns
    -------
    result : object
        The validated specialization object.

    """
    if spec is None:
        msg = "cannot specialize template parameter %d with None"
        raise TypeError(msg % index)
    try:
        hash(spec)
    except TypeError:
        msg = "template parameter %d has unhashable type: '%s'"
        raise TypeError(msg % (index, type(spec).__name__))
    return spec


def validate_template(template):
    """ Validate that the object is a template.

    Parameters
    ----------
    template : object
        The object to validate.

    Returns
    -------
    result : object
        The validated object.

    """
    if not isinstance(template, Template):
        raise TypeError("%s is not a template" % template)
    return template


__compiler_helpers = {
    'add_static_attr': add_static_attr,
    'add_storage': add_storage,
    'declarative_node': declarative_node,
    'enamldef_node': enamldef_node,
    'make_enamldef': make_enamldef,
    'make_object': make_object,
    'make_template': make_template,
    'run_operator': run_operator,
    'template_node': template_node,
    'type_check_expr': type_check_expr,
    'validate_declarative': validate_declarative,
    'validate_template': validate_template,
    'validate_spec': validate_spec,
}
