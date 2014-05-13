#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Enum, List, Typed, ForwardTyped, observe

from enaml.core.declarative import d_

from .action import Action
from .action_group import ActionGroup
from .constraints_widget import ConstraintsWidget, ProxyConstraintsWidget


class ProxyToolBar(ProxyConstraintsWidget):
    """ The abstract definition of a proxy ToolBar object.

    """
    #: A reference to the ToolBar declaration.
    declaration = ForwardTyped(lambda: ToolBar)

    def set_button_style(self, style):
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

    def set_orientation(self, orientation):
        raise NotImplementedError


class ToolBar(ConstraintsWidget):
    """ A widget which displays a row of tool buttons.

    A ToolBar is typically used as a child of a MainWindow where it can
    be dragged and docked in various locations in the same fashion as a
    DockPane. However, a ToolBar can also be used as the child of a
    Container and layed out with constraints, though in this case it will
    lose its ability to be docked.

    """
    #: The button style to apply to actions added to the tool bar.
    button_style = d_(Enum(
        'icon_only', 'text_only', 'text_beside_icon', 'text_under_icon'
    ))

    #: Whether or not the tool bar is movable by the user. This value
    #: only has meaning if the tool bar is the child of a MainWindow.
    movable = d_(Bool(True))

    #: Whether or not the tool bar can be floated as a separate window.
    #: This value only has meaning if the tool bar is the child of a
    #: MainWindow.
    floatable = d_(Bool(True))

    #: A boolean indicating whether or not the tool bar is floating.
    #: This value only has meaning if the tool bar is the child of a
    #: MainWindow.
    floating = d_(Bool(False))

    #: The dock area in the MainWindow where the tool bar is docked.
    #: This value only has meaning if the tool bar is the child of a
    #: MainWindow.
    dock_area = d_(Enum('top', 'right', 'left', 'bottom'))

    #: The areas in the MainWindow where the tool bar can be docked
    #: by the user. This value only has meaning if the tool bar is the
    #: child of a MainWindow.
    allowed_dock_areas = d_(List(
        Enum('top', 'right', 'left', 'bottom', 'all'), ['all'],
    ))

    #: The orientation of the toolbar. This only has meaning when the
    #: toolbar is not a child of a MainWindow and is used as part of
    #: a constraints based layout.
    orientation = d_(Enum('horizontal', 'vertical'))

    #: Whether or not to automatically adjust the 'hug_width' and
    #: 'hug_height' values based on the value of 'orientation'.
    auto_hug = d_(Bool(True))

    #: A reference to the ProxyToolBar object.
    proxy = Typed(ProxyToolBar)

    def items(self):
        """ Get the items defined on the tool bar.

        """
        allowed = (Action, ActionGroup)
        return [c for c in self.children if isinstance(c, allowed)]

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('button_style', 'movable', 'floatable', 'floating', 'dock_area',
        'allowed_dock_areas', 'orientation')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(ToolBar, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # DefaultValue Handlers
    #--------------------------------------------------------------------------
    def _default_hug_width(self):
        """ Get the default hug width for the slider.

        The default hug width is computed based on the orientation.

        """
        if self.orientation == 'horizontal':
            return 'ignore'
        return 'strong'

    def _default_hug_height(self):
        """ Get the default hug height for the slider.

        The default hug height is computed based on the orientation.

        """
        if self.orientation == 'vertical':
            return 'ignore'
        return 'strong'

    #--------------------------------------------------------------------------
    # PostSetAttr Handlers
    #--------------------------------------------------------------------------
    def _post_setattr_orientation(self, old, new):
        """ Post setattr the orientation for the tool bar.

        If auto hug is enabled, the hug values will be updated.

        """
        if self.auto_hug:
            if new == 'vertical':
                self.hug_width = 'strong'
                self.hug_height = 'ignore'
            else:
                self.hug_width = 'ignore'
                self.hug_height = 'strong'
