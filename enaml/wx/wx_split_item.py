#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

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


class WxSplitItem(WxWidget):
    """ A Wx implementation of an Enaml SplitItem.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying QStackItem widget.

        """
        return wxSplitItem(parent)

    def create(self, tree):
        """ Create and initialize the underyling widget.

        """
        super(WxSplitItem, self).create(tree)
        self.set_stretch(tree['stretch'])
        self.set_collapsible(tree['collapsible'])

    def init_layout(self):
        """ Initialize the layout for the underyling widget.

        """
        super(WxSplitItem, self).init_layout()
        self.widget().SetSplitWidget(self.split_widget())

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
        widget = None
        for child in self.children():
            if isinstance(child, WxContainer):
                widget = child.widget()
        return widget

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a WxSplitItem.

        """
        if isinstance(child, WxContainer):
            self.widget().SetSplitWidget(self.split_widget())

    def child_added(self, child):
        """ Handle the child added event for a QtSplitItem.

        """
        if isinstance(child, WxContainer):
            self.widget().SetSplitWidget(self.split_widget())

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_stretch(self, content):
        """ Handle the 'set_stretch' action from the Enaml widget.

        """
        self.set_stretch(content['stretch'])

    def on_action_set_collapsible(self, content):
        """ Handle the 'set_collapsible' action from the Enaml widget.

        """
        self.set_collapsible(content['collapsible'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_stretch(self, stretch):
        """ Set the stretch factor for the underlying widget.

        """
        self.widget().SetStretch(stretch)

    def set_collapsible(self, collapsible):
        """ Set the collapsible flag for the underlying widget.

        """
        # Not supported on Wx
        pass

