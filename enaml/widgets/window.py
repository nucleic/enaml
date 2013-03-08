#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Unicode, Enum, Str, Bool, Event, Coerced, observe

from enaml.core.declarative import d_
from enaml.layout.geometry import Size

from .container import Container
from .widget import Widget


class Window(Widget):
    """ A top-level Window component.

    A Window component is represents of a top-level visible component
    with a frame decoration. It may have at most one child widget which
    is dubbed the 'central widget'. The central widget is an instance
    of Container and is expanded to fit the size of the window.

    A Window does not support features like MenuBars or DockPanes, for
    such functionality, use a MainWindow widget.

    """
    #: The titlebar text.
    title = d_(Unicode())

    #: The initial size of the window. A value of (-1, -1) indicates
    #: to let the client choose the initial size
    initial_size = d_(Coerced(Size, factory=lambda: Size(-1, -1)))

    #: An enum which indicates the modality of the window. The default
    #: value is 'non_modal'.
    modality = d_(Enum('non_modal', 'application_modal', 'window_modal'))

    #: If this value is set to True, the window will be destroyed on
    #: the completion of the `closed` event.
    destroy_on_close = d_(Bool(True))

    #: The source url for the titlebar icon.
    icon_source = d_(Str())

    #: An event fired when the window is closed.
    closed = Event()

    @property
    def central_widget(self):
        """ Get the central widget defined on the window.

        The last `Container` child of the window is the central widget.

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
        """ Return the snapshot for a Window.

        """
        snap = super(Window, self).snapshot()
        snap['title'] = self.title
        snap['initial_size'] = self.initial_size
        snap['modality'] = self.modality
        snap['icon_source'] = self.icon_source
        return snap

    @observe(r'^(title|modality|icon_source)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(Window, self).send_member_change(change)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_closed(self, content):
        """ Handle the 'closed' action from the client widget.

        """
        self.set_guarded(visible=False)
        self.closed()
        if self.destroy_on_close:
            self.destroy()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def close(self):
        """ Send the 'close' action to the client widget.

        """
        self.send_action('close', {})

    def maximize(self):
        """ Send the 'maximize' action to the client widget.

        """
        self.send_action('maximize', {})

    def minimize(self):
        """ Send the 'minimize' action to the client widget.

        """
        self.send_action('minimize', {})

    def restore(self):
        """ Send the 'restore' action to the client widget.

        """
        self.send_action('restore', {})

