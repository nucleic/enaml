#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.workbench.api import ExtensionObject


class ApplicationFactory(ExtensionObject):
    """ An ExtensionObject for creating studio Application instances.

    Plugins which contribute to the 'enaml.studio.ui.application'
    extension point should subclass this factory to create custom
    Application objects.

    """
    def __call__(self):
        """ Create the Application instance for the application.

        The default implementation of this method returns an instance
        of 'enaml.qt.qt_application.QtApplication'

        Returns
        -------
        result : Application
            The Application instance to use for the studio application.

        """
        from enaml.qt.qt_application import QtApplication
        return QtApplication()
