#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Logging Setup
#------------------------------------------------------------------------------
# Add a NullHandler so enaml loggers don't complain when they get used.
import logging

class NullHandler(logging.Handler):

    def handle(self, record):
        pass

    def emit(self, record):
        pass

    def createLock(self):
        self.lock = None

logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

del logging, logger, NullHandler


#------------------------------------------------------------------------------
# Import Helper
#------------------------------------------------------------------------------
def imports():
    """ Lazily imports and returns an enaml imports context.

    """
    from enaml.core.import_hooks import imports
    return imports()


#------------------------------------------------------------------------------
# Operator Context Functions
#------------------------------------------------------------------------------
#: The private storage for the optional default operator context function
#: which overrides that which is provided by default.
_default_operator_context_func = None


def set_default_operator_context_func(func):
    """ Set the default operator context func to the given callable.

    Parameters
    ----------
    func : callable
        A callable object which takes no arguments and returns an
        instance of OperatorContext.

    """
    global _default_operator_context_func
    _default_operator_context_func = func


def reset_default_operator_context_func():
    """ Reset the default operator context func such that the default
    context is returned to the framework default.

    """
    global _default_operator_context_func
    _default_operator_context_func = None


def default_operator_context():
    """ Creates an returns the default operator context. The default
    context is either that which is provided by the framework unless
    overridden by the user by providing a default context func via
    'set_default_operator_context_func'

    """
    ctxt_func = _default_operator_context_func
    if ctxt_func is not None:
        return ctxt_func()
    from enaml.core.operator_context import OperatorContext
    from enaml.core.operators import OPERATORS
    return OperatorContext(OPERATORS)


#------------------------------------------------------------------------------
# Test Helpers
#------------------------------------------------------------------------------
def test_collector():
    """ Discover and collect tests for the Enaml Package.

        .. note :: addapted from the unittest2
    """
    import os
    import sys
    from unittest import TestLoader

    # import __main__ triggers code re-execution
    __main__ = sys.modules['__main__']
    setupDir = os.path.abspath(os.path.dirname(__main__.__file__))

    return TestLoader().discover(setupDir)

