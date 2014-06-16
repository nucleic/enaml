#------------------------------------------------------------------------------
# Copyright (c) 2014, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .dynamicscope import DynamicScope
from .funchelper import call_func


def _super_disallowed(*args, **kwargs):
    """ A function which disallows super() in a declarative function.

    """
    msg = ('super() is not allowed in a declarative function, '
           'use SomeClass.some_method(self, ...) instead.')
    raise TypeError(msg)


def _invoke(func, key, self, args, kwargs):
    """ Invoke a declarative function.

    Parameters
    ----------
    func : FunctionType
        The Python function to invoke.

    key : object
        The local scope key for the scope locals.

    self : Declarative
        The declarative context 'self' object.

    args : tuple
        The positional arguments to pass to the function.

    kwargs : dict
        The keyword arguments to pass to the function.

    """
    f_globals = func.func_globals
    f_builtins = f_globals['__builtins__']
    f_locals = self._d_storage.get(key) or {}
    scope = DynamicScope(self, f_locals, f_globals, f_builtins)
    scope['super'] = _super_disallowed
    return call_func(func, args, kwargs, scope)


class DeclarativeFunction(object):
    """ A descriptor which implements a declarative function.

    """
    # XXX move this class to C++
    __slots__ = ('im_func', 'im_key')

    def __init__(self, im_func, im_key):
        """ Initialize a DeclarativeFunction.

        Parameters
        ----------
        im_func : FunctionType
            The Python function which implements the actual logic.

        im_key : object
            The scope key to lookup the function locals.

        """
        self.im_func = im_func
        self.im_key = im_key

    @property
    def _d_func(self):
        """ An internal compiler metadata flag.

        This allows the function to be overridden from Enaml syntax.

        """
        return True

    def __repr__(self):
        """ Returns a nice string representation of the function.

        """
        im_func = self.im_func
        args = (im_func.__module__, im_func.__name__)
        return '<declarative function %s.%s>' % args

    def __get__(self, im_self, im_class):
        """ Invoke the descriptor protocol for the function.

        If accessed unbound, this method returns 'self'. Otherwise, it
        returns a bound declarative method object.

        Parameters
        ----------
        im_self : Declarative
            The declarative instance owner object.

        im_class : type
            The declarative class type owner.

        """
        if im_self is None:
            return self
        return BoundDeclarativeMethod(
            self.im_func, self.im_key, im_self, im_class)

    def __call__(self, im_self, *args, **kwargs):
        """ Invoke the unbound declarative function.

        Parameters
        ----------
        im_self : Declarative
            The declarative instance owner object.

        *args
            The positional arguments to pass to the function.

        **kwargs
            The keyword arguments to pass to the function.

        """
        return _invoke(self.im_func, self.im_key, im_self, args, kwargs)


class BoundDeclarativeMethod(object):
    """ An object which represents a bound declarative method.

    """
    # XXX move this class to C++
    __slots__ = ('im_func', 'im_key', 'im_self', 'im_class')

    def __init__(self, im_func, im_key, im_self, im_class):
        """ Initialize a BoundDeclarativeMethod.

        Parameters
        ----------
        im_func : FunctionType
            The Python function which implements the actual logic.

        im_key : object
            The scope key to lookup the function locals.

        im_self : Declarative
            The declarative 'self' context for the function.

        im_class : type
            The type of the declarative context object.

        """
        self.im_func = im_func
        self.im_key = im_key
        self.im_self = im_self
        self.im_class = im_class

    def __repr__(self):
        """ Returns a nice string representation of the method.

        """
        im_func = self.im_func
        im_self = self.im_self
        im_class = self.im_class
        args = (im_class.__name__, im_func.__name__, im_self)
        return '<bound declarative method %s.%s of %r>' % args

    def __call__(self, *args, **kwargs):
        """ Invoke the unbound declarative method object.

        Parameters
        ----------
        *args
            The positional arguments to pass to the function.

        **kwargs
            The keyword arguments to pass to the function.

        """
        return _invoke(self.im_func, self.im_key, self.im_self, args, kwargs)
