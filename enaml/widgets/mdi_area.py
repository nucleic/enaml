#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import set_default

from .constraints_widget import ConstraintsWidget
from .mdi_window import MdiWindow


class MdiArea(ConstraintsWidget):
    """ A widget which acts as a virtual window manager for other
    top level widget.

    An MdiArea can be used to provide an area within an application
    that can display other widgets in their own independent windows.
    Children of an MdiArea should be defined as instances of MdiWindow.

    """
    #: An MdiArea expands freely in width and height by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: An MdiArea resists clipping only weakly by default.
    resist_width = set_default('weak')
    resist_height = set_default('weak')

    @property
    def mdi_windows(self):
        """ Return a list of the MdiWindow children.

        """
        isinst = isinstance
        target = MdiWindow
        return [child for child in self.children if isinst(child, target)]

