#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Typed

from . import enaml_ast


class VarPool(Atom):
    """ A class for generating private variable names.

    """
    #: The pool of currently used variable names.
    pool = Typed(set, ())

    def new(self):
        """ Get a new private variable name.

        Returns
        -------
        result : str
            An unused variable name.

        """
        var = '_[var_%d]' % len(self.pool)
        self.pool.add(var)
        return var

    def release(self, name):
        """ Return a variable name to the pool.

        Parameters
        ----------
        name : str
            The variable name which is free to be reused.

        """
        self.pool.discard(name)


def has_identifiers(node):
    """ Return whether an ast node or its decendants has identifiers.

    Parameters
    ----------
    node : ASTNode
        The Enaml ast node of interest.

    Returns
    -------
    result : bool
        True if the node or any of its decendants has declared
        identifiers, False otherwise.

    """
    EnamlDef = enaml_ast.EnamlDef
    ChildDef = enaml_ast.ChildDef
    Template = enaml_ast.Template
    TemplateInst = enaml_ast.TemplateInst
    stack = [node]
    while stack:
        node = stack.pop()
        if isinstance(node, (ChildDef, EnamlDef)):
            if node.identifier:
                return True
            stack.extend(node.body)
        elif isinstance(node, TemplateInst):
            if node.identifiers:
                return True
            stack.extend(node.body)
        elif isinstance(node, Template):
            stack.extend(node.body)
    return False


def needs_engine(node):
    """ Get whether or not a node needs an expression engine.

    A node requires an engine if it has attribute bindings.

    Parameters
    ----------
    node : EnamlDef or ChildDef
        The enaml ast node of interest.

    Returns
    -------
    result : bool
        True if the node class requires an engine, False otherwise.

    """
    Binding = enaml_ast.Binding
    StorageExpr = enaml_ast.StorageExpr
    for item in node.body:
        if isinstance(item, Binding):
            return True
        if isinstance(item, StorageExpr):
            if item.expr is not None:
                return True
    return False


def needs_subclass(node):
    """ Get whether or not a ChildDef node needs subclassing.

    A child def class must be subclassed if it uses storage or
    has attribute bindings.

    Parameters
    ----------
    node : ChildDef
        The child def node of interest.

    Returns
    -------
    result : bool
        True if the class must be subclassed, False otherwise.

    """
    types = (enaml_ast.StorageExpr, enaml_ast.Binding)
    return any(isinstance(item, types) for item in node.body)
