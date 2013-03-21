#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import ast
import types

from atom.api import Atom, Int, List, Str, Typed


def from_dict(dct):
    """ Convert a previously serialized node dict into an ASTNode.

    """
    nodetype = dct['nodetype']
    kind = globals()[nodetype]
    return kind.from_dict(dct)


class ASTNode(Atom):
    """ The base class for Enaml ast nodes.

    """
    #: The name of the .enaml file which generated the node.
    filename = Str()

    #: The line number in the .enaml file which generated the node.
    lineno = Int(-1)

    @classmethod
    def from_dict(cls, dct):
        self = cls()
        self.filename = dct['filename']
        self.lineno = dct['lineno']
        return self

    def as_dict(self):
        dct = {}
        dct['nodetype'] = type(self).__name__
        dct['filename'] = self.filename
        dct['lineno'] = self.lineno
        return dct


class Module(ASTNode):
    """ An ASTNode representing an Enaml module.

    """
    #: The docstring for the module, if given.
    docstring = Str()

    #: The list of ast nodes for the body of the module. This will be
    #: composed of Python and EnamlDef nodes.
    body = List()

    @classmethod
    def from_dict(cls, dct):
        self = super(Module, cls).from_dict(dct)
        self.docstring = dct['docstring']
        self.body = [from_dict(node) for node in dct['body']]
        return self

    def as_dict(self):
        dct = super(Module, self).as_dict()
        dct['docstring'] = self.docstring
        dct['body'] = [node.as_dict() for node in self.body]
        return dct


class Python(ASTNode):
    """ An ASTNode representing a chunk of pure Python code.

    """
    #: The python ast node for the given python code.
    ast = Typed(ast.AST)

    #: The code object representing the compiled ast.
    code = Typed(types.CodeType)

    @classmethod
    def from_dict(cls, dct):
        self = super(Python, cls).from_dict(dct)
        self.ast = None  # XXX deserialize the Python AST
        self.code = dct['code']
        return self

    def as_dict(self):
        dct = super(Python, self).as_dict()
        dct['ast'] = None  # XXX serialize the Python AST
        dct['code'] = self.code
        return dct


class EnamlDef(ASTNode):
    """ An ASTNode representing an enamldef block.

    """
    #: The type name given to the enamldef.
    typename = Str()

    #: The name of the base class which is being inherited.
    base = Str()

    #: The identifier given to the enamldef.
    identifier = Str()

    #: The docstring for the enamldef.
    docstring = Str()

    #: The list of decorator for the enamldef. This will be composed of
    #: Python nodes.
    decorators = List()

    #: The list of body nodes for the enamldef. This will be composed
    #: of StateDef, Binding, and ChildDef nodes.
    body = List()

    @classmethod
    def from_dict(cls, dct):
        self = super(EnamlDef, cls).from_dict(dct)
        self.typename = dct['typename']
        self.base = dct['base']
        self.identifier = dct['identifier']
        self.docstring = dct['docstring']
        self.decorators = [from_dict(node) for node in dct['decorators']]
        self.body = [from_dict(node) for node in dct['body']]
        return self

    def as_dict(self):
        dct = super(EnamlDef, self).as_dict()
        dct['typename'] = self.typename
        dct['base'] = self.base
        dct['identifier'] = self.identifier
        dct['docstring'] = self.docstring
        dct['decorators'] = [node.as_dict() for node in self.decorators]
        dct['body'] = [node.as_dict() for node in self.body]
        return dct


class ChildDef(ASTNode):
    """ An ASTNode representing a child definition.

    """
    #: The type name of the child to create.
    typename = Str()

    #: The identifier given to the child.
    identifier = Str()

    #: The list of body nodes for the child definition. This will be
    #: composed of StateDef, Binding, and ChildDef nodes.
    body = List()

    @classmethod
    def from_dict(cls, dct):
        self = super(ChildDef, cls).from_dict(dct)
        self.typename = dct['typename']
        self.identifier = dct['identifier']
        self.body = [from_dict(node) for node in dct['body']]
        return self

    def as_dict(self):
        dct = super(ChildDef, self).as_dict()
        dct['typename'] = self.typename
        dct['identifier'] = self.identifier
        dct['body'] = [b.as_dict() for b in self.body]
        return dct


class Binding(ASTNode):
    """ An AST node which represents a code binding.

    """
    #: The name of the attribute being bound.
    name = Str()

    #: The operator used to bind the code.
    operator = Str()

    #: The python ast node for the bound python code.
    value = Typed(Python)

    @classmethod
    def from_dict(cls, dct):
        self = super(Binding, cls).from_dict(dct)
        self.name = dct['name']
        self.operator = dct['operator']
        self.value = from_dict(dct['value'])

    def as_dict(self):
        dct = super(Binding, self).as_dict()
        dct['name'] = self.name
        dct['operator'] = self.operator
        dct['value'] = self.value.as_dict()
        return dct


class StateDef(ASTNode):
    """ A base class for 'attr' and 'event' definitions.

    """
    #: The name of the attribute or event being defined.
    name = Str()

    #: The typename of the allowed attribute or event values.
    typename = Str()

    #: The default binding node for the attribute or event.
    binding = Typed(Binding)

    @classmethod
    def from_dict(cls, dct):
        self = super(StateDef, cls).from_dict(dct)
        self.name = dct['name']
        self.typename = dct['typename']
        self.binding = from_dict(dct['binding'])

    def as_dict(self):
        dct = super(Binding, self).as_dict()
        dct['name'] = self.name
        dct['typename'] = self.typename
        dct['binding'] = self.binding.as_dict()
        return dct


class AttrDef(StateDef):
    """ An AST node which represents an 'attr' definition.

    """
    pass


class EventDef(StateDef):
    """ An AST node which represents an 'event' definition.

    """
    pass
