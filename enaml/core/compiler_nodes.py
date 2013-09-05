#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from contextlib import contextmanager

from atom.api import Atom, Str, Typed, ForwardTyped, List
from atom.datastructures.api import sortedmap

from .expression_engine import ExpressionEngine


#: The private stack of active local scopes.
__stack = []


@contextmanager
def new_scope(seed=None):
    """ Create a new scope mapping and push it onto the stack.

    The currently active scope can be retrieved with 'peek_locals'.

    Parameters
    ----------
    seed : sortedmap, optional
        The seed map values for creating the scope.

    Returns
    -------
    result : contextmanager
        A contextmanager which will pop the scope after the context
        exits. It yields the new scope as the context variable.

    """
    if seed is not None:
        scope = seed.copy()
    else:
        scope = sortedmap()
    __stack.append(scope)
    yield scope
    __stack.pop()


def peek_scope():
    """ Get the active scope key and mapping.

    If there is no active scope, this will raise an IndexError.

    Returns
    -------
    result : sortedmap
        The active scope mapping.

    """
    return __stack[-1]


class CompilerNode(Atom):
    """ A base class for defining compiler nodes.

    """
    #: The child compiler nodes for this node.
    children = List(ForwardTyped(lambda: CompilerNode))

    def __call__(self, parent):
        """ Instantiate the type hierarchy for the node.

        This method which must be implemented by subclasses.

        Parameters
        ----------
        parent : Object or None
            The parent object for the hierarchy.

        Returns
        -------
        result : Object or list
            The Object or list of Objects created by the node.

        """
        raise NotImplementedError


class DeclarativeNode(CompilerNode):
    """ A compiler node which represents a type declaration.

    """
    #: The declarative type object to instantiate.
    klass = Typed(type)

    #: The local identifier to associate with the instance.
    identifier = Str()

    #: The key for the local block scope in the storage map.
    scope_key = Typed(object)

    #: The expression engine to associate with the instance.
    engine = Typed(ExpressionEngine)

    def __call__(self, parent):
        """ Instantiate the type hierarchy.

        Parameters
        ----------
        parent : Object or None
            The parent object for the hierarchy.

        Returns
        -------
        result : Declarative
            The declarative instance created by the node.

        """
        instance = self.klass()
        f_locals = peek_scope()
        if self.identifier:
            f_locals[self.identifier] = instance
        if self.engine:
            instance._d_storage[self.scope_key] = f_locals
            instance._d_engine = self.engine
        for node in self.children:
            node(instance)
        instance.set_parent(parent)
        return instance


class EnamlDefNode(DeclarativeNode):
    """ A compiler node which represents an 'enamldef' declaration.

    """
    #: The key object for the local scope.
    scope_key = Typed(object)

    #: The type nodes of the superclasses of the declarative.
    super_nodes = List(ForwardTyped(lambda: EnamlDefNode))

    def __call__(self, parent, **kwargs):
        """ Instantiate the type hierarchy for the node.

        Parameters
        ----------
        parent : Object or None
            The parent object for the hierarchy.

        **kwargs
            Additional metadata to pass to the constructor.

        Returns
        -------
        result : Declarative
            The declarative instance created by the node.

        """
        instance = self.klass.__new__(self.klass)
        for node in self.super_nodes:
            node.populate(instance)
        self.populate(instance)
        instance.__init__(parent, **kwargs)
        return instance

    def populate(self, instance):
        """ Populate the type instance with the node children.

        """
        with new_scope() as f_locals:
            if self.identifier:
                f_locals[self.identifier] = instance
            if self.engine:
                instance._d_storage[self.scope_key] = f_locals
                instance._d_engine = self.engine
            for node in self.children:
                node(instance)


class TemplateNode(CompilerNode):
    """ A compiler node which represents a template declaration.

    """
    #: The local scope for the template instantiation.
    template_scope = Typed(sortedmap, ())

    def __call__(self, parent):
        """ Instantiate the type hierarchy.

        Parameters
        ----------
        parent : Object or None
            The parent object of the declarative.

        Returns
        -------
        result : list
            The list of declarative objects generated by the template.

        """
        instances = []
        with new_scope(self.template_scope):
            for node in self.children:
                value = node(parent)
                if isinstance(value, list):
                    instances.extend(value)
                else:
                    instances.append(value)
        return instances


class TemplateInstNode(CompilerNode):
    """ A compiler node which represents a template instantiation.

    """
    #: The template node for the instantiation.
    template_node = Typed(TemplateNode)

    def __call__(self, parent):
        """ Instantiate the type hierarchy.

        Parameters
        ----------
        parent : Object or None
            The parent object of the template instance.

        Returns
        -------
        result : list
            The list of declarative objects generated by the template.

        """
        return self.template_node(parent)
