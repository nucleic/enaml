#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import ast

from atom.api import Atom, Bool, Enum, Int, List, Str, Instance, Tuple, Typed


class ASTNode(Atom):
    """ The base class for Enaml ast nodes.

    """
    #: The line number in the .enaml file which generated the node.
    lineno = Int(-1)


class PragmaArg(Atom):
    """ An atom class which represents a pragma argument.

    """
    #: The kind of the argument.
    kind = Enum("token", "number", "string")

    #: The value of the argument.
    value = Str()


class Pragma(ASTNode):
    """ An AST node which represents a $pragma expression.

    """
    #: The pragma command to execute.
    command = Str()

    #: The list of arguments for the command.
    arguments = List(PragmaArg)


class Module(ASTNode):
    """ An ASTNode representing an Enaml module.

    """
    #: The list of ast nodes for the body of the module. This will be
    #: composed of PythonModule, EnamlDef, and Template nodes.
    body = List()

    #: The pragmas to apply for the module.
    pragmas = List(Pragma)


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

    #: The pragmas to apply to the enamldef.
    pragmas = List(Pragma)

    #: The list of body nodes for the enamldef. This will be composed
    #: of StorageExpr, Binding, FuncDef, ChildDef and TemplateInst nodes.
    body = List()


class ChildDef(ASTNode):
    """ An ASTNode representing a child definition.

    """
    #: The type name of the child to create.
    typename = Str()

    #: The identifier given to the child.
    identifier = Str()

    #: The list of body nodes for the child def. This will be composed
    #: of StorageExpr, Binding, FuncDef, ChildDef and TemplateInst nodes.
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


class FuncDef(ASTNode):
    """ An AST node which represents a 'func' declaration or override.

    """
    #: The Python function definition.
    funcdef = Typed(ast.FunctionDef)

    #: Whether the function is an override or a 'func' declaration.
    is_override = Bool(False)


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

    #: The pragmas to apply to the template.
    pragmas = List(Pragma)

    #: The parameters associated with the template.
    parameters = Typed(TemplateParameters)

    #: The docstring for the template.
    docstring = Str()

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

    #: The pragmas to apply to the template instance.
    pragmas = List(Pragma)

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


class ASTVisitor(Atom):
    """ A base class for creating AST visitors.

    """
    #: An internal stack of the nodes being visited.
    _node_stack = List()

    def visit(self, node, *args, **kwargs):
        """ The main visitor dispatch method.

        This method will dispatch to a method which has a name which
        matches the pattern visit_<type> where <type> is the name of
        the type of the node. If no visitor method for the node exists,
        the 'default_visit' method will be invoked.

        Parameters
        ----------
        node : object
            The ast node of interest.

        *args
            Additional arguments to pass to the visitor.

        **kwargs
            Additional keywords to pass to the visitor.

        Returns
        -------
        result : object
            The object returned by the visitor, if any.

        """
        name = 'visit_' + type(node).__name__
        visitor = getattr(self, name, None)
        if visitor is None:
            visitor = self.default_visit
        self._node_stack.append(node)
        try:
            result = visitor(node, *args, **kwargs)
        finally:
            self._node_stack.pop()
        return result

    def default_visit(self, node, *args, **kwargs):
        """ The default node visitor method.

        This method is invoked when no named visitor method is found
        for a given node. This default behavior raises an exception for
        the missing handler. Subclasses may reimplement this method for
        custom default behavior.

        """
        msg = "no visitor found for node of type `%s`"
        raise TypeError(msg % type(node).__name__)

    def ancestor(self, n=1):
        """ Retrieve an ancestor node from the internal stack.

        Parameters
        ----------
        n : int, optional
            The depth of the target parent in the ancestry. The default
            is 1 and indicates the parent of the active node.

        Returns
        -------
        result : ASTNode or None
            The desired ancestor node, or None if the index is out of
            range.

        """
        try:
            # the -1 index is the current node
            result = self._node_stack[-1 - n]
        except IndexError:
            result = None
        return result
