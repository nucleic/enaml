#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import List, Enum, Unicode, Bool, Event, observe

from enaml.core.declarative import d_

from .container import Container
from .widget import Widget


class DockPane(Widget):
    """ A widget which can be docked in a MainWindow.

    A DockPane is a widget which can be docked in designated dock areas
    in a MainWindow. It can have at most a single child widget which is
    an instance of Container.

    """
    #: The title to use in the title bar.
    title = d_(Unicode())

    #: Whether or not the title bar is visible.
    title_bar_visible = d_(Bool(True))

    #: The orientation of the title bar.
    title_bar_orientation = d_(Enum('horizontal', 'vertical'))

    #: Whether or not the dock pane is closable via a close button.
    closable = d_(Bool(True))

    #: Whether or not the dock pane is movable by the user.
    movable = d_(Bool(True))

    #: Whether or not the dock can be floated as a separate window.
    floatable = d_(Bool(True))

    #: A boolean indicating whether or not the dock pane is floating.
    floating = d_(Bool(False))

    #: The dock area in the MainWindow where the pane is docked.
    dock_area = d_(Enum('left', 'right', 'top', 'bottom'))

    #: The dock areas in the MainWindow where the pane can be docked
    #: by the user. Note that this does not preclude the pane from
    #: being docked programmatically via the 'dock_area' attribute.
    allowed_dock_areas = d_(List(
        Enum('left', 'right', 'top', 'bottom', 'all'), ['all'],
    ))

    #: An event fired when the user closes the pane by clicking on the
    #: dock pane's close button.
    closed = Event()

    @property
    def dock_widget(self):
        """ A read only property which returns the dock widget.

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
        """ Returns the snapshot dict for the DockPane.

        """
        snap = super(DockPane, self).snapshot()
        snap['title'] = self.title
        snap['title_bar_visible'] = self.title_bar_visible
        snap['title_bar_orientation'] = self.title_bar_orientation
        snap['closable'] = self.closable
        snap['movable'] = self.movable
        snap['floatable'] = self.floatable
        snap['floating'] = self.floating
        snap['dock_area'] = self.dock_area
        snap['allowed_dock_areas'] = self.allowed_dock_areas
        return snap

    @observe(r'^(title|title_bar_visible|title_bar_orientation|closable|'
             r'movable|floatable|floating|dock_area|allowed_dock_areas)$',
             regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(DockPane, self).send_member_change(change)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_closed(self, content):
        """ Handle the 'closed' action from the client widget.

        """
        self.set_guarded(visible=False)
        self.closed()

    def on_action_floated(self, content):
        """ Handle the 'floated' action from the client widget.

        """
        self.set_guarded(floating=True)

    def on_action_docked(self, content):
        """ Handle the 'docked' action from the client widget.

        """
        self.set_guarded(floating=False)
        self.set_guarded(dock_area=content['dock_area'])

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def open(self):
        """ Open the dock pane in the MainWindow.

        Calling this method will also set the pane visibility to True.

        """
        self.set_guarded(visible=True)
        self.send_action('open', {})

    def close(self):
        """ Close the dock pane in the MainWindow.

        Calling this method will set the pane visibility to False.

        """
        self.set_guarded(visible=False)
        self.send_action('close', {})

