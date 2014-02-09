#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx
from wx.lib.splitter import MultiSplitterWindow

from atom.api import Typed

from enaml.widgets.splitter import ProxySplitter

from .wx_constraints_widget import WxConstraintsWidget
from .wx_split_item import WxSplitItem


_ORIENTATION_MAP = {
    'horizontal': wx.HORIZONTAL,
    'vertical': wx.VERTICAL,
}


class wxSplitter(MultiSplitterWindow):
    """ A wx.lib.splitter.MultiSplitterWindow subclass that changes
    the behavior of resizing neighbors to be consistent with Qt.

    """
    def _OnMouse(self, event):
        """ Overriden parent class mouse event handler which fakes the
        state of the keyboard so that resize behavior is consistent
        between wx and Qt.

        """
        # We modify the mouse event to "fake" like the shift key is
        # always down. This causes the splitter to not adjust its
        # neighbor when dragging the sash. This behavior is consistent
        # with Qt's behavior. This is not *the best* way to handle this,
        # but it's the easiest and quickest at the moment. The proper
        # way would be to reimplement this method in its entirety and
        # allow the adjustNeighbor computation to be based on keyboard
        # state as well as attribute flags.
        #
        # TODO implement this properly (or just rewrite this entire
        # control, because like everything else in Wx, it's crap).
        event.m_shiftDown = True
        return super(wxSplitter, self)._OnMouse(event)

    def _GetWindowMin(self, window):
        """ Overriden parent class method which properly computes the
        window min size.

        """
        size = window.GetEffectiveMinSize()
        if self._orient == wx.HORIZONTAL:
            res = size.GetWidth()
        else:
            res = size.GetHeight()
        return res

    def _GetSashSize(self):
        """ Overridden parent class method to return a proper sash size
        for the custom sash painting.

        """
        return 4

    def _DrawSash(self, dc):
        """ Overridden parent class method which draws a custom sash.

        On Windows, the default themed sash drawing causes the sash to
        not be visible; this method corrects that problem and draws a
        sash which is visibly similar to Enaml's Qt Windows version.

        """
        sash_size = self._GetSashSize()
        width, height = self.GetClientSize()
        light_pen = wx.WHITE_PEN
        dark_pen = wx.GREY_PEN
        brush = wx.Brush(self.GetBackgroundColour())
        if self._orient == wx.HORIZONTAL:
            pos = 0
            for sash in self._sashes[:-1]:
                pos += sash
                dc.SetPen(wx.TRANSPARENT_PEN)
                dc.SetBrush(brush)
                dc.DrawRectangle(pos, 0, sash_size, height)
                dc.SetPen(light_pen)
                dc.DrawLine(pos + 1, 0, pos + 1, height)
                dc.SetPen(dark_pen)
                dc.DrawLine(pos + 2, 0, pos + 2, height)
                pos += sash_size
        else:
            pos = 0
            for sash in self._sashes[:-1]:
                pos += sash
                dc.SetPen(wx.TRANSPARENT_PEN)
                dc.SetBrush(brush)
                dc.DrawRectangle(0, pos, width, sash_size)
                dc.SetPen(light_pen)
                dc.DrawLine(0, pos + 1, width, pos + 1)
                dc.SetPen(dark_pen)
                dc.DrawLine(0, pos + 2, width, pos + 2)
                pos += sash_size

    def _OnSize(self, event):
        """ Overridden parent class method which resizes the sashes.

        The default Wx behavior allocates all extra space to the last
        split item, and it will clip the items when the window size is
        reduced. This override uses a weighted algorithm to allocate
        the free space among the items and will not allow the items
        to be clipped by a window resize.

        """
        # Pre-fetch some commonly used objects
        get_min = self._GetWindowMin
        windows = self._windows
        sashes = self._sashes

        # Compute the total space available for the sashes
        sash_widths = self._GetSashSize() * (len(windows) - 1)
        offset = sash_widths + 2 * self._GetBorderSize()
        if self._orient == wx.HORIZONTAL:
            free_space = self.GetClientSize().GetWidth() - offset
        else:
            free_space = self.GetClientSize().GetHeight() - offset

        # Compute the effective stretch factors for each window. The
        # effective stretch factor is the greater of the current or
        # minimum width of the window, multiplied by the window's
        # stretch factor.
        parts = []
        total_stretch = 0
        for idx, (sash, window) in enumerate(zip(sashes, windows)):
            minw = get_min(window)
            if sash < minw:
                sash = sashes[idx] = minw
            stretch = window.GetStretch() * sash
            parts.append((stretch, idx, minw, window))
            total_stretch += stretch

        # Add (or remove) the extra space by fairly allocating it to
        # each window based on their effective stretch factor.
        diff_space = free_space - sum(sashes)
        for stretch, idx, minw, window in parts:
            if stretch > 0:
                d = diff_space * stretch / total_stretch
                new = max(sashes[idx] + d, minw)
                sashes[idx] = new

        # Since the windows are clipped to their minimum width, it's
        # possible that the current space occupied by the windows will
        # be too large. In that case, the overage is distributed to the
        # windows fairly, based on their relative capacity for shrink.
        curr_space = sum(sashes)
        if curr_space > free_space:
            diffs = []
            total_diff = 0
            for stretch, idx, minw, window in parts:
                diff = sashes[idx] - minw
                if diff > 0:
                    diffs.append((diff, window, idx, minw))
                    total_diff += diff
            remaining = curr_space - free_space
            diffs.sort()
            for diff, window, idx, minw in reversed(diffs):
                delta = remaining * diff / total_diff
                old = sashes[idx]
                new = max(old - delta, minw)
                actual_diff = old - new
                remaining -= actual_diff
                total_diff -= actual_diff
                sashes[idx] = new

        # The superclass handler which will actually perform the layout.
        super(wxSplitter, self)._OnSize(event)


class WxSplitter(WxConstraintsWidget, ProxySplitter):
    """ A Wx implementation of an Enaml ProxySplitter.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(wxSplitter)

    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying wxSplitter widget.

        """
        self.widget = wxSplitter(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying control.

        """
        super(WxSplitter, self).init_widget()
        d = self.declaration
        self.set_orientation(d.orientation, guard=False)
        self.set_live_drag(d.live_drag)

    def init_layout(self):
        """ Handle the layout initialization for the splitter.

        """
        super(WxSplitter, self).init_layout()
        widget = self.widget
        for item in self.split_items():
            widget.AppendWindow(item)

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a WxSplitter.

        """
        super(WxSplitter, self).child_added(child)
        if isinstance(child, WxSplitItem):
            for index, dchild in enumerate(self.children()):
                if child is dchild:
                    self.widget.InsertWindow(index, child.widget)
                    self.geometry_updated()

    def child_removed(self, child):
        """ Handle the child removed event for a WxSplitter.

        """
        super(WxSplitter, self).child_removed(child)
        if isinstance(child, WxSplitItem):
            widget = child.widget
            self.widget.DetachWindow(widget)
            widget.Hide()
            self.geometry_updated()

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def split_items(self):
        """ Get the split items defined for the widget.

        """
        for d in self.declaration.split_items():
            yield d.proxy.widget or None

    #--------------------------------------------------------------------------
    # ProxySplitter API
    #--------------------------------------------------------------------------
    def set_orientation(self, orientation, guard=True):
        """ Update the orientation of the splitter.

        """
        wx_orientation = _ORIENTATION_MAP[orientation]
        widget = self.widget
        if guard:
            with self.geometry_guard():
                widget.SetOrientation(wx_orientation)
                widget.SizeWindows()
        else:
            widget.SetOrientation(wx_orientation)
            widget.SizeWindows()

    def set_live_drag(self, live_drag):
        """ Updates the drag state of the splitter.

        """
        if live_drag:
            self.widget.WindowStyle |= wx.SP_LIVE_UPDATE
        else:
            self.widget.WindowStyle &= ~wx.SP_LIVE_UPDATE
