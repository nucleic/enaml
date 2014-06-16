#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Range, Enum, Typed, ForwardTyped, observe

from enaml.core.declarative import d_
from .control import Control, ProxyControl


class ProxySeparator(ProxyControl):
    """ The abstract definition of a proxy Separator object.

    """
    #: A reference to the Separator declaration.
    declaration = ForwardTyped(lambda: Separator)

    def set_orientation(self, resizable):
        raise NotImplementedError

    def set_line_style(self, style):
        raise NotImplementedError

    def set_line_width(self, width):
        raise NotImplementedError

    def set_midline_width(self, width):
        raise NotImplementedError


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

    #: Whether or not to automatically adjust the 'hug_width' and
    #: 'hug_height' values based on the value of 'orientation'.
    auto_hug = d_(Bool(True))

    #: A reference to the ProxySeparator object.
    proxy = Typed(ProxySeparator)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('orientation', 'line_style', 'line_width', 'midline_width')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(Separator, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # DefaultValue Handlers
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
