#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from atom.api import Typed

from enaml.widgets.split_item import ProxySplitItem

from .wx_single_widget_sizer import wxSingleWidgetSizer
from .wx_container import WxContainer
from .wx_widget import WxWidget


class wxSplitItem(wx.Panel):
    """ A wxPanel subclass which acts as an item in a wxSplitter.

    """
    def __init__(self, parent):
        """ Initialize a wxSplitItem.

        Parameters
        ----------
        parent : wx.Window
            The parent widget of the split item.

        """
        super(wxSplitItem, self).__init__(parent)
        self._split_widget = None
        self._stretch = 0
        self.SetSizer(wxSingleWidgetSizer())

    def GetSplitWidget(self):
        """ Get the split widget for this split item.

        Returns
        -------
        result : wxWindow or None
            The split widget being managed by this item.

        """
        return self._split_widget

    def SetSplitWidget(self, widget):
        """ Set the split widget for this split item.

        Parameters
        ----------
        widget : wxWindow
            The wxWindow to use as the split widget in this item.

        """
        self._split_widget = widget
        self.GetSizer().Add(widget)

    def GetStretch(self):
        """ Get the stretch factor for the widget.

        Returns
        -------
        result : int
            The stretch factor for the widget.

        """
        return self._stretch

    def SetStretch(self, stretch):
        """ Set the stretch factor for the widget.

        Parameters
        ----------
        stretch : int
            The stretch factor for the widget.

        """
        self._stretch = stretch


class WxSplitItem(WxWidget, ProxySplitItem):
    """ A Wx implementation of an Enaml ProxySplitItem.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(wxSplitItem)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QStackItem widget.

        """
        self.widget = wxSplitItem(self.parent_widget())

    def init_widget(self):
        """ Initialize the underyling widget.

        """
        super(WxSplitItem, self).init_widget()
        d = self.declaration
        self.set_stretch(d.stretch)
        self.set_collapsible(d.collapsible)

    def init_layout(self):
        """ Initialize the layout for the underyling widget.

        """
        super(WxSplitItem, self).init_layout()
        self.widget.SetSplitWidget(self.split_widget())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def split_widget(self):
        """ Find and return the split widget child for this widget.

        Returns
        -------
        result : wxWindow or None
            The split widget defined for this widget, or None if one is
            not defined.

        """
        d = self.declaration.split_widget()
        if d is not None:
            return d.proxy.widget or None

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a WxSplitItem.

        """
        super(WxSplitItem, self).child_added(child)
        if isinstance(child, WxContainer):
            self.widget.SetSplitWidget(self.split_widget())

    def child_removed(self, child):
        """ Handle the child removed event for a WxSplitItem.

        """
        super(WxSplitItem, self).child_removed(child)
        if isinstance(child, WxContainer):
            self.widget.SetSplitWidget(self.split_widget())

    #--------------------------------------------------------------------------
    # ProxySplitItem API
    #--------------------------------------------------------------------------
    def set_stretch(self, stretch):
        """ Set the stretch factor for the underlying widget.

        """
        self.widget.SetStretch(stretch)

    def set_collapsible(self, collapsible):
        """ Set the collapsible flag for the underlying widget.

        This is not supported on wx.

        """
        pass
