#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.workbench.extension_object import ExtensionObject


class WindowFactory(ExtensionObject):
    """ An interface for creating studio window factories.

    Plugins which contribute to the 'enaml.studio.ui.window' extension
    point should subclass this factory to create custom StudioWindow
    objects.

    """
    def __call__(self, parent=None, **kwargs):
        """ Create the StudioWindow instance for the application.

        Parameters
        ----------
        parent : Widget, optional
            The parent of the of the window.

        **kwargs
            Additional metadata to apply to the window.

        Returns
        -------
        result : StudioWindow
            The window instance to use for the studio application.

        """
        raise NotImplementedError