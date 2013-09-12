#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Event, Instance, Member
from atom.datastructures.api import sortedmap

from .alias import Alias
from .compiler_nodes import (
    DeclarativeNode, EnamlDefNode, TemplateNode, TemplateInstNode,
    DeclarativeInterceptNode, EnamlDefInterceptNode
)
from .declarative import Declarative, d_
from .declarative_meta import patch_d_member
from .enamldef_meta import EnamlDefMeta
from .expression_engine import ExpressionEngine
from .operators import __get_operators
from .template import Template


def validate_alias(node_map, target, attr):
    if target not in node_map:
        msg = "'%s' is not a valid alias target"
        raise TypeError(msg % target)
    if attr:
        item = getattr(node_map[target].klass, attr, None)
        if not isinstance(item, (Alias, Member)):
            msg = "'%s' is not a valid alias attribute"
            raise TypeError(msg % attr)


def add_alias(node_map, node, name, target, attr):
    """ Add an alias to a Declarative subclass.

    Parameters
    ----------
    node_map : dict
        A dict mapping identifier to declarative child nodes for the
        entire enamldef block.

    node : EnamlDefNode
        The enamldef node for which an alias should be added.

    name : str
        The name of the alias.

    target : str
        The target of the alias.

    attr : str
        The attribute being accessed on the target. This should be
        an empty string for object aliases.

    """
    validate_alias(node_map, target, attr)
    klass = node.klass
    item = getattr(klass, name, None)
    if isinstance(item, Alias):
        msg = "can't override alias '%s'"
        raise TypeError(msg % name)
    if name in klass.members():
        msg = "can't override member '%s' with an alias"
        raise TypeError(msg % name)
    alias = Alias(target, attr, node.scope_key)
    setattr(klass, name, alias)


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

    if isinstance(getattr(klass, name, None), Alias):
        msg = "can't override alias '%s' with a member"
        raise TypeError(msg % name)

    members = klass.members()
    member = members.get(name)
    if member is not None:
        if member.metadata is None or not member.metadata.get('d_member'):
            msg = "can't override non-declarative member '%s'"
            raise TypeError(msg % name)
        if member.metadata.get('d_final'):
            msg = "can't override the final member '%s'"
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
    patch_d_member(new)
    members[name] = new
    setattr(klass, name, new)


def declarative_node(klass, identifier, scope_key, store_locals):
    """ Create and return a DeclarativeNode for the given klass.

    Parameters
    ----------
    klass : type
        The resolved declarative class for the node.

    identifier : str
        The local string identifier to associate with instances.

    scope_key : object
        The key for the local scope in the local storage maps.

    store_locals : bool
        Whether instances of this node class should store the
        local scope in their storage map.

    Returns
    -------
    result : DeclarativeNode
        The compiler node for the given klass.

    """
    #if klass.__intercepts_child_nodes__:
    #    node = DeclarativeInterceptNode()
    #else:
    node = DeclarativeNode()
    node.klass = klass
    node.identifier = identifier
    node.scope_key = scope_key
    node.store_locals = store_locals
    # If the class is an enamldef, copy its node as the super node.
    super_node = getattr(klass, '__node__', None)
    if super_node is not None:
        super_node = super_node.copy()
        node.super_node = super_node
        node.engine = super_node.engine
    return node


def enamldef_node(klass, identifier, scope_key, store_locals):
    """ Create and return an EnamlDefNode for the given class.

    Parameters
    ----------
    klass : type
        The enamldef declarative class for the node.

    identifier : str
        The local string identifier to associate with instances.

    scope_key : object
        The key for the local scope in the local storage maps.

    store_locals : bool
        Whether instances of this node class should store the
        local scope in their storage map.

    Returns
    -------
    result : EnamlDefNode
        The compiler node for the given class.

    """
    #if klass.__intercepts_child_nodes__:
    #    node = EnamlDefInterceptNode()
    #else:
    node = EnamlDefNode()
    node.klass = klass
    node.identifier = identifier
    node.scope_key = scope_key
    node.store_locals = store_locals
    # If the class is an enamldef, copy its node as the super node.
    super_node = getattr(klass, '__node__', None)
    if super_node is not None:
        super_node = super_node.copy()
        node.super_node = super_node
        node.engine = super_node.engine
    return node


def template_node():
    """ Create and return a template node.

    Returns
    -------
    result : TemplateNode
        A new compiler template node.

    """
    return TemplateNode()


def template_inst_node(template_inst, names, starname):
    """ Create and return a template inst node.

    Parameters
    ----------
    template_inst : TemplateInst
        The template instantiation object.

    names : tuple
        The identifier names to associate with the instantiation items.
        This may be an empty tuple if there are no such identifiers.

    starname : str
        The star name to associate with the extra instantiated items.
        This may be an empty string if there is no such item.

    Returns
    -------
    result : TemplateInstNode
        The compiler node for the template instantiation.

    """
    node = TemplateInstNode()
    node.template_node = template_inst.template_node
    node.names = names
    node.starname = starname
    return node


def make_template_scope(node, scope_tuple):
    """ Create and add the template scope to a template node.

    Parameters
    ----------
    node : TemplateNode
        The template node for which to create the scope.

    scope_tuple : tuple
        A tuple of alternating key, value pairs representing the
        scope of a template instantiation.

    """
    scope = sortedmap()
    t_iter = iter(scope_tuple)
    for key, value in zip(t_iter, t_iter):
        scope[key] = value
    node.template_scope = scope
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


def bind_alias(node, name, pair, alias):
    pass


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

    member = node.klass.members().get(name)
    if member is None:
        alias = getattr(node.klass, name, None)
        if isinstance(alias, AttributeAlias):
            bind_alias(node, name, pair, alias)
        elif isinstance(alias, ObjectAlias):
            raise TypeError("can't bind to an object alias '%s'" % name)
        else:
            raise TypeError("'%s' is not a declarative member" % name)

    # The read and write semantics are reversed here. In the context of
    # a declarative member, d_readable means that an attribute can be
    # *read* from enaml and it's value *written* to the expression,
    # d_writable means that an expression can be *read* and its value
    # *written* to the attribute attribute.
    if member.metadata is None or not member.metadata.get('d_member'):
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


def validate_unpack_size(template_inst, n, ex_unpack):
    """ Validate the length of a template instantiation.

    """
    size = template_inst.template_node.size()
    if size < n:
        suffix = 'values' if size > 1 else 'value'
        raise ValueError("need more than %d %s to unpack" % (size, suffix))
    if not ex_unpack and size > n:
        raise ValueError("too many values to unpack")
    return template_inst


__compiler_helpers = {
    'add_alias': add_alias,
    'add_storage': add_storage,
    'declarative_node': declarative_node,
    'enamldef_node': enamldef_node,
    'make_enamldef': make_enamldef,
    'make_object': make_object,
    'make_template': make_template,
    'make_template_scope': make_template_scope,
    'run_operator': run_operator,
    'template_node': template_node,
    'template_inst_node': template_inst_node,
    'type_check_expr': type_check_expr,
    'validate_declarative': validate_declarative,
    'validate_spec': validate_spec,
    'validate_template': validate_template,
    'validate_unpack_size': validate_unpack_size,
}
