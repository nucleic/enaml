#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Typed, ForwardTyped, observe

from enaml.colors import ColorMember
from enaml.core.declarative import d_

from .toolkit_dialog import ToolkitDialog, ProxyToolkitDialog


class ProxyColorDialog(ProxyToolkitDialog):
    """ The abstract defintion of a proxy ColorDialog object.

    """
    #: A reference to the ColorDialog declaration.
    declaration = ForwardTyped(lambda: ColorDialog)

    def set_current_color(self, color):
        raise NotImplementedError

    def set_show_alpha(self, show):
        raise NotImplementedError

    def set_show_buttons(self, show):
        raise NotImplementedError


class ColorDialog(ToolkitDialog):
    """ A toolkit dialog that allows the user to select a color.

    """
    #: The currently selected color of the dialog.
    current_color = d_(ColorMember('white'))

    #: Whether or not to show the alpha value control.
    show_alpha = d_(Bool(True))

    #: Whether or not to show the dialog ok/cancel buttons.
    show_buttons = d_(Bool(True))

    #: The color selected when the user clicks accepts the dialog.
    #: This value is output only.
    selected_color = ColorMember()

    #: A reference to the ProxyColorDialog object.
    proxy = Typed(ProxyColorDialog)

    @staticmethod
    def get_color(parent=None, **kwargs):
        """ A static method which launches a color dialog.

        Parameters
        ----------
        parent : ToolkitObject or None
            The parent toolkit object for this dialog.

        **kwargs
            Additional data to pass to the dialog constructor.

        Returns
        -------
        result : Color or None
            The selected color or None if no color was selected.

        """
        dialog = ColorDialog(parent, **kwargs)
        dialog.exec_()
        if dialog.result:
            return dialog.selected_color

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('current_color', 'show_alpha', 'show_buttons'))
    def _update_proxy(self, change):
        """ An observer which updates the proxy when the data changes.

        """
        # The superclass implementation is sufficient.
        super(ColorDialog, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def _prepare(self):
        """ A reimplemented preparation method.

        This method resets the selected color to None.

        """
        super(ColorDialog, self)._prepare()
        self.selected_color = None
