#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Int, Bool, Range, Unicode, Typed, ForwardTyped, observe, set_default
)

from enaml.core.declarative import d_

from .control import Control, ProxyControl


class ProxySpinBox(ProxyControl):
    """ The abstract definition of a proxy SpinBox object.

    """
    #: A reference to the SpinBox declaration.
    declaration = ForwardTyped(lambda: SpinBox)

    def set_minimum(self, minimum):
        raise NotImplementedError

    def set_maximum(self, maximum):
        raise NotImplementedError

    def set_value(self, value):
        raise NotImplementedError

    def set_prefix(self, prefix):
        raise NotImplementedError

    def set_suffix(self, suffix):
        raise NotImplementedError

    def set_special_value_text(self, text):
        raise NotImplementedError

    def set_single_step(self, step):
        raise NotImplementedError

    def set_read_only(self, read_only):
        raise NotImplementedError

    def set_wrapping(self, wrapping):
        raise NotImplementedError


class SpinBox(Control):
    """ A spin box widget which manipulates integer values.

    """
    #: The minimum value for the spin box. Defaults to 0.
    minimum = d_(Int(0))

    #: The maximum value for the spin box. Defaults to 100.
    maximum = d_(Int(100))

    #: The position value of the spin box. The value will be clipped to
    #: always fall between the minimum and maximum.
    value = d_(Int(0))

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

    #: A reference to the ProxySpinBox object.
    proxy = Typed(ProxySpinBox)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('minimum', 'maximum', 'value', 'prefix', 'suffix',
        'special_value_text', 'single_step', 'read_only', 'wrapping')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(SpinBox, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # PostSetAttr Handlers
    #--------------------------------------------------------------------------
    def _post_setattr_minimum(self, old, new):
        """ Post setattr the minimum value for the spin box.

        If the new minimum is greater than the current value or maximum,
        those values are adjusted up.

        """
        if new > self.maximum:
            self.maximum = new
        if new > self.value:
            self.value = new

    def _post_setattr_maximum(self, old, new):
        """ Post setattr the maximum value for the spin box.

        If the new maximum is less than the current value or the minimum,
        those values are adjusted down.

        """
        if new < self.minimum:
            self.minimum = new
        if new < self.value:
            self.value = new

    #--------------------------------------------------------------------------
    # Post Validation Handlers
    #--------------------------------------------------------------------------
    def _post_validate_value(self, old, new):
        """ Post validate the value for the spin box.

        The value is clipped to minimum and maximum bounds.

        """
        return max(self.minimum, min(new, self.maximum))
