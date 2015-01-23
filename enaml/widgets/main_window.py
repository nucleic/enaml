#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped

from .dock_pane import DockPane
from .menu_bar import MenuBar
from .status_bar import StatusBar
from .tool_bar import ToolBar
from .window import Window, ProxyWindow


class ProxyMainWindow(ProxyWindow):
    """ The abstract definition of a proxy MainWindow object.

    """
    #: A reference to the MainWindow declaration.
    declaration = ForwardTyped(lambda: MainWindow)


class MainWindow(Window):
    """ A top level main window widget.

    MainWindow widgets are top level widgets which provide additional
    functionality beyond frame decoration. A MainWindow may optionally
    contain a MenuBar, any number of ToolBars, a StatusBar, and any
    number of DockPanes. Like Window, a MainWindow can have at most one
    central Container widget, which will be expanded to fit into the
    available space.

    """
    #: A reference to the ProxyMainWindow object.
    proxy = Typed(ProxyMainWindow)

    def menu_bar(self):
        """ Get the menu bar defined as a child on the window.

        The last MenuBar declared as a child is used as the official
        menu bar of the window.

        """
        for child in reversed(self.children):
            if isinstance(child, MenuBar):
                return child

    def dock_panes(self):
        """ Get the dock panes defined as children on the window.

        """
        return [c for c in self.children if isinstance(c, DockPane)]

    def status_bar(self):
        """ Get the status bar defined as a child on the window.

        The last StatusBar declared as a child is used as the official
        status bar of the window.

        """
        for child in reversed(self.children):
            if isinstance(child, StatusBar):
                return child

    def tool_bars(self):
        """ Get the tool bars defined as children on the window.

        """
        return [c for c in self.children if isinstance(c, ToolBar)]
