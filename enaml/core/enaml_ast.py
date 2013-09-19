#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import ast

from atom.api import Atom, Enum, Int, List, Str, Instance, Tuple, Typed


class ASTNode(Atom):
    """ The base class for Enaml ast nodes.

    """
    #: The line number in the .enaml file which generated the node.
    lineno = Int(-1)


class Module(ASTNode):
    """ An ASTNode representing an Enaml module.

    """
    #: The list of ast nodes for the body of the module. This will be
    #: composed of PythonModule, EnamlDef, and Template nodes.
    body = List()


class PythonExpression(ASTNode):
    """ An ASTNode representing a Python expression.

    """
    #: The python ast node for the given python code.
    ast = Typed(ast.Expression)


class PythonModule(ASTNode):
    """ An ASTNode representing a chunk of Python code.

    """
    #: The python ast node for the given python code.
    ast = Typed(ast.Module)


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
    #: of StorageExpr, Binding, ChildDef, and TemplateInst nodes.
    body = List()


class ChildDef(ASTNode):
    """ An ASTNode representing a child definition.

    """
    #: The type name of the child to create.
    typename = Str()

    #: The identifier given to the child.
    identifier = Str()

    #: The list of body nodes for the child def. This will be composed
    #: of StorageExpr, Binding, ChildDef and TemplateInst nodes.
    body = List()


class ConstExpr(ASTNode):
    """ An AST node which represents a 'const' expression.

    """
    #: The name being assigned by the expression.
    name = Str()

    #: The name of the type of allowed values for the expression.
    typename = Str()

    #: The Python expression to evaluate.
    expr = Typed(PythonExpression)


class AliasExpr(ASTNode):
    """ An AST node which represents an 'alias' expression.

    """
    #: The name of the alias.
    name = Str()

    #: The identifier of the target being aliased.
    target = Str()

    #: The chain of names being accessed by the alias.
    chain = Tuple()


class OperatorExpr(ASTNode):
    """ An AST node which represents an operator expression.

    """
    #: The operator used to bind the code.
    operator = Str()

    #: The python ast node for the bound python code.
    value = Instance((PythonExpression, PythonModule))


class Binding(ASTNode):
    """ An AST node which represents a code binding.

    """
    #: The name of the attribute being bound.
    name = Str()

    #: The operator expression for the binding.
    expr = Typed(OperatorExpr)


class ExBinding(ASTNode):
    """ An AST node which represents an extended code binding.

    """
    #: The chain of names being bound for the expression.
    chain = Tuple()

    #: The operator expression for the binding.
    expr = Typed(OperatorExpr)


class StorageExpr(ASTNode):
    """ An AST node representing a storage expression.

    """
    #: The stype of the storage expression.
    kind = Enum('attr', 'event')

    #: The name of the storage object being defined.
    name = Str()

    #: The name of the type of allowed values for the storage object.
    typename = Str()

    #: The default expression bound to the storage object. This may
    #: be None if the storage object has no default expr binding.
    expr = Typed(OperatorExpr)


class PositionalParameter(ASTNode):
    """ An AST node for storing a positional template parameter.

    """
    #: The name of the parameter.
    name = Str()

    #: The parameter specialization.
    specialization = Typed(PythonExpression)


class KeywordParameter(ASTNode):
    """ An AST node for storing a keyword template parameter.

    """
    #: The name of the parameter.
    name = Str()

    #: The default value for the parameter.
    default = Typed(PythonExpression)


class TemplateParameters(ASTNode):
    """ An AST node for template parameters.

    """
    #: The positional parameters.
    positional = List(PositionalParameter)

    #: The keyword parameters.
    keywords = List(KeywordParameter)

    #: The variadic star param.
    starparam = Str()


class Template(ASTNode):
    """ An AST node for template definitions.

    """
    #: The name given to the template.
    name = Str()

    #: The parameters associated with the template.
    parameters = Typed(TemplateParameters)

    #: The body of the template. This will be composed of ConstExpr,
    #: ChildDef, and TemplateInst nodes.
    body = List()


class TemplateArguments(ASTNode):
    """ An ASTNode representing template instatiation arguments.

    """
    #: The list of python expressions for the arguments.
    args = List(PythonExpression)

    #: The variadic argument.
    stararg = Typed(PythonExpression)


class TemplateIdentifiers(ASTNode):
    """ An AST node representing template identifiers.

    """
    #: The list of identifier names
    names = List(Str())

    #: The capturing star name.
    starname = Str()


class TemplateInst(ASTNode):
    """ An AST node for template instantiation definitions.

    """
    #: The name of the template to instantiate.
    name = Str()

    #: The arguments to pass to the template.
    arguments = Typed(TemplateArguments)

    #: The identifiers to apply to the template items.
    identifiers = Typed(TemplateIdentifiers)

    #: The body of the template instance.
    body = List()


class TemplateInstBinding(ASTNode):
    """ An AST node for a template binding.

    """
    #: The name of the object being bound.
    name = Str()

    #: The chain of names being bound on the object.
    chain = Tuple()

    #: The operator expression for the binding.
    expr = Typed(OperatorExpr)
