#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .widget import Widget


class MdiWindow(Widget):
    """ A widget which can be used as a window in an MdiArea.

    An MdiWindow is a widget which can be used as an independent window
    in an MdiArea. It can have at most a single child widget which is
    an instance of Widget.

    """
    @property
    def mdi_widget(self):
        """ A read-only property which returns the window's widget.

        """
        widget = None
        for child in self.children:
            if isinstance(child, Widget):
                widget = child
        return widget

