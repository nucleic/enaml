#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .wx_control import WxControl


class WxAbstractButton(WxControl):
    """ A Wx implementation of the Enaml AbstractButton class.

    This class can serve as a base class for widgets that implement
    button behavior such as CheckBox, RadioButton and PushButtons.
    It is not meant to be used directly.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ This method must be implemented by subclasses to create
        the proper button widget.

        """
        raise NotImplementedError

    def create(self, tree):
        """ Create and initialize the abstract button widget.

        Subclasses should reimplement this method and bind appropriate
        event handlers to the 'on_clicked' and 'on_toggled' event
        handlers.

        """
        super(WxAbstractButton, self).create(tree)
        self.set_checkable(tree['checkable'])
        self.set_checked(tree['checked'])
        self.set_text(tree['text'])

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_checked(self, content):
        """ Handle the 'set_checked' action from the Enaml widget.

        """
        self.set_checked(content['checked'])

    def on_action_set_text(self, content):
        """ Handle the 'set_text' action from the Enaml widget.

        """
        self.set_text(content['text'])
        # Trigger a relayout since the size hint likely changed

    def on_action_set_icon_size(self, content):
        """ Handle the 'set_icon_size' action from the Enaml widget.

        """
        self.set_icon_size(content['icon_size'])

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
        content = {'checked': self.get_checked()}
        self.send_action('clicked', content)

    def on_toggled(self, event):
        """ The event handler for the toggled event.

        Parameters
        ----------
        event : wxEvent
            The wx event object. This is ignored by the handler.

        """
        content = {'checked': self.get_checked()}
        self.send_action('toggled', content)

    #--------------------------------------------------------------------------
    # Abstract API
    #--------------------------------------------------------------------------
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

    def set_text(self, text):
        """ Sets the widget's text with the provided value.

        """
        self.widget().SetLabel(text)

    def set_icon(self, icon):
        """ Sets the widget's icon to the provided image

        """
        pass

    def set_icon_size(self, icon_size):
        """ Sets the widget's icon size to the provided tuple

        """
        pass

