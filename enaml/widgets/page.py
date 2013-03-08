#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Unicode, Bool, Str, Event, observe

from enaml.core.declarative import d_

from .container import Container
from .widget import Widget


class Page(Widget):
    """ A widget which can be used as a page in a Notebook control.

    A Page is a widget which can be used as a child of a Notebook
    control. It can have at most a single child widget which is an
    instance of Container.

    """
    #: The title to use for the page in the notebook.
    title = d_(Unicode())

    #: The source url for the icon to use for the page.
    icon_source = d_(Str())

    #: Whether or not this individual page is closable. Note that the
    #: 'tabs_closable' flag on the parent Notebook must be set to True
    #: for this to have any effect.
    closable = d_(Bool(True))

    #: An event fired when the user closes the page by clicking on
    #: the tab's close button. This event is fired by the parent
    #: Notebook when the tab is closed. This event has no payload.
    closed = Event()

    @property
    def page_widget(self):
        """ A read only property which returns the page widget.

        """
        widget = None
        for child in self.children:
            if isinstance(child, Container):
                widget = child
        return widget

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the snapshot for the control.

        """
        snap = super(Page, self).snapshot()
        snap['title'] = self.title
        snap['closable'] = self.closable
        snap['icon_source'] = self.icon_source
        return snap

    @observe(r'^(title|closable|icon_source)$', regex=True)
    def send_member_change(self, change):
        """ Send the member state change to the client.

        """
        # The superclass implementation is suffient
        super(Page, self).send_member_change(change)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_closed(self, content):
        """ Handle the 'closed' action from the client widget.

        """
        self.set_guarded(visible=False)
        self.closed()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def open(self):
        """ Open the page in the Notebook.

        Calling this method will also set the page visibility to True.

        """
        self.set_guarded(visible=True)
        self.send_action('open', {})

    def close(self):
        """ Close the page in the Notebook.

        Calling this method will set the page visibility to False.

        """
        self.set_guarded(visible=False)
        self.send_action('close', {})

