#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.workbench.extension_object import ExtensionObject


class Configuration(ExtensionObject):
    """ An interface for creating a studio workspace configuration.

    Plugins which extend 'enaml.studio.workspace.configurations' should
    subclass this class to create custom configuration objects.

    """
    def shutdown(self):
        pass

    def content(self):
        return None
