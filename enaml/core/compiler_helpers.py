#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from functools import update_wrapper

from atom.api import Event, Instance, Member
from atom.datastructures.api import sortedmap

from .alias import Alias
from .compiler_nodes import (
    DeclarativeNode, EnamlDefNode, TemplateNode, TemplateInstanceNode
)
from .declarative import Declarative, d_
from .declarative_function import DeclarativeFunction
from .declarative_meta import patch_d_member
from .enamldef_meta import EnamlDefMeta
from .expression_engine import ExpressionEngine
from .operators import __get_operators
from .template import Template
from .funchelper import call_func


def resolve_alias(node, alias):
    """ Resolve the compiler item pointed to by an alias.

    Parameters
    ----------
    node : DeclarativeNode
        The declarative node on which the alias is being accessed.

    alias : Alias
        The alias object which is being accessed.

    Returns
    -------
    result : 2-tuple
        A 2-tuple of (node, member) which represents the resolved alias.
        If the alias does not point to a member, then the member will be
        None. Both values will be None if the alias is not valid.

    """
    if node is None:
        return (None, None)
    if node.scope_key != alias.key:
        return resolve_alias(node.super_node, alias)
    target = node.id_nodes.get(alias.target)
    if target is None:
        return (None, None)
    chain = alias.chain
    if not chain:
        return (target, None)
    last = len(chain) - 1
    for index, name in enumerate(chain):
        item = getattr(target.klass, name, None)
        if isinstance(item, Member):
            if index == last:
                return (target, item)
            return (None, None)
        if isinstance(item, Alias):
            target, member = resolve_alias(target, item)
            if target is None:
                return (None, None)
            if member is not None:
                if index == last:
                    return (target, member)
                return (None, None)
            if index == last:
                return (target, None)
        else:
            return (None, None)
    return (None, None)


def _override_fail(klass, name):
    msg = "can't override '%s.%s'"
    raise TypeError(msg % (klass.__name__, name))


def add_alias(node, name, target, chain):
    """ Add an alias to a Declarative subclass.

    Parameters
    ----------
    node : EnamlDefNode
        The enamldef node for which the alias should be added.

    name : str
        The attribute name to use when adding the alias to the class.

    target : str
        The node target for the alias.

    chain : tuple
        The chain of names to associate with the alias.

    """
    klass = node.klass
    if hasattr(klass, name):
        _override_fail(klass, name)
    alias = Alias(target, chain, node.scope_key)
    res_node, res_member = resolve_alias(node, alias)
    if res_node is None:
        msg = "'%s' is not a valid alias reference"
        parts = [target] + list(chain)
        raise TypeError(msg % '.'.join(parts))
    alias.canset = res_member is not None
    setattr(klass, name, alias)


def add_storage(node, name, store_type, kind):
    """ Add user storage to a Declarative subclass.

    Parameters
    ----------
    node : DeclarativeNode
        The declarative node to which storage should be added.

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

    klass = node.klass
    members = klass.members()
    member = members.get(name)
    if member is not None:
        if member.metadata is None or not member.metadata.get('d_member'):
            msg = "can't override non-declarative member '%s.%s'"
            raise TypeError(msg % (klass.__name__, name))
        if member.metadata.get('d_final'):
            msg = "can't override final member '%s.%s'"
            raise TypeError(msg % (klass.__name__, name))
    elif hasattr(klass, name):
        _override_fail(klass, name)

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
        Whether instances of the class should store the local scope in
        their storage map.

    Returns
    -------
    result : DeclarativeNode
        The compiler node for the given klass.

    """
    node = DeclarativeNode()
    node.klass = klass
    node.identifier = identifier
    node.scope_key = scope_key
    node.store_locals = store_locals
    node.child_intercept = klass.__intercepts_child_nodes__
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
        Whether instances of the class should store the local scope in
        their storage map.

    Returns
    -------
    result : EnamlDefNode
        The compiler node for the given class.

    """
    node = EnamlDefNode()
    node.klass = klass
    node.identifier = identifier
    node.scope_key = scope_key
    node.store_locals = store_locals
    node.child_intercept = klass.__intercepts_child_nodes__
    # If the class is an enamldef, copy its node as the super node.
    super_node = getattr(klass, '__node__', None)
    if super_node is not None:
        super_node = super_node.copy()
        node.super_node = super_node
        node.engine = super_node.engine
    klass.__node__ = node
    return node


def template_node(scope_key):
    """ Create and return a new template node.

    Parameters
    ----------
    scope_key : object
        The key for the local scope in the local storage maps.

    Returns
    -------
    result : TemplateNode
        A new compiler template node.

    """
    node = TemplateNode()
    node.scope_key = scope_key
    return node


def template_inst_node(templ, names, starname, scope_key, copy):
    """ Create and return a new template inst node.

    Parameters
    ----------
    templ : TemplateInst
        The template instantiation object.

    names : tuple
        The identifier names to associate with the instantiation items.
        This may be an empty tuple if there are no such identifiers.

    starname : str
        The star name to associate with the extra instantiated items.
        This may be an empty string if there is no such item.

    scope_key : object
        The key for the local scope in the local storage maps.

    copy : bool
        Whether a copy of the underlying template node is required. A
        copy will be required when the template instance has bindings
        so that the closure keys remain isolated to this instance.

    Returns
    -------
    result : TemplateInstNode
        The compiler node for the template instantiation.

    """
    node = TemplateInstanceNode()
    node.template = templ.node.copy() if copy else templ.node
    node.names = names
    node.starname = starname
    node.scope_key = scope_key
    return node


def add_template_scope(node, names, values):
    """ Create and add the template scope to a template node.

    Parameters
    ----------
    node : TemplateNode
        The template node for which to create the scope.

    scope_tuple : tuple
        A tuple of alternating key, value pairs representing the
        scope of a template instantiation.

    Returns
    -------
    result : sortedmap
        The scope mapping for the given scope tuple.

    """
    scope = sortedmap()
    for name, value in zip(names, values):
        scope[name] = value
    node.scope = scope


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

    Returns
    -------
    result : EnamlDefMeta
        A new class generator from the EnamlDefMeta metaclass.

    """
    return EnamlDefMeta(name, bases, dct)


def make_object():
    """ Create a new empty object instance.

    Returns
    -------
    result : object
        A new object instance.

    """
    return object()


def make_template(paramspec, func, name, f_globals, template_map):
    """ Create a new template object.

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


def bind_aliased_member_impl(name, node, member, pair, scope_key):
    """ Bind a pair for the given aliased node and member.

    This function validates the declarative member, adds the pair
    to the node's engine, and adds the closure key for the scope.

    Parameters
    ----------
    name : str
        The pre-resolved name of the alias member. This is used for
        error reporting. The member name is used for binding.

    node : DeclarativeNode
        The compiler node holding the declarative class.

    member : Member
        The member which is being bound. It will be checked to ensure
        it is declarative and appropriately readable and writable.

    pair : HandlerPair
        The handler pair to add to the expression engine.

    scope_key : object
        The closure scope key for adding to the node's closure keys.

    """
    if member.metadata is None or not member.metadata.get('d_member'):
        raise TypeError("alias '%s' is not a declarative member" % name)
    if pair.writer is not None and not member.metadata.get('d_readable'):
        raise TypeError("alias '%s' is not readable from enaml" % name)
    if pair.reader is not None and not member.metadata.get('d_writable'):
        raise TypeError("alias '%s' is not writable from enaml" % name)
    if node.engine is None:
        node.engine = ExpressionEngine()
    node.engine.add_pair(member.name, pair)
    if node.closure_keys is None:
        node.closure_keys = set()
    node.closure_keys.add(scope_key)


def bind_aliased_member(node, name, alias, pair, scope_key):
    """ Bind a handler pair to an aliased member.

    Parameters
    ----------
    node : DeclarativeNode
        The compiler node holding the declarative class.

    name : str
        The name being bound for the class.

    alias : Alias
        The alias being bound.

    pair : HandlerPair
        The handler pair to add to the expression engine.

    scope_key : object
        The closure scope key for adding to the node's closure keys.

    """
    target_node, member = resolve_alias(node, alias)
    if target_node is None or member is None:
        msg = "alias '%s' does not resolve to a declarative member"
        raise TypeError(msg % name)
    bind_aliased_member_impl(name, target_node, member, pair, scope_key)


def bind_extended_member(node, chain, pair, scope_key):
    """ Bind a handler pair to an extended member.

    Parameters
    ----------
    node : DeclarativeNode
        The compiler node holding the declarative class.

    chain : tuple
        A tuple of names for the extended binding.

    pair : HandlerPair
        The handler pair to add to the expression engine.

    scope_key : object
        The closure scope key for adding to the node's closure keys.

    """
    # Resolve everything but the last item in the chain. Everything
    # up to that point must be aliases which resolve to an object.
    seen = []
    target_node = node
    for name in chain[:-1]:
        seen.append(name)
        alias = getattr(target_node.klass, name, None)
        if not isinstance(alias, Alias):
            raise TypeError("'%s' is not an alias" % '.'.join(seen))
        target_node, member = resolve_alias(target_node, alias)
        if target_node is None or member is not None:
            msg = "'%s' does not alias an object"
            raise TypeError(msg % '.'.join(seen))

    # Resolve the final item in the chain, which must be a Member.
    # The call to bind_member() will validate that it is declarative.
    name = chain[-1]
    member = getattr(target_node.klass, name, None)
    if isinstance(member, Alias):
        target_node, member = resolve_alias(target_node, member)
        if target_node is None or member is None:
            msg = "'%s' does not alias a member"
            raise TypeError(msg % '.'.join(chain))
    elif not isinstance(member, Member):
        msg = "'%s' does not alias a member"
        raise TypeError(msg % '.'.join(chain))

    # Bind the final aliased member.
    bind_aliased_member_impl(name, target_node, member, pair, scope_key)


def bind_member(node, name, pair):
    """ Bind a handler pair to a node.

    Parameters
    ----------
    node : DeclarativeNode
        The compiler node holding the declarative class.

    name : str
        The name being bound for the class.

    pair : HandlerPair
        The handler pair to add to the expression engine.

    """
    member = node.klass.members().get(name)
    if member is None:
        raise TypeError("'%s' is not a declarative member" % name)
    if member.metadata is None or not member.metadata.get('d_member'):
        raise TypeError("'%s' is not a declarative member" % name)
    if pair.writer is not None and not member.metadata.get('d_readable'):
        raise TypeError("'%s' is not readable from enaml" % name)
    if pair.reader is not None and not member.metadata.get('d_writable'):
        raise TypeError("'%s' is not writable from enaml" % name)
    if node.engine is None:
        node.engine = ExpressionEngine()
    node.engine.add_pair(name, pair)


def run_operator(scope_node, node, name, op, code, f_globals):
    """ Run the operator for a given node.

    Parameters
    ----------
    scope_node : DeclarativeNode
        The node which holds the scope key for the scope in which the
        code will execute.

    node : DeclarativeNode
        The compiler node holding the declarative class being bound.

    name : str or tuple
        The name or names being bound for the class.

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
    scope_key = scope_node.scope_key
    pair = operators[op](code, scope_key, f_globals)
    if isinstance(name, tuple):
        # The template inst binding with a single name will take this
        # path by using a length-1 name tuple. See bug #78.
        bind_extended_member(node, name, pair, scope_key)
    else:
        item = getattr(node.klass, name, None)
        if isinstance(item, Alias):
            bind_aliased_member(node, name, item, pair, scope_key)
        else:
            # This is the path for a standard binding on a child def.
            # It does not need the closure scope key. See bug #78.
            bind_member(node, name, pair)


def make_unpack_map(node):
    """ Make a mapping of unpack values for a template instance.

    Parameters
    ----------
    node : TemplateInstanceNode
        The compiler node for the template instantiation.

    Returns
    -------
    result : dict
        A dict mapping unpack name to compiler node for the template
        instantiation.

    """
    return dict(zip(node.names, node.iternodes()))


def type_check_expr(value, kind):
    """ Type check the value of an expression.

    Parameters
    ----------
    value : object
        The value to type check.

    kind : type
        The allowed type of the value.

    """
    if not isinstance(kind, type):
        raise TypeError("%s is not a type" % kind)
    if not isinstance(value, kind):
        msg = "expression value has invalid type '%s'"
        raise TypeError(msg % type(value).__name__)


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

    """
    if not isinstance(template, Template):
        raise TypeError("%s is not a template" % template)


def validate_unpack_size(template_inst, count, variadic):
    """ Validate the length of a template instantiation.

    Parameters
    ----------
    template_inst : TemplateInstance
        An instantiation of a template.

    count : int
        The number of singular unpack parameters.

    variadic : bool
        Whether or not a variadic unpacking parameter is present.

    """
    size = template_inst.node.size()
    if size < count:
        suffix = 'values' if size > 1 else 'value'
        raise ValueError("need more than %d %s to unpack" % (size, suffix))
    if not variadic and size > count:
        raise ValueError("too many values to unpack")


def add_decl_function(node, func, is_override):
    """ Add a declarative function to a declarative class.

    Parameters
    ----------
    node : DeclarativeNode
        The compiler node holding the declarative class.

    func : FunctionType
        The python function to add to the class.

    is_override : bool
        True if the function was declared with override syntax, False
        if declared as a new function on the declarative class.

    """
    name = func.__name__
    klass = node.klass
    if is_override:
        current = getattr(klass, name, None)
        if not getattr(current, "_d_func", False):
            raise TypeError("'%s' is not a declarative function" % name)
    elif hasattr(klass, name):
        _override_fail(klass, name)
    d_func = DeclarativeFunction(func, node.scope_key)
    setattr(klass, name, d_func)


def wrap_function(func, scope):
    """Wrap a function to call it with the dynamicscope in which it was defined

    Parameters
    ----------
    func : FunctionType
        Function for which a new scope need to be built

    scope : DynamicScope
        Scope in which the function was defined.

    """
    def wrapper(*args, **kwargs):
        return call_func(func, args, kwargs, scope)

    update_wrapper(wrapper, func)

    return wrapper


__compiler_helpers = {
    'add_alias': add_alias,
    'add_decl_function': add_decl_function,
    'add_template_scope': add_template_scope,
    'add_storage': add_storage,
    'declarative_node': declarative_node,
    'enamldef_node': enamldef_node,
    'make_enamldef': make_enamldef,
    'make_object': make_object,
    'make_template': make_template,
    'make_unpack_map': make_unpack_map,
    'run_operator': run_operator,
    'template_node': template_node,
    'template_inst_node': template_inst_node,
    'type_check_expr': type_check_expr,
    'validate_declarative': validate_declarative,
    'validate_spec': validate_spec,
    'validate_template': validate_template,
    'validate_unpack_size': validate_unpack_size,
    'wrap_func': wrap_function,
}
