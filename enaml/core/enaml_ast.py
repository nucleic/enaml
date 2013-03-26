#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import ast

from atom.api import Atom, Enum, Int, List, Str, Typed


class ASTNode(Atom):
    """ The base class for Enaml ast nodes.

    """
    #: The line number in the .enaml file which generated the node.
    lineno = Int(-1)


class Module(ASTNode):
    """ An ASTNode representing an Enaml module.

    """
    #: The list of ast nodes for the body of the module. This will be
    #: composed of Python and EnamlDef nodes.
    body = List()


class Python(ASTNode):
    """ An ASTNode representing a chunk of pure Python code.

    """
    #: The python ast node for the given python code.
    ast = Typed(ast.AST)


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
    #: of StorageDef, Binding, and ChildDef nodes.
    body = List()


class ChildDef(ASTNode):
    """ An ASTNode representing a child definition.

    """
    #: The type name of the child to create.
    typename = Str()

    #: The identifier given to the child.
    identifier = Str()

    #: The list of body nodes for the child definition. This will be
    #: composed of StorageDef, Binding, and ChildDef nodes.
    body = List()


class OperatorExpr(ASTNode):
    """ An AST node which represents an operator expression.

    """
    #: The operator used to bind the code.
    operator = Str()

    #: The python ast node for the bound python code.
    value = Typed(Python)


class Binding(ASTNode):
    """ An AST node which represents a code binding.

    """
    #: The name of the attribute being bound.
    name = Str()

    #: The operator expression for the binding.
    expr = Typed(OperatorExpr)


class StorageDef(ASTNode):
    """ An AST node for storage definitions.

    """
    #: The kind of the storage definition.
    kind = Enum('attr', 'event')

    #: The name of the storage object being defined.
    name = Str()

    #: The typename of the allowed values for the storage object.
    typename = Str()

    #: The default expression bound to the storage object. This may
    #: be None if the storage object has no default expr binding.
    expr = Typed(OperatorExpr)
