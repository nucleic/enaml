#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, List, Typed


class Workbench(Atom):
    """ A base class for creating plugin-style applications.

    This class provides the functionality for managing the lifecycle of
    plugins. It does not provide any UI functionality. That behavior
    must be supplied by a subclass, such as WorkbenchUI.

    """
    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def __init__(self, plugins=None):
        pass

    def add_plugin(self, plugin):
        pass

    def remove_plugin(self, plugin):
        pass

    def get_plugin(self, plugin_id):
        pass

    def get_extensions(self, extension_point_id):
        pass

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
