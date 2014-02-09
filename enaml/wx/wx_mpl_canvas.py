#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from enaml.widgets.mpl_canvas import ProxyMPLCanvas

from .wx_control import WxControl

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wx import NavigationToolbar2Wx


class WxMPLCanvas(WxControl, ProxyMPLCanvas):
    """ A Wx implementation of an Enaml MPLCanvas.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying widget.

        """
        widget = wx.Panel(self.parent_widget())
        sizer = wx.BoxSizer(wx.VERTICAL)
        widget.SetSizer(sizer)
        self.widget = widget

    def init_layout(self):
        """ Initialize the layout of the underlying widget.

        """
        super(WxMPLCanvas, self).init_layout()
        self._refresh_mpl_widget()

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def set_figure(self, figure):
        """ Set the MPL figure for the widget.

        """
        with self.geometry_guard():
            self._refresh_mpl_widget()

    def set_toolbar_visible(self, visible):
        """ Set the toolbar visibility for the widget.

        """
        widget = self.widget
        sizer = widget.GetSizer()
        children = sizer.GetChildren()
        if len(children) == 2:
            with self.geometry_guard():
                widget.Freeze()
                toolbar = children[0]
                toolbar.Show(visible)
                sizer.Layout()
                widget.Thaw()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _refresh_mpl_widget(self):
        """ Create the mpl widget and update the underlying control.

        """
        # Delete the old widgets in the layout, it's just shenanigans
        # to try to reuse the old widgets when the figure changes.
        widget = self.widget
        widget.Freeze()
        sizer = widget.GetSizer()
        sizer.Clear(True)

        # Create the new figure and toolbar widgets. It seems that key
        # events will not be processed without an mpl figure manager.
        # However, a figure manager will create a new toplevel window,
        # which is certainly not desired in this case. This appears to
        # be a limitation of matplotlib.
        figure = self.declaration.figure
        if figure:
            canvas = FigureCanvasWxAgg(widget, -1, figure)
            toolbar = NavigationToolbar2Wx(canvas)
            toolbar.Show(self.declaration.toolbar_visible)
            sizer.Add(toolbar, 0, wx.EXPAND)
            sizer.Add(canvas, 1, wx.EXPAND)

        sizer.Layout()
        widget.Thaw()
