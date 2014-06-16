#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Unicode, Enum, Typed, ForwardTyped, observe

from enaml.core.declarative import d_

from .container import Container, ProxyContainer


class ProxyGroupBox(ProxyContainer):
    """ The abstract definition of a proxy GroupBox object.

    """
    #: A reference to the GroupBox declaration.
    declaration = ForwardTyped(lambda: GroupBox)

    def set_title(self, title):
        raise NotImplementedError

    def set_flat(self, flat):
        raise NotImplementedError

    def set_title_align(self, align):
        raise NotImplementedError


class GroupBox(Container):
    """ The GroupBox container, which introduces a group of widgets with
    a title and usually has a border.

    """
    #: The title displayed at the top of the box.
    title = d_(Unicode())

    #: The flat parameter determines if the GroupBox is displayed with
    #: just the title and a header line (True) or with a full border
    #: (False, the default).
    flat = d_(Bool(False))

    #: The alignment of the title text.
    title_align = d_(Enum('left', 'right', 'center'))

    #: A reference to the ProxyGroupBox object.
    proxy = Typed(ProxyGroupBox)

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('title', 'flat', 'title_align')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(GroupBox, self)._update_proxy(change)
