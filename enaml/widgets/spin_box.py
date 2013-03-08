#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int, Bool, Range, Unicode, observe, set_default

from enaml.core.declarative import d_

from .control import Control


class SpinBox(Control):
    """ A spin box widget which manipulates integer values.

    """
    #: The minimum value for the spin box. Defaults to 0.
    minimum = d_(Int(0))

    #: The maximum value for the spin box. Defaults to 100.
    maximum = d_(Int(100))

    #: The current integer value for the spin box, constrained to
    #: minimum <= value <= maximum.
    value = d_(Range('minimum', 'maximum'))

    #: An optional prefix to include in the displayed text.
    prefix = d_(Unicode())

    #: An optional suffix to include in the displayed text.
    suffix = d_(Unicode())

    #: Optional text to display when the spin box is at its minimum.
    #: This allows the developer to indicate to the user a special
    #: significance to the minimum value e.g. "Auto"
    special_value_text = d_(Unicode())

    #: The step size for the spin box. Defaults to 1.
    single_step = d_(Range(low=1))

    #: Whether or not the spin box is read-only. If True, the user
    #: will not be able to edit the values in the spin box, but they
    #: will still be able to copy the text to the clipboard.
    read_only = d_(Bool(False))

    #: Whether or not the spin box will wrap around at its extremes.
    #: Defaults to False.
    wrapping = d_(Bool(False))

    #: A spin box expands freely in width by default.
    hug_width = set_default('ignore')

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Return the dict of creation attributes for the control.

        """
        snap = super(SpinBox, self).snapshot()
        snap['maximum'] = self.maximum
        snap['minimum'] = self.minimum
        snap['value'] = self.value
        snap['prefix'] = self.prefix
        snap['suffix'] = self.suffix
        snap['special_value_text'] = self.special_value_text
        snap['single_step'] = self.single_step
        snap['read_only'] = self.read_only
        snap['wrapping'] = self.wrapping
        return snap

    @observe(r'^(minimum|maximum|value|prefix|suffix|special_value_text|'
             r'single_step|read_only|wrapping)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(SpinBox, self).send_member_change(change)

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_value_changed(self, content):
        """ Handle the 'value_changed' action from the client widget.

        """
        self.set_guarded(value=content['value'])

