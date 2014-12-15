#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped, Enum, Range, observe

from enaml.core.declarative import d_

from .toolkit_object import ToolkitObject, ProxyToolkitObject
from .widget import Widget


class ProxyStatusItem(ProxyToolkitObject):
    """ The abstract definition of a proxy StatusItem object.

    """
    #: A reference to the StatusItem declaration
    declaration = ForwardTyped(lambda: StatusItem)

    def set_mode(self, mode):
        raise NotImplementedError

    def set_stretch(self, stretch):
        raise NotImplementedError


class StatusItem(ToolkitObject):
    """ An item which holds a widget to include in a status bar.

    """
    #: The mode of a status item. A 'normal' item can be obscured by
    #: temporary status messages; a 'permanent' item cannot.
    mode = d_(Enum('normal', 'permanent'))

    #: The stretch factor to apply to this item, relative to the other
    #: items in the status bar.
    stretch = d_(Range(low=0))

    #: A reference to the ProxyStatusItem object.
    proxy = Typed(ProxyStatusItem)

    def status_widget(self):
        """ Get the status widget for the item.

        The last Widget child is used as the status widget.

        """
        for child in reversed(self.children):
            if isinstance(child, Widget):
                return child

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('mode', 'stretch')
    def _update_proxy(self, change):
        """ Update the proxy when the status item data changes.

        """
        # The superclass implementation is sufficient.
        super(StatusItem, self)._update_proxy(change)
