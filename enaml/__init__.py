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
