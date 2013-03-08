#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
#from .dock_pane import DockPane
from .menu_bar import MenuBar
#from .tool_bar import ToolBar
from .window import Window


class MainWindow(Window):
    """ A top level main window widget.

    MainWindow widgets are top level widgets which provide additional
    functionality beyond frame decoration. A MainWindow may optionally
    contain a MenuBar, any number of ToolBars, a StatusBar, and any
    number of DockPanes. Like Window, a MainWindow can have at most one
    central Container widget, which will be expanded to fit into the
    available space.

    """
    @property
    def menu_bar(self):
        """ A read only property which returns the window's MenuBar.

        """
        menu = None
        for child in self.children:
            if isinstance(child, MenuBar):
                menu = child
        return menu

    #: A read only property which returns the window's ToolBars.
    #tool_bars = Property(depends_on='children')

    #: A read only property which returns the window's DockPanes.
    #dock_panes = Property(depends_on='children')

    #: A read only property which returns the window's StatusBar.
    # status_bar = Property(depends_on='children')

    #@cached_property
    # def _get_tool_bars(self):
    #     """ The getter for the 'tool_bars' property.

    #     Returns
    #     -------
    #     result : tuple
    #         The tuple of ToolBar instances defined as children of this
    #         MainWindow.

    #     """
    #     isinst = isinstance
    #     panes = (child for child in self.children if isinst(child, ToolBar))
    #     return tuple(panes)

    # #@cached_property
    # def _get_dock_panes(self):
    #     """ The getter for the 'dock_panes' property.

    #     Returns
    #     -------
    #     result : tuple
    #         The tuple of DockPane instances defined as children of this
    #         MainWindow.

    #     """
    #     isinst = isinstance
    #     panes = (child for child in self.children if isinst(child, DockPane))
    #     return tuple(panes)

