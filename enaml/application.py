#------------------------------------------------------------------------------
# Copyright (c) 2014, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from heapq import heappush, heappop
from itertools import count
from threading import Lock

from atom.api import (
    Atom, Bool, Typed, ForwardTyped, Tuple, Dict, Callable, Value, List,
    observe
)


class ScheduledTask(Atom):
    """ An object representing a task in the scheduler.

    """
    #: The callable to run when the task is executed.
    _callback = Callable()

    #: The args to pass to the callable.
    _args = Tuple()

    #: The keywords to pass to the callable.
    _kwargs = Dict()

    #: The result of invoking the callback.
    _result = Value()

    #: Whether or not the task is still valid.
    _valid = Bool(True)

    #: Whether or not the task is still pending.
    _pending = Bool(True)

    #: A callable to invoke with the result of running the task.
    _notify = Callable()

    def __init__(self, callback, args, kwargs):
        """ Initialize a ScheduledTask.

        Parameters
        ----------
        callback : callable
            The callable to run when the task is executed.

        args : tuple
            The tuple of positional arguments to pass to the callback.

        kwargs : dict
            The dict of keyword arguments to pass to the callback.

        """
        self._callback = callback
        self._args = args
        self._kwargs = kwargs

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _execute(self):
        """ Execute the underlying task. This should only been called
        by the scheduler loop.

        """
        try:
            if self._valid:
                self._result = self._callback(*self._args, **self._kwargs)
                if self._notify is not None:
                    self._notify(self._result)
        finally:
            del self._notify
            self._pending = False

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def notify(self, callback):
        """ Set a callback to be run when the task is executed.

        Parameters
        ----------
        callback : callable
            A callable which accepts a single argument which is the
            results of the task. It will be invoked immediate after
            the task is executed, on the main event loop thread.

        """
        self._notify = callback

    def pending(self):
        """ Returns True if this task is pending execution, False
        otherwise.

        """
        return self._pending

    def unschedule(self):
        """ Unschedule the task so that it will not be executed. If
        the task has already been executed, this call has no effect.

        """
        self._valid = False

    def result(self):
        """ Returns the result of the task, or ScheduledTask.undefined
        if the task has not yet been executed, was unscheduled before
        execution, or raised an exception on execution.

        """
        return self._result


class ProxyResolver(Atom):
    """ An object which resolves requests for proxy objects.

    """
    #: A dictionary of factories functions to use when resolving the
    #: proxy. The function should take no arguments, and return the
    #: proxy class when called.
    factories = Dict()

    def resolve(self, name):
        """ Resolve the given name to a proxy calls.

        For example, 'Field' should resolve to a class which implements
        the ProxyField interface.

        Parameters
        ----------
        name : string
            The name of the proxy object to resolve.

        Returns
        -------
        result : type or None
            A class which implements the proxy interface, or None if
            no class can be found for the given name.

        """
        factory = self.factories.get(name)
        if factory is not None:
            return factory()


def StyleSheet():
    """ A lazy importer for the Enaml StyleSheet class.

    """
    from enaml.styling import StyleSheet
    return StyleSheet


class Application(Atom):
    """ The application object which manages the top-level communication
    protocol for serving Enaml views.

    """
    #: The proxy resolver to use for the application. This will normally
    #: be supplied by application subclasses, but can also be supplied
    #: by the developer to supply custom proxy resolution behavior.
    resolver = Typed(ProxyResolver)

    #: The style sheet to apply to the entire application.
    style_sheet = ForwardTyped(StyleSheet)

    #: The task heap for application tasks.
    _task_heap = List()

    #: The counter to break heap ties.
    _counter = Value(factory=count)

    #: The heap lock for protecting heap access.
    _heap_lock = Value(factory=Lock)

    #: Private class storage for the singleton application instance.
    _instance = None

    @staticmethod
    def instance():
        """ Get the global Application instance.

        Returns
        -------
        result : Application or None
            The global application instance, or None if one has not yet
            been created.

        """
        return Application._instance

    def __new__(cls, *args, **kwargs):
        """ Create a new Enaml Application.

        There may be only one application instance in existence at any
        point in time. Attempting to create a new Application when one
        exists will raise an exception.

        """
        if Application._instance is not None:
            raise RuntimeError('An Application instance already exists')
        self = super(Application, cls).__new__(cls, *args, **kwargs)
        Application._instance = self
        return self

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _process_task(self, task):
        """ Processes the given task, then dispatches the next task.

        """
        try:
            task._execute()
        finally:
            self._next_task()

    def _next_task(self):
        """ Pulls the next task off the heap and processes it on the
        main gui thread.

        """
        heap = self._task_heap
        with self._heap_lock:
            if heap:
                priority, ignored, task = heappop(heap)
                self.deferred_call(self._process_task, task)

    @observe('style_sheet.destroyed')
    def _clear_destroyed_style_sheet(self, change):
        """ An observer which clears a destroyed style sheet.

        """
        self.style_sheet = None

    @observe('style_sheet')
    def _invalidate_style_cache(self, change):
        """ An observer which invalidates the style sheet cache.

        """
        if change['type'] == 'update':
            from enaml.styling import StyleCache
            StyleCache._app_sheet_changed()

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    def start(self):
        """ Start the application's main event loop.

        """
        raise NotImplementedError

    def stop(self):
        """ Stop the application's main event loop.

        """
        raise NotImplementedError

    def deferred_call(self, callback, *args, **kwargs):
        """ Invoke a callable on the next cycle of the main event loop
        thread.

        Parameters
        ----------
        callback : callable
            The callable object to execute at some point in the future.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to
            the callback.

        """
        raise NotImplementedError

    def timed_call(self, ms, callback, *args, **kwargs):
        """ Invoke a callable on the main event loop thread at a
        specified time in the future.

        Parameters
        ----------
        ms : int
            The time to delay, in milliseconds, before executing the
            callable.

        callback : callable
            The callable object to execute at some point in the future.

        *args, **kwargs
            Any additional positional and keyword arguments to pass to
            the callback.

        """
        raise NotImplementedError

    def is_main_thread(self):
        """ Indicates whether the caller is on the main gui thread.

        Returns
        -------
        result : bool
            True if called from the main gui thread. False otherwise.

        """
        raise NotImplementedError

    def create_mime_data(self):
        """ Create a new mime data object to be filled by the user.

        Returns
        -------
        result : MimeData
            A concrete implementation of the MimeData class.

        """
        raise NotImplementedError

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def resolve_proxy_class(self, declaration_class):
        """ Resolve the proxy implementation class for a declaration.

        This can be reimplemented by Application subclasses if more
        control is needed.

        Parameters
        ----------
        declaration_class : type
            A ToolkitObject subclass for which the proxy implementation
            class should be resolved.

        Returns
        -------
        result : type
            A ProxyToolkitObject subclass for the given class, or None
            if one could not be resolved.

        """
        resolver = self.resolver
        for base in declaration_class.mro():
            name = base.__name__
            cls = resolver.resolve(name)
            if cls is not None:
                return cls

    def create_proxy(self, declaration):
        """ Create the proxy object for the given declaration.

        This can be reimplemented by Application subclasses if more
        control is needed.

        Parameters
        ----------
        declaration : ToolkitObject
            The object for which a toolkit proxy should be created.

        Returns
        -------
        result : ProxyToolkitObject or None
            An appropriate toolkit proxy object, or None if one cannot
            be create for the given declaration object.

        """
        cls = self.resolve_proxy_class(type(declaration))
        if cls is not None:
            return cls(declaration=declaration)
        msg = "could not resolve a toolkit implementation for the '%s' "
        msg += "component when running under a '%s'"
        d_name = type(declaration).__name__
        a_name = type(self).__name__
        raise TypeError(msg % (d_name, a_name))

    def schedule(self, callback, args=None, kwargs=None, priority=0):
        """ Schedule a callable to be executed on the event loop thread.

        This call is thread-safe.

        Parameters
        ----------
        callback : callable
            The callable object to be executed.

        args : tuple, optional
            The positional arguments to pass to the callable.

        kwargs : dict, optional
            The keyword arguments to pass to the callable.

        priority : int, optional
            The queue priority for the callable. Smaller values indicate
            lower priority, larger values indicate higher priority. The
            default priority is zero.

        Returns
        -------
        result : ScheduledTask
            A task object which can be used to unschedule the task or
            retrieve the results of the callback after the task has
            been executed.

        """
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        task = ScheduledTask(callback, args, kwargs)
        heap = self._task_heap
        with self._heap_lock:
            needs_start = len(heap) == 0
            item = (-priority, next(self._counter), task)
            heappush(heap, item)
        if needs_start:
            if self.is_main_thread():
                self._next_task()
            else:
                self.deferred_call(self._next_task)
        return task

    def has_pending_tasks(self):
        """ Get whether or not the application has pending tasks.

        Returns
        -------
        result : bool
            True if there are pending tasks. False otherwise.

        """
        heap = self._task_heap
        with self._heap_lock:
            has_pending = len(heap) > 0
        return has_pending

    def destroy(self):
        """ Destroy this application instance.

        Once an application is created, it must be destroyed before a
        new application can be instantiated.

        """
        self.stop()
        Application._instance = None


#------------------------------------------------------------------------------
# Helper Functions
#------------------------------------------------------------------------------
def deferred_call(callback, *args, **kwargs):
    """ Invoke a callable on the next cycle of the main event loop
    thread.

    This is a convenience function for invoking the same method on the
    current application instance. If an application instance does not
    exist, a RuntimeError will be raised.

    Parameters
    ----------
    callback : callable
        The callable object to execute at some point in the future.

    *args, **kwargs
        Any additional positional and keyword arguments to pass to
        the callback.

    """
    app = Application.instance()
    if app is None:
        raise RuntimeError('Application instance does not exist')
    app.deferred_call(callback, *args, **kwargs)


def timed_call(ms, callback, *args, **kwargs):
    """ Invoke a callable on the main event loop thread at a specified
    time in the future.

    This is a convenience function for invoking the same method on the
    current application instance. If an application instance does not
    exist, a RuntimeError will be raised.

    Parameters
    ----------
    ms : int
        The time to delay, in milliseconds, before executing the
        callable.

    callback : callable
        The callable object to execute at some point in the future.

    *args, **kwargs
        Any additional positional and keyword arguments to pass to
        the callback.

    """
    app = Application.instance()
    if app is None:
        raise RuntimeError('Application instance does not exist')
    app.timed_call(ms, callback, *args, **kwargs)


def is_main_thread():
    """ Indicates whether the caller is on the main gui thread.

    This is a convenience function for invoking the same method on the
    current application instance. If an application instance does not
    exist, a RuntimeError will be raised.

    Returns
    -------
    result : bool
        True if called from the main gui thread. False otherwise.

    """
    app = Application.instance()
    if app is None:
        raise RuntimeError('Application instance does not exist')
    return app.is_main_thread()


def schedule(callback, args=None, kwargs=None, priority=0):
    """ Schedule a callable to be executed on the event loop thread.

    This call is thread-safe.

    This is a convenience function for invoking the same method on the
    current application instance. If an application instance does not
    exist, a RuntimeError will be raised.

    Parameters
    ----------
    callback : callable
        The callable object to be executed.

    args : tuple, optional
        The positional arguments to pass to the callable.

    kwargs : dict, optional
        The keyword arguments to pass to the callable.

    priority : int, optional
        The queue priority for the callable. Smaller values indicate
        lower priority, larger values indicate higher priority. The
        default priority is zero.

    Returns
    -------
    result : ScheduledTask
        A task object which can be used to unschedule the task or
        retrieve the results of the callback after the task has
        been executed.

    """
    app = Application.instance()
    if app is None:
        raise RuntimeError('Application instance does not exist')
    return app.schedule(callback, args, kwargs, priority)
