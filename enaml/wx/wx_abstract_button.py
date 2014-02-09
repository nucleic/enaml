#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int

from enaml.widgets.abstract_button import ProxyAbstractButton

from .wx_control import WxControl


# cyclic notification guard flags
CHECKED_GUARD = 0x1


class WxAbstractButton(WxControl, ProxyAbstractButton):
    """ A Wx implementation of an Enaml ProxyAbstractButton.

    This class can serve as a base class for widgets that implement
    button behavior such as CheckBox, RadioButton and PushButtons.
    It is not meant to be used directly.

    """
    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Implement in a subclass to create the widget.

        """
        raise NotImplementedError

    def init_widget(self):
        """ Initialize the button widget.

        """
        super(WxAbstractButton, self).init_widget()
        d = self.declaration
        if d.text:
            self.set_text(d.text, guard=False)
        self.set_checkable(d.checkable)
        self.set_checked(d.checked)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_clicked(self, event):
        """ The event handler for the clicked event.

        Parameters
        ----------
        event : wxEvent
            The wx event object. This is ignored by the handler.

        """
        if not self._guard & CHECKED_GUARD:
            checked = self.get_checked()
            self.declaration.checked = checked
            self.declaration.clicked(checked)

    def on_toggled(self, event):
        """ The event handler for the toggled event.

        Parameters
        ----------
        event : wxEvent
            The wx event object. This is ignored by the handler.

        """
        if not self._guard & CHECKED_GUARD:
            checked = self.get_checked()
            self.declaration.checked = checked
            self.declaration.toggled(checked)

    #--------------------------------------------------------------------------
    # ProxyAbstractButton API
    #--------------------------------------------------------------------------
    def set_text(self, text, guard=True):
        """ Sets the widget's text with the provided value.

        """
        if guard:
            with self.geometry_guard():
                self.widget.SetLabel(text)
        else:
            self.widget.SetLabel(text)

    def set_icon(self, icon):
        """ Sets the widget's icon to the provided image

        This is not supported on wx.

        """
        pass

    def set_icon_size(self, icon_size):
        """ Sets the widget's icon size to the provided tuple

        This is not supported on wx.

        """
        pass

    def set_checkable(self, checkable):
        """ Sets whether or not the widget is checkable.

        """
        raise NotImplementedError

    def get_checked(self):
        """ Returns the checked state of the widget.

        """
        raise NotImplementedError

    def set_checked(self, checked):
        """ Sets the widget's checked state with the provided value.

        """
        raise NotImplementedError
