#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from types import FunctionType

from atom.api import Typed, Value, Event

from .declarative import Declarative, d_
from .enaml_def import EnamlDef
from .exceptions import (
    DeclarativeNameError, DeclarativeError, OperatorLookupError,
)
from .operators import DEFAULT_OPERATORS


def _do_process_enamldef(klass, descr, f_globals):
    """ A helper function which post processes an enamldef class.

    The post processing phase is responsible for adding member storage
    for local scope dicts, resolving class types for the descriptions,
    adding the user defined attributes and events, making the functions
    for the expression code objects, and calling the operators to bind
    the expressions.

    Parameters
    ----------
    klass : EnamlDef
        The enamldef class to be processed.

    descr : dict
        The description dictionary for the enamldef.

    f_globals : dict
        The global scope of the .enaml module.

    """
    # Add the resolved class definition for the enamldef. Since the
    # enamldef is already an independent subclass, it does not need
    # to be subclassed again before the transformations are made.
    # If the class has no __operators__ attribute then the default
    # operators will be used. Operators can be applied by using a
    # decorator or by setting the attribute before the module has
    # been fully imported.
    descr['class'] = klass
    if not hasattr(klass, '__operators__'):
        operators = klass.__operators__ = DEFAULT_OPERATORS
    else:
        operators = klass.__operators__

    # Pass over the child descriptions and resolve the classes. Child
    # types with user attrs or bound expressions are subclassed.
    stack = list(descr['children'])
    while stack:
        d = stack.pop()
        try:
            rcls = f_globals[d['type']]
        except KeyError:
            raise DeclarativeNameError(d['type'], d)
        if not isinstance(rcls, type) or not issubclass(rcls, Declarative):
            message = "'%s' is not a Declarative subclass" % d['type']
            raise DeclarativeError(message, d)
        if d['bindings'] or d['attrs']:
            modname = f_globals['__name__']
            dct = {'__module__': modname, '__doc__': rcls.__doc__}
            d['class'] = type(rcls)(rcls.__name__, (rcls,), dct)
        else:
            d['class'] = rcls
        stack.extend(d['children'])

    # After the classes are resolved and the subclasses created, the
    # member creations and transformations can be performed.
    stack = [descr]
    while stack:
        d = stack.pop()
        thisklass = d['class']
        members = thisklass.members()

        # If the block has locals and the given item has bindings, then
        # a member needs to be added to store the scope. It is possible
        # that the member was already added by '_make_enamldef_helper_'.
        scopename = d['scopename']
        if scopename and scopename not in members and d['bindings']:
            v = Value()
            v.set_name(scopename)
            v.set_index(len(members))
            members[scopename] = v
            setattr(thisklass, scopename, v)

        # Add the user defined attributes. If an attribute cannot be
        # overridden, an appropriate exception will be raised.
        for attr in d['attrs']:
            attrname = attr['name']
            if attrname in members:
                m = members[attrname]
                if m.metadata is None or not m.metadata.get('d_member'):
                    message = "cannot override non-declarative member '%s'"
                    message = message % attrname
                    raise DeclarativeError(message, attr)
                if m.metadata.get('d_final'):
                    message = "cannot override the final member '%s'"
                    message = message % attrname
                    raise DeclarativeError(message, attr)
            attrtypename = attr['type']
            if attrtypename:
                try:
                    attrtype = f_globals[attrtypename]
                except KeyError:
                    try:
                        attrtype = f_globals['__builtins__'][attrtypename]
                    except KeyError:
                        raise DeclarativeNameError(attrtypename, attr)
            else:
                attrtype = object
            if attr['is_event']:
                newmember = d_(Event(attrtype), writable=False)
            else:
                newmember = d_(Typed(attrtype))
            if attrname in members:
                m = members[attrname]
                newmember.set_index(m.index)
                newmember.copy_static_observers(m)
            else:
                newmember.set_index(len(members))
            newmember.set_name(attrname)
            members[attrname] = newmember
            setattr(thisklass, attrname, newmember)

        # Create the function objects for the operator bindings and
        # call the operators to bind the expressions.
        for b in d['bindings']:
            code = b['code']
            name = b['name']
            # If the code is a tuple, it represents the ':=' operator
            # which is a combination of '<<' and '>>' functions.
            if isinstance(code, tuple):
                sub_code, upd_code = code
                func = FunctionType(sub_code, f_globals, name)
                func2 = FunctionType(upd_code, f_globals, name)
                b['func'] = func
                b['func2'] = func2  # TODO this could be cleaner
            else:
                func = FunctionType(code, f_globals, name)
                b['func'] = func
            try:
                operator = operators[b['operator']]
            except KeyError:
                raise OperatorLookupError(b['operator'], b)
            operator(thisklass, b)

        # Process the children of the description.
        stack.extend(d['children'])


def _post_process_enamldefs_(enamldefs, f_globals):
    """ Post process the descriptions created by the compiler.

    This function will resolve the symbols for the class definitions and
    create the necessary subclasses with relevant bound expressions.

    This function is imported and called by code generated by the Enaml
    compiler when it parses and compiles a .enaml file.

    Parameters
    ----------
    enamldefs : list
        A list of 2-tuples of the form (class, descr) where the class
        is an enamldef class and descr is the description dict for that
        class.

    f_globals : dict
        The dictionary of globals for the .enaml module.

    """
    for klass, descr in enamldefs:
        _do_process_enamldef(klass, descr, f_globals)


def _make_enamldef_helper_(name, base, description, f_globals):
    """ A compiler helper function for creating a new EnamlDef type.

    This function is called by the bytecode generated by the Enaml
    compiler when an enaml module is imported. It is used to make new
    types from the 'enamldef' keyword.

    This helper will raise an exception if the base type is of an
    incompatible type.

    Parameters
    ----------
    name : str
        The name to use when generating the new type.

    base : type
        The base class to use for the new type. This must be a subclass
        of Declarative.

    description : dict
        The description dictionay by the Enaml compiler. This dict will
        be used during instantiation to populate new instances with
        children and bound expressions.

    f_globals : dict
        The dictionary of globals for objects created by this class.

    Returns
    -------
    result : EnamlDef
        A new enamldef subclass of the given base class.

    """
    if not isinstance(base, type) or not issubclass(base, Declarative):
        msg = "can't derive enamldef from '%s'"
        raise TypeError(msg % base)
    dct = {}
    dct['__module__'] = f_globals.get('__name__', '')
    dct['__doc__'] = description['doc']
    # Add the member which will hold the local scope dict for the given
    # scope name. This needs to be done before the post process handler
    # creates any subclasses of the enamldef during class resolution.
    #
    # TODO I think local scope management can be done better.
    scopename = description['scopename']
    if scopename and description['bindings']:
        dct[scopename] = Value()
    decl_cls = EnamlDef(name, (base,), dct)
    decl_cls.__descriptions__ += ((description, f_globals),)
    return decl_cls
