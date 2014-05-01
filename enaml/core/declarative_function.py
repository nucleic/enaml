#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .dynamicscope import DynamicScope
from .funchelper import call_func


def d_virtual(func):
    """ A decorator for creating declarative virtual method.

    This decorator can be applied to a method of a Declarative subclass
    in order to allow that method to be overriden using Enaml method
    override syntax.

    Parameters
    ----------
    func : FunctionType
        The function to make declarative virtual.

    Returns
    -------
    result : func
        The original function tagged with the appropriate metadata
        for the compiler.

    """
    func._d_virtual = True
    return func


class DeclarativeFunction(object):
    """ A descriptor which represents a declarative function.

    """
    # XXX move this class to C++
    __slots__ = ('im_func', 'im_key', '_d_virtual')

    def __init__(self, im_func, im_key):
        """ Initialize a DeclarativeFunction.

        Parameters
        ----------
        im_func : FunctionType
            The Python function which implements the logic.

        im_key : object
            The scope im_key to lookup the function locals.

        """
        self.im_func = im_func
        self.im_key = im_key
        self._d_virtual = True

    def __repr__(self):
        mod = self.im_func.__module__
        name = self.im_func.__name__
        return '<declarative function %s.%s>' % (mod, name)

    def __get__(self, im_self, im_class):
        if im_self is None:
            return self
        im_func = self.im_func
        im_key = self.im_key
        return BoundDeclarativeMethod(im_func, im_self, im_key)


class BoundDeclarativeMethod(object):
    """ An object which represents a bound declarative method.

    """
    # XXX move this class to C++
    __slots__ = ('im_func', 'im_self', 'im_key')

    def __init__(self, im_func, im_self, im_key):
        """ Initialize a BoundDeclarativeMethod.

        Parameters
        ----------
        im_func : FunctionType
            The Python function which implements the logic.

        im_self : Declarative
            The declarative 'self' context for the function.

        key : object
            The scope key to lookup the function locals.

        """
        self.im_func = im_func
        self.im_self = im_self
        self.im_key = im_key

    def __repr__(self):
        im_self = self.im_self
        args = (self.im_func.__name__, type(im_self).__name__, im_self)
        return "<bound declarative method %s.%s of %r>" % args

    def __call__(self, *args, **kwargs):
        im_func = self.im_func
        f_globals = im_func.func_globals
        f_builtins = f_globals['__builtins__']
        im_self = self.im_self
        f_locals = im_self._d_storage.get(self.im_key) or {}
        scope = DynamicScope(im_self, f_locals, f_globals, f_builtins)
        return call_func(im_func, args, kwargs, scope)
