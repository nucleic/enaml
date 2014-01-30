#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .application_factory import ApplicationFactory


class QtApplicationFactory(ApplicationFactory):
    """ An ApplicationFactory for creating QtApplication instances.

    """
    def __call__(self):
        """ Create the QtApplication instance for the studio.

        Returns
        -------
        result : QtApplication
            The QtApplication instance to use for the studio.

        """
        from enaml.qt.qt_application import QtApplication
        return QtApplication()
