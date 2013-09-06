#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from contextlib import contextmanager

from atom.api import Atom, Str, Tuple, Typed, ForwardTyped, List
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

        This is invoked by other compiler nodes when a hierarchy is
        being instantiated.

        Parameters
        ----------
        parent : Declarative or None
            The parent declarative object for the hierarchy.

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

    def size(self):
        """ Return the size of the instantiated node.

        """
        return 1


class EnamlDefNode(DeclarativeNode):
    """ A compiler node which represents an 'enamldef' declaration.

    """
    #: The type nodes of the superclasses of the declarative.
    super_nodes = List(ForwardTyped(lambda: EnamlDefNode))

    def __call__(self, instance):
        """ Instantiate the type hierarchy for the node.

        This is invoked by the EnamlDefMeta class when an enamldef
        class is called. The metaclass creates the new instances and
        passes it as the argument. This is done so that subclasses of
        the enamldef work properly without requiring a copy of the
        compiler node.

        Parameters
        ----------
        instance : EnamlDef
            The enamldef instance which should be populated.

        """
        for node in self.super_nodes:
            node.populate(instance)
        self.populate(instance)

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


class DeclarativeInterceptNode(DeclarativeNode):
    """ A DeclarativeNode which intercepts child creation.

    """
    def __call__(self, parent):
        """ Instantiate the type hierarchy.

        This is invoked by other compiler nodes when a hierarchy is
        being instantiated.

        Parameters
        ----------
        parent : Declarative or None
            The parent declarative object for the hierarchy.

        Returns
        -------
        result : Declarative
            The declarative instance created by the node.

        """
        klass = self.klass
        instance = klass()
        f_locals = peek_scope()
        if self.identifier:
            f_locals[self.identifier] = instance
        if self.engine:
            instance._d_storage[self.scope_key] = f_locals
            instance._d_engine = self.engine
        instance.child_node_intercept(self.children[:], f_locals)
        instance.set_parent(parent)
        return instance


class EnamlDefInterceptNode(EnamlDefNode):
    """ An EnamlDefNode which intercepts child creation.

    """
    def populate(self, instance):
        """ Populate the type instance with the node children.

        """
        with new_scope() as f_locals:
            if self.identifier:
                f_locals[self.identifier] = instance
            if self.engine:
                instance._d_storage[self.scope_key] = f_locals
                instance._d_engine = self.engine
            instance.child_node_intercept(self.children[:], f_locals)


class TemplateNode(CompilerNode):
    """ A compiler node which represents a template declaration.

    """
    #: The local scope for the template instantiation.
    template_scope = Typed(sortedmap, ())

    def __call__(self, parent):
        """ Instantiate the type hierarchy.

        Parameters
        ----------
        parent : Declarative or None
            The parent declarative object for the templates.

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

    def size(self):
        """ Return the size of the instantiated node.

        """
        return sum(child.size() for child in self.children)


class TemplateInstNode(CompilerNode):
    """ A compiler node which represents a template instantiation.

    This compiler node will never have children.

    """
    #: The template node which will create the instances.
    template_node = Typed(TemplateNode)

    #: The named identifiers for the instantiated objects.
    names = Tuple()

    #: The starname identifier for the instantiated objects.
    starname = Str()

    def __call__(self, parent):
        """ Invoke the template instantiation to build the objects.

        Parameters
        ----------
        parent : Declarative
            The parent declarative object for the instantiation.

        """
        instances = self.template_node(parent)
        f_locals = peek_scope()
        if self.names:
            for name, instance in zip(self.names, instances):
                f_locals[name] = instance
        if self.starname:
            f_locals[self.starname] = tuple(instances[len(self.names):])
        return instances

    def size(self):
        """ Return the size of the instantiated node.

        """
        return self.template_node.size()
