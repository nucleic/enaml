#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from abc import ABCMeta, abstractmethod
from heapq import heappush, heappop
from itertools import count
import logging
from threading import Lock


logger = logging.getLogger(__name__)


class ScheduledTask(object):
    """ An object representing a task in the scheduler.

    """
    #: A sentinel object indicating that the result of the task is
    #: undefined or that the task has not yet been executed.
    undefined = object()

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
        self._result = self.undefined
        self._valid = True
        self._pending = True
        self._notify = None

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
            self._notify = None
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


class Application(object):
    """ The application object which manages the top-level communication
    protocol for serving Enaml views.

    """
    __metaclass__ = ABCMeta

    #: Private storage for the singleton application instance.
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
        self = super(Application, cls).__new__(cls)
        Application._instance = self
        return self

    def __init__(self, factories):
        """ Initialize an Enaml Application.

        Parameters
        ----------
        factories : iterable
            An iterable of SessionFactory instances that will be used
            to create the sessions for the application.

        """
        self._all_factories = []
        self._named_factories = {}
        self._task_heap = []
        self._counter = count()
        self._heap_lock = Lock()
        self.add_factories(factories)

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

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
    @abstractmethod
    def start_session(self, name):
        """ Start a new session of the given name.

        This method will create a new session object for the requested
        session type and return the new session_id. If the session name
        is invalid, an exception will be raised.

        Parameters
        ----------
        name : str
            The name of the session to start.

        Returns
        -------
        result : str
            The unique identifier for the created session.

        """
        raise NotImplementedError

    @abstractmethod
    def end_session(self, session_id):
        """ End the session with the given session id.

        This method will close down the existing session. If the session
        id is not valid, an exception will be raised.

        Parameters
        ----------
        session_id : str
            The unique identifier for the session to close.

        """
        raise NotImplementedError

    @abstractmethod
    def session(self, session_id):
        """ Get the session for the given session id.

        Parameters
        ----------
        session_id : str
            The unique identifier for the session to retrieve.

        Returns
        -------
        result : Session or None
            The session object with the given id, or None if the id
            does not correspond to an active session.

        """
        raise NotImplementedError

    @abstractmethod
    def sessions(self):
        """ Get the currently active sessions for the application.

        Returns
        -------
        result : list
            The list of currently active sessions for the application.

        """
        raise NotImplementedError

    @abstractmethod
    def start(self):
        """ Start the application's main event loop.

        """
        raise NotImplementedError

    @abstractmethod
    def stop(self):
        """ Stop the application's main event loop.

        """
        raise NotImplementedError

    @abstractmethod
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

    @abstractmethod
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

    @abstractmethod
    def is_main_thread(self):
        """ Indicates whether the caller is on the main gui thread.

        Returns
        -------
        result : bool
            True if called from the main gui thread. False otherwise.

        """
        raise NotImplementedError

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
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
            item = (-priority, self._counter.next(), task)
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

    def add_factories(self, factories):
        """ Add session factories to the application.

        Parameters
        ----------
        factories : iterable
            An iterable of SessionFactory instances to add to the
            application.

        """
        all_factories = self._all_factories
        named_factories = self._named_factories
        for factory in factories:
            name = factory.name
            if name in named_factories:
                msg = 'Multiple session factories named `%s`; ' % name
                msg += 'replacing previous value.'
                logger.warn(msg)
                old_factory = named_factories.pop(name)
                all_factories.remove(old_factory)
            all_factories.append(factory)
            named_factories[name] = factory

    def discover(self):
        """ Get a dictionary of session information for the application.

        Returns
        -------
        result : list
            A list of dicts of information about the available sessions.

        """
        info = [
            {'name': fact.name, 'description': fact.description}
            for fact in self._all_factories
        ]
        return info

    def destroy(self):
        """ Destroy this application instance.

        Once an application is created, it must be destroyed before a
        new application can be instantiated.

        """
        for session in self.sessions():
            self.end_session(session.session_id)
        self._all_factories = []
        self._named_factories = {}
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

