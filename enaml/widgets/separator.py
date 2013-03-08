#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Range, Enum, observe

from enaml.core.declarative import d_
from .control import Control


class Separator(Control):
    """ A widget which draws a horizontal or vertical separator line.

    """
    #: The orientation of the separator line.
    orientation = d_(Enum('horizontal', 'vertical'))

    #: The line style for the separator.
    line_style = d_(Enum('sunken', 'raised', 'plain'))

    #: The thickness of the outer separator line.
    line_width = d_(Range(low=0, high=3, value=1))

    #: The thickness of the inner separator line. This only has an
    #: effect for the 'sunken' and 'raised' line styles.
    midline_width = d_(Range(low=0, high=3, value=0))

    #: A flag indicating whether the user has explicitly set the hug
    #: property. If it is not explicitly set, the hug values will be
    #: updated automatically when the orientation changes.
    _explicit_hug = Bool(False)

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dictionary for the Separator.

        """
        snap = super(Separator, self).snapshot()
        snap['orientation'] = self.orientation
        snap['line_style'] = self.line_style
        snap['line_width'] = self.line_width
        snap['midline_width'] = self.midline_width
        return snap

    @observe(r'^(orientation|line_style|line_width|midline_width)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(Separator, self).send_member_change(change)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    def _observe_orientation(self, change):
        """ Update the hug properties if they are not explicitly set.

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
        """ Get the default hug width for the separator.

        The default hug width is computed based on the orientation.

        """
        if self.orientation == 'horizontal':
            return 'ignore'
        return 'strong'

    def _default_hug_height(self):
        """ Get the default hug height for the separator.

        The default hug height is computed based on the orientation.

        """
        if self.orientation == 'vertical':
            return 'ignore'
        return 'strong'

    #--------------------------------------------------------------------------
    # Property Methods
    #--------------------------------------------------------------------------
    def _get_hug_width(self):
        """ The property getter for 'hug_width'.

        Returns a computed hug value unless overridden by the user.

        """
        res = self._hug_width
        if res is None:
            if self.orientation == 'horizontal':
                res = 'ignore'
            else:
                res = 'strong'
        return res

    def _get_hug_height(self):
        """ The proper getter for 'hug_height'.

        Returns a computed hug value unless overridden by the user.

        """
        res = self._hug_height
        if res is None:
            if self.orientation == 'vertical':
                res = 'ignore'
            else:
                res = 'strong'
        return res

    def _set_hug_width(self, value):
        """ The property setter for 'hug_width'.

        Overrides the computed value.

        """
        self._hug_width = value

    def _set_hug_height(self, value):
        """ The property setter for 'hug_height'.

        Overrides the computed value.

        """
        self._hug_height = value

