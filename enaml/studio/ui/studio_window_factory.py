#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .window_factory import WindowFactory


class StudioWindowFactory(WindowFactory):
    """ A WindowFactory for creating default StudioWindow instances.

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
        import enaml
        with enaml.imports():
            from enaml.studio.ui.studio_window import StudioWindow
        return StudioWindow(parent, **kwargs)
