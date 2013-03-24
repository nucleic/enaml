#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from types import CodeType, FunctionType

from atom.api import (
    Atom, Member, Callable, Enum, Int, List, Str, Typed, ForwardTyped
)


class ConstructNode(Atom):
    """ The base class for Enaml construct nodes.

    A construct node is an abstract representation of the tree described
    by an 'enamldef' block. Unlike the AST generated by the parser, this
    tree will contain resolved class objects and the other information
    needed to create an instance of the 'enamldef'.

    """
    #: The parent of the construct tree node.
    parent = ForwardTyped(lambda: ConstructNode)

    #: The line number which created the node.
    lineno = Int(-1)

    @classmethod
    def from_dict(cls, dct):
        """ Create an instance of the node from a dict.

        Subclasses should reimplement this classmethod.

        Parameters
        ----------
        dct : dict
            The serializable dictionary created by the Enaml compiler
            which represents the construction tree.

        Returns
        -------
        result : ConstructNode
            The construct node for the given dict description.

        """
        self = cls()
        self.lineno = dct['lineno']
        return self

    def root(self):
        """ Get the root node for the construct tree.

        Returns
        -------
        result : ConstructNode
            The root of the construct tree.

        """
        node = self
        while node.parent:
            node = node.parent
        return node


class EnamlDefConstruct(ConstructNode):
    """ A construct node representing an 'enamldef' block.

    """
    #: The name of the file which holds enamldef definition.
    filename = Str()

    #: The type name given to the enamldef.
    typename = Str()

    #: The name of the base class which is being inherited.
    base = Str()

    #: The identifier given to the enamldef.
    identifier = Str()

    #: The docstring for the enamldef.
    docstring = Str()

    #: The list of storage def nodes for the enamldef.
    storage_defs = List()

    #: The list of binding nodes for the enamldef.
    bindings = List()

    #: The list of child def nodes for the enamldef.
    child_defs = List()

    #: The resolved base class for the enamldef object. This is updated
    #: during the resolution passes over the tree.
    baseclass = Typed(type)

    #: The created type class for the enamldef object. This is updated
    #: during the resolution passes over the tree.
    typeclass = Typed(type)

    #: The module globals for the enamldef. This is updated during the
    #: resolution passes over the tree.
    f_globals = Typed(dict)

    #: The member to use for accessing the local scope of an instance.
    #: This is updated during the resolution passes over the tree.
    scope_member = Typed(Member)

    #: The callable to invoke to populate an instance for the node.
    #: This is updated during the resolution passes over the tree.
    populate = Callable()

    @classmethod
    def from_dict(cls, dct):
        self = super(EnamlDefConstruct, cls).from_dict(dct)
        self.filename = dct['filename']
        self.typename = dct['typename']
        self.base = dct['base']
        self.identifier = dct['identifier']
        self.docstring = dct['docstring']
        for storage_def in dct['storage_defs']:
            node = StorageDefConstruct.from_dict(storage_def)
            node.parent = self
            self.storage_defs.append(node)
        for binding in dct['bindings']:
            node = BindingConstruct.from_dict(binding)
            node.parent = self
            self.bindings.append(node)
        for child_def in dct['child_defs']:
            node = ChildDefConstruct.from_dict(child_def)
            node.parent = self
            self.child_defs.append(node)
        return self


class StorageDefConstruct(ConstructNode):
    """ A construct node for a storage definition.

    """
    #: The kind of the state definition.
    kind = Enum('attr', 'event')

    #: The name of the state object being defined.
    name = Str()

    #: The typename of the allowed values for the state object.
    typename = Str()

    #: The resolved type class for using with the state def. This is
    #: updated during the resolution passes over the tree.
    typeclass = Typed(type)

    @classmethod
    def from_dict(cls, dct):
        self = super(StorageDefConstruct, cls).from_dict(dct)
        self.kind = dct['kind']
        self.name = dct['name']
        self.typename = dct['typename']
        return self


class BindingConstruct(ConstructNode):
    """ A construct node for an attribute binding.

    """
    #: The name of the attribute being bound.
    name = Str()

    #: The operator symbol used in the enaml source.
    operator = Str()

    #: The python code object to use for the binding.
    code = Typed(CodeType)

    #: The auxiliary code object for the binding. This may be null.
    auxcode = Typed(CodeType)

    #: The function object created for 'code'.
    func = Typed(FunctionType)

    #: The function object created for 'auxcode'.
    auxfunc = Typed(FunctionType)

    #: The operator function to use to bind the code object. This is
    #: updated during the resolution passes over the tree.
    operator_func = Callable()

    @classmethod
    def from_dict(cls, dct):
        self = super(BindingConstruct, cls).from_dict(dct)
        self.name = dct['name']
        self.operator = dct['operator']
        self.code = dct['code']
        if dct['auxcode']:
            self.auxcode = dct['auxcode']
        return self


class ChildDefConstruct(ConstructNode):
    """ A construct node for a child definition.

    """
    #: The type name of the child to create.
    typename = Str()

    #: The identifier given to the child.
    identifier = Str()

    #: The list of state def nodes for the child.
    storage_defs = List()

    #: The list of binding nodes for the child.
    bindings = List()

    #: The list of child def nodes for the child.
    child_defs = List()

    #: The resolved type class for the child object. This is updated
    #: during the resolution passes over the tree.
    typeclass = Typed(type)

    #: The member to use for accessing the local scope of an instance.
    #: This is updated during the resolution passes over the tree.
    scope_member = Typed(Member)

    #: The callable to invoke to populate an instance for the node.
    #: This is updated during the resolution passes over the tree.
    populate = Callable()

    @classmethod
    def from_dict(cls, dct):
        self = super(ChildDefConstruct, cls).from_dict(dct)
        self.typename = dct['typename']
        self.identifier = dct['identifier']
        for state_def in dct['storage_defs']:
            node = StorageDefConstruct.from_dict(state_def)
            node.parent = self
            self.storage_defs.append(node)
        for binding in dct['bindings']:
            node = BindingConstruct.from_dict(binding)
            node.parent = self
            self.bindings.append(node)
        for child_def in dct['child_defs']:
            node = ChildDefConstruct.from_dict(child_def)
            node.parent = self
            self.child_defs.append(node)
        return self
