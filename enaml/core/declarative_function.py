#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .dynamicscope import DynamicScope
from .funchelper import call_func


class DeclarativeFunction(object):
    """ A descriptor which represents a declarative function.

    """
    # XXX move this class to C++
    __slots__ = ('__func__', '__key__')

    def __init__(self, im_func, im_key):
        """ Initialize a DeclarativeFunction.

        Parameters
        ----------
        im_func : FunctionType
            The Python function which implements the logic.

        im_key : object
            The scope im_key to lookup the function locals.

        """
        self.__func__ = im_func
        self.__key__ = im_key

    def __repr__(self):
        mod = self.__func__.__module__
        name = self.__func__.__name__
        return '<declarative function %s.%s>' % (mod, name)

    def __get__(self, im_self, im_class):
        if im_self is None:
            return self
        im_func = self.__func__
        im_key = self.__key__
        return BoundDeclarativeMethod(im_func, im_self, im_class, im_key)


class BoundDeclarativeMethod(object):
    """ An object which represents a bound declarative method.

    """
    # XXX move this class to C++
    __slots__ = ('__func__', '__self__', '__class__', '__key__')

    def __init__(self, im_func, im_self, im_class, im_key):
        """ Initialize a BoundDeclarativeMethod.

        Parameters
        ----------
        im_func : FunctionType
            The Python function which implements the logic.

        im_self : Declarative
            The declarative 'self' context for the function.

        im_class : Declarative type
            The class of the 'self' argument.

        key : object
            The scope key to lookup the function locals.

        """
        self.__func__ = im_func
        self.__self__ = im_self
        self.__class__ = im_class
        self.__key__ = im_key

    def __repr__(self):
        cls_name = self.__class__.__name__
        name = self.__func__.__name__
        args = (cls_name, name, self.__self__)
        return "<bound declarative method %s.%s of %s>" % args

    def __call__(self, *args, **kwargs):
        func = self.__func__
        f_globals = func.func_globals
        f_builtins = f_globals['__builtins__']
        im_self = self.__self__
        f_locals = im_self._d_storage.get(self.__key__) or {}
        scope = DynamicScope(im_self, f_locals, f_globals, f_builtins)
        return call_func(func, (), {}, scope)
