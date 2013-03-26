#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import itertools
from types import FunctionType

from atom.api import Value, Event, Instance

from .declarative import Declarative, d_
from .enamldef_meta import EnamlDefMeta
from .exceptions import (
    DeclarativeNameError, DeclarativeError, OperatorLookupError
)
from .operators import __get_operators as get_operators


class Resolver(object):
    """ An object which resolves the global symbols in a construct tree.

    This single public entry point for this class is the 'resolve(...)'
    classmethod.

    """
    @classmethod
    def resolve(cls, node, f_globals):
        """ Resolve the symbols and definitions for the tree.

        Resolving the tree occurs in multiple passes:
            1) Global symbols operator definitions are resolved.
            2) Classes and subclasses are generated as-needed.
            3) Members for storing local scope is added as-needed.
            4) Members for user storage definitions are added.
            5) The operators are invoked to bind the handlers.

        Changes to the tree are performed in-place.

        Parameters
        ----------
        node : EnamlDefConstruct
            The enamldef construct node to resolve.

        f_globals : dict
            The globals dictionary to use when resolving the tree.

        """
        resolver = cls(node, f_globals)
        resolver._resolve_globals()
        resolver._create_classes()
        resolver._create_local_storage()
        resolver._create_user_storage()
        resolver._call_operators()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    #: A generator expression which yields unique scope names.
    _scopenames = ('__locals_%d__' % i for i in itertools.count())

    def __init__(self, node, f_globals):
        self._root = node
        self._f_globals = f_globals
        self._operators = get_operators()

    def _raise_error(self, exc_type, msg, node):
        filename = self._root.filename
        context = self._root.typename
        raise exc_type(msg, filename, context, node.lineno)

    #--------------------------------------------------------------------------
    # Globals Resolution
    #--------------------------------------------------------------------------
    def _resolve_globals(self):
        node = self._root
        node.f_globals = self._f_globals
        try:
            baseclass = self._f_globals[node.base]
        except KeyError:
            self._raise_error(DeclarativeNameError, node.base, node)
        if (not isinstance(baseclass, type) or
            not issubclass(baseclass, Declarative)):
            msg = "cannot derive enamldef from '%s'" % node.base
            self._raise_error(DeclarativeError, msg, node)
        node.baseclass = baseclass
        for storage in node.storage_defs:
            self._resolve_storage_globals(storage)
        for binding in node.bindings:
            self._resolve_binding_globals(binding)
        for child in node.child_defs:
            self._resolve_child_globals(child)

    def _resolve_storage_globals(self, node):
        if node.typename:
            try:
                typeclass = self._f_globals[node.typename]
            except KeyError:
                try:
                    typeclass = self._f_globals['__builtins__'][node.typename]
                except KeyError:
                    exc_type = DeclarativeNameError
                    self._raise_error(exc_type, node.typename, node)
            if not isinstance(typeclass, type):
                msg = "'%s' is not a type" % node.typename
                self._raise_error(DeclarativeError, msg, node)
            node.typeclass = typeclass
        else:
            node.typeclass = object

    def _resolve_binding_globals(self, node):
        try:
            operator_func = self._operators[node.operator]
        except KeyError:
            self._raise_error(OperatorLookupError, node.operator, node)
        node.operator_func = operator_func
        f_globals = self._f_globals
        node.func = FunctionType(node.code, f_globals, node.name)
        if node.auxcode is not None:
            node.auxfunc = FunctionType(node.auxcode, f_globals, node.name)

    def _resolve_child_globals(self, node):
        try:
            typeclass = self._f_globals[node.typename]
        except KeyError:
            self._raise_error(DeclarativeNameError, node.typename, node)
        if (not isinstance(typeclass, type) or
            not issubclass(typeclass, Declarative)):
            msg = "'%s' is not a Declarative subclass" % node.typename
            self._raise_error(DeclarativeError, msg, node)
        node.typeclass = typeclass
        for storage in node.storage_defs:
            self._resolve_storage_globals(storage)
        for binding in node.bindings:
            self._resolve_binding_globals(binding)
        for child in node.child_defs:
            self._resolve_child_globals(child)

    #--------------------------------------------------------------------------
    # Class Creation
    #--------------------------------------------------------------------------
    def _create_classes(self):
        node = self._root
        dct = {}
        dct['__module__'] = self._f_globals.get('__name__', '')
        dct['__doc__'] = node.docstring
        typeclass = EnamlDefMeta(node.typename, (node.baseclass,), dct)
        node.typeclass = typeclass
        node.populate = typeclass.populator_func()
        for child in node.child_defs:
            self._create_child_classes(child)

    def _create_child_classes(self, node):
        # A child class only needs to be subclassed if it is adding
        # storage or has operator bindings. Otherwise, creating a
        # subclass just consumes unnecessary space.
        if node.storage_defs or node.bindings:
            dct = {}
            dct['__module__'] = self._f_globals.get('__name__', '')
            base = node.typeclass
            node.typeclass = type(base)(node.typename, (base,), dct)
        node.populate = node.typeclass.populator_func()
        for child in node.child_defs:
            self._create_child_classes(child)

    #--------------------------------------------------------------------------
    # Locals Storage Creation
    #--------------------------------------------------------------------------
    def _create_local_storage(self):
        # Only classes which have operator bindings need local storage.
        scopename = self._scopenames.next()
        stack = [self._root]
        while stack:
            node = stack.pop()
            if node.bindings:
                klass = node.typeclass
                members = klass.members()
                storage = Value()
                storage.set_name(scopename)
                storage.set_index(len(members))
                members[scopename] = storage
                node.scope_member = storage
                # The member is not added to the class so that it
                # remains hidden from the user and object namespace
            stack.extend(node.child_defs)

    #--------------------------------------------------------------------------
    # User Storage Creation
    #--------------------------------------------------------------------------
    def _create_user_storage(self):
        stack = [self._root]
        while stack:
            node = stack.pop()
            klass = node.typeclass
            members = klass.members()
            for storage in node.storage_defs:
                m = members.get(storage.name)
                if m is not None:
                    if m.metadata is None or not m.metadata.get('d_member'):
                        msg = "cannot override non-declarative member '%s'"
                        msg = msg % storage.name
                        self._raise_error(DeclarativeError, msg, storage)
                    if m.metadata.get('d_final'):
                        msg = "cannot override the final member '%s'"
                        msg = msg % storage.name
                        self._raise_error(DeclarativeError, msg, storage)
                if storage.kind == 'event':
                    event = Event(storage.typeclass)
                    new = d_(event, writable=False, final=False)
                else:
                    attr = Instance(storage.typeclass)
                    new = d_(attr, final=False)
                if m is not None:
                    new.set_index(m.index)
                    new.copy_static_observers(m)
                else:
                    new.set_index(len(members))
                new.set_name(storage.name)
                members[storage.name] = new
                setattr(klass, storage.name, new)
            stack.extend(node.child_defs)

    #--------------------------------------------------------------------------
    # Operator Call
    #--------------------------------------------------------------------------
    def _call_operators(self):
        stack = [self._root]
        while stack:
            node = stack.pop()
            klass = node.typeclass
            for binding in node.bindings:
                binding.operator_func(klass, binding)
            stack.extend(node.child_defs)
