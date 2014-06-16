#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Typed, ForwardTyped, Unicode, Enum, Event, observe, set_default
)

from enaml.core.declarative import d_

from .control import Control, ProxyControl


class ProxyLabel(ProxyControl):
    """ The abstract definition of a proxy Label object.

    """
    #: A reference to the Label declaration.
    declaration = ForwardTyped(lambda: Label)

    def set_text(self, text):
        raise NotImplementedError

    def set_align(self, align):
        raise NotImplementedError

    def set_vertical_align(self, align):
        raise NotImplementedError


class Label(Control):
    """ A simple control for displaying read-only text.

    """
    #: The unicode text for the label.
    text = d_(Unicode())

    #: The horizontal alignment of the text in the widget area.
    align = d_(Enum('left', 'right', 'center', 'justify'))

    #: The vertical alignment of the text in the widget area.
    vertical_align = d_(Enum('center', 'top', 'bottom'))

    #: An event emitted when the user clicks a link in the label.
    #: The payload will be the link that was clicked.
    link_activated = d_(Event(), writable=False)

    #: Labels hug their width weakly by default.
    hug_width = set_default('weak')

    #: A reference to the ProxyLabel object.
    proxy = Typed(ProxyLabel)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('text', 'align', 'vertical_align')
    def _update_proxy(self, change):
        """ An observer which sends the state change to the proxy.

        """
        # The superclass implementation is sufficient.
        super(Label, self)._update_proxy(change)
