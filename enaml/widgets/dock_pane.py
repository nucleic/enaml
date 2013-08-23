#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    List, Enum, Unicode, Bool, Event, Typed, ForwardTyped, observe
)

from enaml.core.declarative import d_

from .container import Container
from .widget import Widget, ProxyWidget


class ProxyDockPane(ProxyWidget):
    """ The abstract definition of a proxy DockPane object.

    """
    #: A reference to the DockPane declaration.
    declaration = ForwardTyped(lambda: DockPane)

    def set_title(self, title):
        raise NotImplementedError

    def set_title_bar_visible(self, visible):
        raise NotImplementedError

    def set_title_bar_orientation(self, orientation):
        raise NotImplementedError

    def set_closable(self, closable):
        raise NotImplementedError

    def set_movable(self, movable):
        raise NotImplementedError

    def set_floatable(self, floatable):
        raise NotImplementedError

    def set_floating(self, floating):
        raise NotImplementedError

    def set_dock_area(self, area):
        raise NotImplementedError

    def set_allowed_dock_areas(self, areas):
        raise NotImplementedError


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
    closed = d_(Event(), writable=False)

    #: A reference to the ProxyDockPane object.
    proxy = Typed(ProxyDockPane)

    def dock_widget(self):
        """ Get the dock widget defined for the dock pane.

        The last child Container is considered the dock widget.

        """
        for child in reversed(self.children):
            if isinstance(child, Container):
                return child

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('title', 'title_bar_visible', 'title_bar_orientation', 'closable',
        'movable', 'floatable', 'floating', 'dock_area', 'allowed_dock_areas')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(DockPane, self)._update_proxy(change)

    # TODO spend some time thinking about the open/close api
    # I would rather everything be consistent, which likely
    # means destroy-on-close behavior should be the norm.
    def open(self):
        #msg = "The 'open()' method will be removed in Enaml version "
        #msg += "0.8.0. Use 'show()' instead."
        #import warnings
        #warnings.warn(msg, FutureWarning, stacklevel=2)
        self.show()

    def close(self):
        #msg = "The 'close()' method will be removed in Enaml version "
        #msg += "0.8.0. Use 'hide()' instead."
        #import warnings
        #warnings.warn(msg, FutureWarning, stacklevel=2)
        self.hide()
