#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Enum, Range, ForwardTyped, Typed, observe

from enaml.core.declarative import d_

from .constraints_widget import ConstraintsWidget, ProxyConstraintsWidget


class Border(Atom):
    """ A class for defining a border on a Frame.

    Border instances should be treated as read-only once created.

    """
    #: The style of the border.
    style = Enum('box', 'panel', 'styled_panel')

    #: The shadow style applied to the border.
    line_style = Enum('plain', 'sunken', 'raised')

    #: The thickness of the outer border line.
    line_width = Range(low=0, value=1)

    #: The thickness of the inner border line. This only has an effect
    #: for the 'sunken' and 'raised' line styles.
    midline_width = Range(low=0, value=0)


class ProxyFrame(ProxyConstraintsWidget):
    """ The abstract definition of a proxy Frame object.

    """
    #: A reference to the Frame declaration.
    declaration = ForwardTyped(lambda: Frame)

    def set_border(self, border):
        raise NotImplementedError


class Frame(ConstraintsWidget):
    """ A ConstraintsWidget that draws an optional border.

    This class serves as a base class for widgets such as Container and
    ScrollArea. It should not normally be used directly by user code.

    """
    #: The border to apply to the frame. This may not be supported by
    #: all toolkit backends.
    border = d_(Typed(Border))

    #: A reference to the ProxyContainer object.
    proxy = Typed(ProxyFrame)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('border')
    def _update_proxy(self, change):
        """ An observer which updates the proxy when the border changes.

        """
        # The superclass handler is sufficient
        super(Frame, self)._update_proxy(change)
