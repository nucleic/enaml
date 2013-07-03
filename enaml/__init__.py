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
def imports(operators=None, union=True):
    """ Lazily imports and returns an enaml imports context.

    Parameters
    ----------
    operators : dict, optional
        An optional dictionary of operators to push onto the operator
        stack for the duration of the import context. If this is not
        provided, the default Enaml operators will be used. Unless a
        custom model framework is being used (i.e. not Atom), custom
        operators will typically not be needed.

    union : bool, optional
        Whether to union the operators with the operators on the top
        of the operator stack. The default is True and is typically
        the correct choice to allow overriding a subset of the default
        Enaml operators.

    Returns
    -------
    result : context manager
        A context manager which will install the Enaml import hook
        (and optional operators) for the duration of the context.

    """
    from enaml.core.import_hooks import imports
    if operators is None:
        return imports()

    from contextlib import contextmanager
    from enaml.core.operators import operator_context

    @contextmanager
    def imports_context():
        with imports():
            with operator_context(operators, union):
                yield

    return imports_context()
