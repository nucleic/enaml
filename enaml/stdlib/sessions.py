#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
""" Enaml Standard Library - Sessions

This module contains some Session subclasses and associated utilities that
handle common Session use cases.

"""
from collections import Iterable
from functools import wraps

from atom.api import Callable, Tuple, Dict

from enaml.session import Session
from enaml.session_factory import SessionFactory


class SimpleSession(Session):
    """ A concrete Session class that receives a callable, positional,
    and keyword arguments and creates the associated view(s).

    """
    #: The callable to invoke to create the session windows.
    session_callable = Callable(lambda *args, **kwargs: [])

    #: The arguments to pass to the callable.
    args = Tuple()

    #: The keyword arguments to pass to the callable.
    kwargs = Dict()

    def on_open(self):
        """ Create the view from the callable

        """
        w = self.session_callable(*self.args, **self.kwargs)
        if isinstance(w, Iterable):
            self.windows.extend(w)
        else:
            self.windows.append(w)


def simple_session(sess_name, sess_descr, sess_callable, *args, **kwargs):
    """ Creates a SessionFactory instance for a callable.

    This creates a SessionFactory instance which will create instances
    of SimpleSession when prompted by the application.

    Parameters
    ----------
    sess_name : str
        A unique, human-friendly name for the session.

    sess_descr : str
        A brief description of the session.

    sess_callable : callable
        A callable which will return an Enaml view or iterable of views.

    *args, **kwargs
        Optional positional and keyword arguments to pass to the callable
        when the session is created.

    """
    kwds = dict(session_callable=sess_callable, args=args, kwargs=kwargs)
    fact = SessionFactory(sess_name, sess_descr, SimpleSession, **kwds)
    return fact


def view_factory(sess_name=None, sess_descr=None):
    """ A decorator that creates a session factory from a callable.

    This can be used in the following ways:

        @view_factory
        def view(...):
            ...
            return View(...)

        @view_factory('my-views', 'This is several views')
        def views(...):
            ...
            return [View1(...), View2(...)]

        simple = view_factory(Main)

    """
    def wrapper(func, _name, _descr):
        if _name is None:
            _name = func.__name__
        if _descr is None:
            _descr = func.__doc__ or 'no description'
        @wraps(func)
        def closure(*args, **kwargs):
            return simple_session(_name, _descr, func, *args, **kwargs)
        return closure
    if sess_name is not None and callable(sess_name):
        return wrapper(sess_name, None, sess_descr)
    def _wrapper(func):
        return wrapper(func, sess_name, sess_descr)
    return _wrapper


def show_simple_view(view, toolkit='qt', description=''):
    """ Display a simple view to the screen in the local process.

    Parameters
    ----------
    view : Object
        The top level Object to use as the view.

    toolkit : string, optional
        The toolkit backend to use to display the view. Currently
        supported values are 'qt' and 'wx'. The default is 'qt'.
        Note that not all functionality is available on Wx.

    description : string, optional
        An optional description to give to the session.

    """
    f = lambda: view
    if toolkit == 'qt':
        from enaml.qt.qt_application import QtApplication
        app = QtApplication([simple_session('main', description, f)])
    elif toolkit == 'wx':
        from enaml.wx.wx_application import WxApplication
        app = WxApplication([simple_session('main', description, f)])
    else:
        raise ValueError('Unknown toolkit `%s`' % toolkit)
    app.start_session('main')
    app.start()
    return app

