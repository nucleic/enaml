#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Enum, List, observe

from enaml.core.declarative import d_

from .action import Action
from .action_group import ActionGroup
from .constraints_widget import ConstraintsWidget


class ToolBar(ConstraintsWidget):
    """ A widget which displays a row of tool buttons.

    A ToolBar is typically used as a child of a MainWindow where it can
    be dragged and docked in various locations in the same fashion as a
    DockPane. However, a ToolBar can also be used as the child of a
    Container and layed out with constraints, though in this case it will
    lose its ability to be docked.

    """
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
        Enum('top', 'right', 'left', 'bottom', 'all'), value=['all'],
    ))

    #: The orientation of the toolbar. This only has meaning when the
    #: toolbar is not a child of a MainWindow and is used as part of
    #: a constraints based layout.
    orientation = d_(Enum('horizontal', 'vertical'))

    #: A flag indicating whether the user has explicitly set the hug
    #: property. If it is not explicitly set, the hug values will be
    #: updated automatically when the orientation changes.
    _explicit_hug = Bool(False)

    @property
    def items(self):
        """ A read only property which returns the list of toolbar items.

        """
        isinst = isinstance
        types = (Action, ActionGroup)
        return [child for child in self.children if isinst(child, types)]

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dict for the DockPane.

        """
        snap = super(ToolBar, self).snapshot()
        snap['movable'] = self.movable
        snap['floatable'] = self.floatable
        snap['floating'] = self.floating
        snap['dock_area'] = self.dock_area
        snap['allowed_dock_areas'] = self.allowed_dock_areas
        snap['orientation'] = self.orientation
        return snap

    @observe(r'^(movable|floatable|floating|dock_area|allowed_dock_areas|'
             r'orientation)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(ToolBar, self).send_member_change(change)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
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
    # Observers
    #--------------------------------------------------------------------------
    def _observe_orientation(self, change):
        """ Updates the hug properties if they are not explicitly set.

        """
        if not self._explicit_hug:
            self.hug_width = self._default_hug_width()
            self.hug_height = self._default_hug_height()
            # Reset to False to remove the effect of the above.
            self._explicit_hug = False

    #--------------------------------------------------------------------------
    # Default Handlers
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
    # Post Validation Handlers
    #--------------------------------------------------------------------------
    def _post_validate_hug_width(self, old, new):
        """ Post validate the hug width for the slider.

        This sets the explicit hug flag to True.

        """
        self._explicit_hug = True
        return new

    def _post_validate_hug_height(self, old, new):
        """ Post validate the hug height for the slider.

        This sets the explicit hug flag to True.

        """
        self._explicit_hug = True
        return new

