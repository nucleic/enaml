#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from types import CodeType

from atom.api import (
    Atom, Callable, Enum, Int, List, Str, Typed, ForwardTyped, Instance, Event
)

from .declarative import Declarative, d_
from .enaml_def import EnamlDefMeta
from .exceptions import (
    DeclarativeNameError, DeclarativeError, OperatorLookupError
)
from .operators import __get_operators


def scope_name_generator():
    stem = '__locals_%d__'
    i = 0
    while True:
        yield stem % i
        i += 1
scope_name_generator = scope_name_generator()


class ConstructNode(Atom):
    """ The base class for Enaml construct nodes.

    """
    #: The parent of the construct tree node.
    parent = ForwardTyped(lambda: ConstructNode)

    #: The line number which created the node.
    lineno = Int(-1)

    @classmethod
    def from_dict(cls, dct):
        """ Create the node from a dict description.

        """
        return cls()

    def root(self):
        """ Get the root node for the construct tree.

        """
        node = self
        while node.parent:
            node = node.parent
        return node

    def resolve(self, f_globals):
        """ Resolve the globals for the node and its children.

        """
        pass


class EnamlDefConstruct(ConstructNode):
    """ A construct node for an enamldef block.

    """
    #: The filename which created the enamldef.
    filename = Str()

    #: The type name given to the enamldef.
    typename = Str()

    #: The name of the base class which is being inherited.
    base = Str()

    #: The identifier given to the enamldef.
    identifier = Str()

    #: The docstring for the enamldef.
    docstring = Str()

    #: The list of state def nodes for the enamldef.
    state_defs = List()

    #: The list of binding nodes for the enamldef.
    bindings = List()

    #: The list of child def nodes for the enamldef.
    child_defs = List()

    #: A unique name for the local scope object for this block.
    local_scope = Str()

    #: The resolved base class for the enamldef object.
    base_class = Typed(type)

    #: The created type class for the enamldef object.
    type_class = Typed(type)

    #: The module globals for the enamldef.
    f_globals = Typed(dict)

    @classmethod
    def from_dict(cls, dct):
        self = cls()
        self.lineno = dct['lineno']
        self.filename = dct['filename']
        self.typename = dct['typename']
        self.base = dct['base']
        self.identifier = dct['identifier']
        self.docstring = dct['docstring']
        for state_def in dct['state_defs']:
            node = StateDefConstruct.from_dict(state_def)
            node.parent = self
            self.state_defs.append(node)
        for binding in dct['bindings']:
            node = BindingConstruct.from_dict(binding)
            node.parent = self
            self.bindings.append(node)
        for child_def in dct['child_defs']:
            node = ChildDefConstruct.from_dict(child_def)
            node.parent = self
            self.child_defs.append(node)
        return self

    def resolve(self, f_globals):
        try:
            base_class = f_globals[self.base]
        except KeyError:
            raise DeclarativeNameError(self.base, self)
        if (not isinstance(base_class, type) or
            not issubclass(base_class, Declarative)):
            msg = "cannot derive enamldef from '%s'"
            raise DeclarativeError(msg % self.base, self)
        self.base_class = base_class
        self.f_globals = f_globals
        dct = {}
        dct['__module__'] = f_globals.get('__name__', '')
        dct['__doc__'] = self.docstring
        self.type_class = EnamlDefMeta(self.typename, (base_class,), dct)
        for state in self.state_defs:
            state.resolve(f_globals)
        for binding in self.bindings:
            binding.resolve(f_globals)
        for child in self.child_defs:
            child.resolve(f_globals)


class StateDefConstruct(ConstructNode):
    """ A construct node for an state definition.

    """
    #: The kind of the state definition.
    kind = Enum('attr', 'event')

    #: The name of the state object being defined.
    name = Str()

    #: The typename of the allowed values for the state object.
    typename = Str()

    #: The resolved type class for using with the state def.
    type_class = Typed(type)

    @classmethod
    def from_dict(cls, dct):
        self = cls()
        self.lineno = dct['lineno']
        self.kind = dct['kind']
        self.name = dct['name']
        self.typename = dct['typename']
        return self

    def resolve(self, f_globals):
        typename = self.typename
        if typename:
            try:
                type_class = f_globals[typename]
            except KeyError:
                try:
                    type_class = f_globals['__builtins__'][typename]
                except KeyError:
                    raise DeclarativeError(typename, self)
            if not isinstance(type_class, type):
                msg = "'%s' is not a valid type"
                raise DeclarativeError(msg % typename, self)
            self.type_class = type_class
        else:
            self.type_class = type_class = object
        name = self.name
        owner = self.parent
        members = owner.members()
        if name in members:
            member = members[name]
            if member.metadata is None or not member.metadata.get('d_member'):
                msg = "cannot override non-declarative member '%s'"
                raise DeclarativeError(msg % name, self)
            if member.metadata.get('d_final'):
                msg = "cannot override the final member '%s'"
                raise DeclarativeError(msg % name, self)
        if self.kind == 'attr':
            newmember = d_(Instance(type_class), final=False)
        else:
            newmember = d_(Event(type_class), writable=False, final=False)
        if name in members:
            member = members[name]
            newmember.set_index(member.index)
            newmember.copy_static_observers(member)
        else:
            newmember.set_index(len(members))
        newmember.set_name(name)
        setattr(owner, name, newmember)


class BindingConstruct(ConstructNode):
    """ A construct node which represents a code binding.

    """
    #: The name of the attribute being bound.
    name = Str()

    #: The operator symbol used in the enaml source.
    operator = Str()

    #: The python code object to use for the binding.
    code = Typed(CodeType)

    #: The secondary code object for the binding.
    aux_code = Typed(CodeType)

    #: The operator function to use to bind the code object.
    operator_func = Callable()

    @classmethod
    def from_dict(cls, dct):
        self = cls()
        self.lineno = dct['lineno']
        self.name = dct['name']
        self.operator = dct['operator']
        self.code = dct['code']
        if dct['aux_code']:
            self.aux_code = dct['aux_code']
        return self

    def resolve(self, f_globals):
        try:
            op_func = __get_operators()[self.operator]
        except KeyError:
            raise OperatorLookupError(self.operator, self)
        self.operator_func = op_func
        op_func(self.parent, self)


class ChildDefConstruct(ConstructNode):
    """ A construct node representing a child definition.

    """
    #: The type name of the child to create.
    typename = Str()

    #: The identifier given to the child.
    identifier = Str()

    #: The list of state def nodes for the child.
    state_defs = List()

    #: The list of binding nodes for the child.
    bindings = List()

    #: The list of child def nodes for the child.
    child_defs = List()

    #: The resolved type class for the child object.
    type_class = Typed(type)

    @classmethod
    def from_dict(cls, dct):
        self = cls()
        self.lineno = dct['lineno']
        self.typename = dct['typename']
        self.identifier = dct['identifier']
        for state_def in dct['state_defs']:
            node = StateDefConstruct.from_dict(state_def)
            node.parent = self
            self.state_defs.append(node)
        for binding in dct['bindings']:
            node = BindingConstruct.from_dict(binding)
            node.parent = self
            self.bindings.append(node)
        for child_def in dct['child_defs']:
            node = ChildDefConstruct.from_dict(child_def)
            node.parent = self
            self.child_defs.append(node)
        return self

    def resolve(self, f_globals):
        try:
            type_class = f_globals[self.typename]
        except KeyError:
            raise DeclarativeNameError(self.typename, self)
        if (not isinstance(type_class, type) or
            not issubclass(type_class, Declarative)):
            msg = "'%s' is not a Declarative subclass"
            raise DeclarativeError(msg % self.typename, self)
        self.type_class = type_class
        if self.state_defs or self.bindings:
            # XXX subclass before adding members
        for state in self.state_defs:
            state.resolve(f_globals)
        for binding in self.bindings:
            binding.resolve(f_globals)
        for child in self.child_defs:
            child.resolve(f_globals)
