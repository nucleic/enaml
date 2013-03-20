#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from .wx_control import WxControl

from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.backends.backend_wx import NavigationToolbar2Wx


class WxMPLCanvas(WxControl):
    """ A Wx implementation of an Enaml MPLCanvas.

    """
    #: Internal storage for the matplotlib figure.
    _figure = None

    #: Internal storage for whether or not to show the toolbar.
    _toolbar_visible = False

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying widget.

        """
        widget = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        widget.SetSizer(sizer)
        return widget

    def create(self, tree):
        """ Create and initialize the underlying widget.

        """
        super(WxMPLCanvas, self).create(tree)
        self._figure = tree['figure']
        self._toolbar_visible = tree['toolbar_visible']

    def init_layout(self):
        """ Initialize the layout of the underlying widget.

        """
        super(WxMPLCanvas, self).init_layout()
        self.refresh_mpl_widget(notify=False)

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_figure(self, content):
        """ Handle the 'set_figure' action from the Enaml widget.

        """
        self._figure = content['figure']
        self.refresh_mpl_widget()

    def on_action_set_toolbar_visible(self, content):
        """ Handle the 'set_toolbar_visible' action from the Enaml
        widget.

        """
        visible = content['toolbar_visible']
        self._toolbar_visible = visible
        widget = self.widget()
        sizer = widget.GetSizer()
        children = sizer.GetChildren()
        if len(children) == 2:
            widget.Freeze()
            old_hint = widget.GetBestSize()
            toolbar = children[0]
            toolbar.Show(visible)
            new_hint = widget.GetBestSize()
            if old_hint != new_hint:
                self.size_hint_updated()
            sizer.Layout()
            widget.Thaw()

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def refresh_mpl_widget(self, notify=True):
        """ Create the mpl widget and update the underlying control.

        Parameters
        ----------
        notify : bool, optional
            Whether to notify the layout system if the size hint of the
            widget has changed. The default is True.

        """
        # Delete the old widgets in the layout, it's just shenanigans
        # to try to reuse the old widgets when the figure changes.
        widget = self.widget()
        widget.Freeze()
        if notify:
            old_hint = widget.GetBestSize()
        sizer = widget.GetSizer()
        sizer.Clear(True)

        # Create the new figure and toolbar widgets. It seems that key
        # events will not be processed without an mpl figure manager.
        # However, a figure manager will create a new toplevel window,
        # which is certainly not desired in this case. This appears to
        # be a limitation of matplotlib.
        figure = self._figure
        if figure is not None:
            canvas = FigureCanvasWxAgg(widget, -1, figure)
            toolbar = NavigationToolbar2Wx(canvas)
            toolbar.Show(self._toolbar_visible)
            sizer.Add(toolbar, 0, wx.EXPAND)
            sizer.Add(canvas, 1, wx.EXPAND)

        if notify:
            new_hint = widget.GetBestSize()
            if old_hint != new_hint:
                self.size_hint_updated()

        sizer.Layout()
        widget.Thaw()
