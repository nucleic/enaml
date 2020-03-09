#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped, Str

from enaml.core.declarative import d_
from enaml.icon import Icon

from .widget import Widget, ProxyWidget


class ProxyMdiWindow(ProxyWidget):
    """ The abstract definition of a proxy MdiWindow.

    """
    #: A reference to the MdiWindow declaration.
    declaration = ForwardTyped(lambda: MdiWindow)

    def set_title(self, title):
        raise NotImplementedError

    def set_icon(self, icon):
        raise NotImplementedError


class MdiWindow(Widget):
    """ A widget which can be used as a window in an MdiArea.

    An MdiWindow is a widget which can be used as an independent window
    in an MdiArea. It can have at most a single child widget which is
    an instance of Widget.

    """
    #: The titlebar text.
    title = d_(Str())

    #: The title bar icon.
    icon = d_(Typed(Icon))

    def mdi_widget(self):
        """ Get the mdi widget defined for the window.

        The last Widget child is the mdi widget.

        """
        for child in reversed(self.children):
            if isinstance(child, Widget):
                return child
