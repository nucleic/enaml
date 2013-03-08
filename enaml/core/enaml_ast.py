#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
class ASTNode(object):
    """ The base Enaml AST node.

    Attributes
    ----------
    lineno : int
        The line number in the source code that created this node.

    """
    def __init__(self, lineno):
        self.lineno = lineno

    def __repr__(self):
        return self.__class__.__name__

    def __str__(self):
        return repr(self)


class Module(ASTNode):
    """ An AST node representing an Enaml module.

    Attributes
    ----------
    doc : str
        The module's documentation string.

    body : list
        A list of ast nodes comprising the body of the module.

    """
    def __init__(self, body, lineno):
        super(Module, self).__init__(lineno)
        self.body = body


class Python(ASTNode):
    """ An AST node representing a chunk of pure Python code.

    Attributes
    ----------
    py_ast : ast.AST
        A Python ast node.

    """
    def __init__(self, py_ast, lineno):
        super(Python, self).__init__(lineno)
        self.py_ast = py_ast


class Declaration(ASTNode):
    """ An AST node representing an Enaml declaration.

    Attributes
    ----------
    name : str
        The name of the declaration.

    base : str
        The name of the base type.

    identifier : str
        The local identifier to use for instances of the declaration.

    doc : str
        The documentation string for the declaration.

    body : list
        A list of AST nodes that comprise the body of the declaration.

    """
    def __init__(self, name, base, identifier, doc, body, lineno):
        super(Declaration, self).__init__(lineno)
        self.name = name
        self.base = base
        self.identifier = identifier
        self.doc = doc
        self.body = body


class Instantiation(ASTNode):
    """ An AST node representing a declaration instantiation.

    Attributes
    ----------
    name : str
        The name of declaration being instantiated.

    identifier : str
        The local identifier to use for the new instance.

    body : list
        A list of AST nodes which comprise the instantiation body.

    """
    def __init__(self, name, identifier, body, lineno):
        super(Instantiation, self).__init__(lineno)
        self.name = name
        self.identifier = identifier
        self.body = body


class AttributeDeclaration(ASTNode):
    """ An AST node which represents an attribute declaration.

    Attributes
    ----------
    name : str
        The name of the attribute being declared.

    type : str
        A string representing the type of the attribute, or None if no
        type was given. If None the attribute can be of any type.

    default : AttributeBinding or None
        The default binding of the attribute, or None if no default
        is provided.

    is_event : boolean
        Whether or not this declaration represents an event.
        i.e. was declared with 'event' instead of 'attr'.

    """
    def __init__(self, name, type, default, is_event, lineno):
        super(AttributeDeclaration, self).__init__(lineno)
        self.name = name
        self.type = type
        self.default = default
        self.is_event = is_event


class AttributeBinding(ASTNode):
    """ An AST node which represents an expression attribute binding.

    Attributes
    ----------
    name : str
        The name of the attribute being bound.

    binding : BoundExpression
        The BoundExpression ast node which represents the binding.

    """
    def __init__(self, name, binding, lineno):
        super(AttributeBinding, self).__init__(lineno)
        self.name = name
        self.binding = binding


class BoundExpression(ASTNode):
    """ An ast node which represents a bound expression.

    Attributes
    ----------
    op : str
        The name of the operator that will perform the binding.

    expr : Python
        A Python ast node that reprents the bound expression.

    """
    def __init__(self, op, expr, lineno):
        super(BoundExpression, self).__init__(lineno)
        self.op = op
        self.expr = expr

