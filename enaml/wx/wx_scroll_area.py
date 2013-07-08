#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from atom.api import Typed

from enaml.widgets.scroll_area import ProxyScrollArea

from .wx_container import WxContainer
from .wx_frame import WxFrame
from .wx_single_widget_sizer import wxSingleWidgetSizer


# The 'always_on' scroll policy is not supported on wx, because it
# requires setting a window style flag which does not dynamically
# toggle in a reliable fashion. Since we only support 'off' or 'auto'
# it's easiest to use this mapping to convert straight from policy
# values into a respective scroll rate. A rate of Zero causes wx not
# to show the scroll bar. A positive rate indicates to scroll that many
# pixels per event. We set the rate to 1 to have smooth scrolling. Wx
# doesn't make a distinction between scroll events caused by the mouse
# or scrollbar and those caused by clicking the scroll buttons (ala qt),
# and thus this rate applies the same to all of those events. Since we
# expect that clicking on a scroll button happens much more infrequently
# than scrolling by dragging the scroll bar, we opt for a lower rate
# in order to get smooth drag scrolling and sacrifice some usability
# on the scroll buttons.
SCROLLBAR_MAP = {
    'as_needed': 1,
    'always_off': 0,
    'always_on': 1,
}


class wxScrollAreaSizer(wxSingleWidgetSizer):
    """ A wxSingleWidgetSizer subclass which makes adjusts the min
    size to account for a 2 pixel error in Wx.

    """
    def CalcMin(self):
        """ Returns the minimum size for the area owned by the sizer.

        Returns
        -------
        result : wxSize
            The wx size representing the minimum area required by the
            sizer.

        """
        # The effective min size computation is correct, but the wx
        # scrolled window interprets it with an error of 2px. That
        # is we need to make wx think that the min size is 2px smaller
        # than it actually is so that scroll bars should and hide at
        # the appropriate sizes.
        res = super(wxScrollAreaSizer, self).CalcMin()
        if res.IsFullySpecified():
            res.width -= 2
            res.height -= 2
        return res


class wxScrollArea(wx.ScrolledWindow):
    """ A custom wx.ScrolledWindow which is suits Enaml's use case.

    """
    #: The internal best size. The same as QAbstractScrollArea.
    _best_size = wx.Size(256, 192)

    def __init__(self, *args, **kwargs):
        """ Initialize a wxScrollArea.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initialize
            a wxScrolledWindow.

        """
        super(wxScrollArea, self).__init__(*args, **kwargs)
        self._scroll_widget = None
        self.SetSizer(wxScrollAreaSizer())

    def GetBestSize(self):
        """ An overridden parent class method which returns a sensible
        best size.

        The default wx implementation returns a best size of (16, 16)
        on Windows; far too small to be useful. So, we just adopt the
        size hint of (256, 192) used in Qt's QAbstractScrollArea.

        """
        return self._best_size

    def GetScrollWidget(self):
        """ Get the scroll widget for this scroll area.

        Returns
        -------
        results : wxWindow
            The wxWindow being scrolled by this scroll area.

        """
        return self._scroll_widget

    def SetScrollWidget(self, widget):
        """ Set the scroll widget for this scroll area.

        Parameters
        ----------
        widget : wxWindow
            The wxWindow which should be scrolled by this area.

        """
        self._scroll_widget = widget
        self.GetSizer().Add(widget)


class WxScrollArea(WxFrame, ProxyScrollArea):
    """ A Wx implementation of an Enaml ScrollArea.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(wxScrollArea)

    def create_widget(self):
        """ Create the underlying wxScrolledWindow widget.

        """
        style = wx.HSCROLL | wx.VSCROLL | wx.BORDER_SIMPLE
        self.widget = wxScrollArea(self.parent_widget(), style=style)

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(WxScrollArea, self).init_widget()
        d = self.declaration
        self.set_horizontal_policy(d.horizontal_policy)
        self.set_vertical_policy(d.vertical_policy)
        self.set_widget_resizable(d.widget_resizable)

    def init_layout(self):
        """ Handle the layout initialization for the scroll area.

        """
        super(WxScrollArea, self).init_layout()
        self.widget.SetScrollWidget(self.scroll_widget())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def scroll_widget(self):
        """ Find and return the scroll widget child for this widget.

        """
        w = self.declaration.scroll_widget()
        if w is not None:
            return w.proxy.widget or None

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a WxScrollArea.

        """
        super(WxScrollArea, self).child_added(child)
        if isinstance(child, WxContainer):
            self.widget.SetScrollWidget(self.scroll_widget())

    def child_removed(self, child):
        """ Handle the child removed event for a WxScrollArea.

        """
        super(WxScrollArea, self).child_removed(child)
        if isinstance(child, WxContainer):
            self.widget.SetScrollWidget(self.scroll_widget())

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def replace_constraints(self, old_cns, new_cns):
        """ A reimplemented WxConstraintsWidget layout method.

        Constraints layout may not cross the boundary of a ScrollArea,
        so this method is no-op which stops the layout propagation.

        """
        pass

    #--------------------------------------------------------------------------
    # ProxyScrollArea API
    #--------------------------------------------------------------------------
    def set_horizontal_policy(self, policy):
        """ Set the horizontal scrollbar policy of the widget.

        """
        horiz = SCROLLBAR_MAP[policy]
        vert = SCROLLBAR_MAP[self.declaration.vertical_policy]
        self.widget.SetScrollRate(horiz, vert)

    def set_vertical_policy(self, policy):
        """ Set the vertical scrollbar policy of the widget.

        """
        horiz = SCROLLBAR_MAP[self.declaration.horizontal_policy]
        vert = SCROLLBAR_MAP[policy]
        self.widget.SetScrollRate(horiz, vert)

    def set_widget_resizable(self, resizable):
        """ Set whether or not the scroll widget is resizable.

        This is not supported on Wx.

        """
        pass
