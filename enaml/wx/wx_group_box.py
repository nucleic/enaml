#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx

from atom.api import Typed

from enaml.widgets.group_box import ProxyGroupBox

from .wx_container import WxContainer, wxContainer


WX_ALIGNMENTS = {
    'left': wx.ALIGN_LEFT,
    'center': wx.ALIGN_CENTER,
    'right': wx.ALIGN_RIGHT,
}


class wxGroupBox(wxContainer):
    """ A wxContainer sublcass that implements GroupBox functionality.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxGroupBox.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments to initialize a
            wxContainer.

        """
        super(wxGroupBox, self).__init__(*args, **kwargs)
        self._title = ''
        self._border = wx.StaticBox(self)
        self._line = wx.StaticLine(self)
        self._label = wx.StaticText(self)
        self._label.Raise()
        self._label_size = self._label.GetBestSize()
        self._title_alignment = wx.ALIGN_LEFT
        self._flat = False
        # Set the panel to double buffered or suffer terrible
        # rendering artifacts
        self.SetDoubleBuffered(True)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def GetAlignment(self):
        """ Return the wx alignment flag for the current alignment
        of the group box title.

        """
        return self._title_alignment

    def SetAlignment(self, alignment):
        """ Set the alignment of the title of the group box. Should
        be one of wx.ALIGN_LEFT, wx.ALIGN_RIGHT, wx.ALIGN_CENTER.

        """
        self._title_alignment = alignment
        self._update_layout()

    def GetFlat(self):
        """ Returns a boolean indicating whether the group box is using
        a flat style.

        """
        return self._flat

    def SetFlat(self, flat):
        """ Set whether or not the group box should be displayed using
        a flat style.

        """
        self._flat = flat
        if flat:
            self._border.Show(False)
            self._line.Show(True)
        else:
            self._border.Show(True)
            self._line.Show(False)
        self._update_layout()

    def GetTitle(self):
        """ Return the current title text in the group box.

        """
        # Undo the hack applied in SetTitle(...)
        title = self._title
        if title:
            title = title[1:-1]
        return title

    def SetTitle(self, title):
        """ Set the current title text in the group box.

        """
        # A bit of a hack to give us a little padding around the label
        if title:
            title = ' %s ' % title
        self._title = title
        self._label.SetLabel(title)
        self._label_size = self._label.GetBestSize()
        if not title:
            self._label.Show(False)
        else:
            self._label.Show(True)
        self._update_layout()

    def SetDimensions(self, x, y, width, height):
        """ Overridden parent class method to synchronize the group
        box decorations.

        """
        super(wxGroupBox, self).SetDimensions(x, y, width, height)
        self._update_layout()

    def SetSize(self, size):
        """ Overridden parent class method to synchronize the group
        box decorations.

        """
        super(wxGroupBox, self).SetSize(size)
        self._update_layout()

    def GetContentsMargins(self):
        """ Get the contents margins for the group box.

        These margins are computed empirically so that they look similar
        to the margins provided by Qt on Windows.

        Returns
        -------
        result : tuple
            The top, right, bottom, and left margin values.

        """
        label = self._label
        height = label.GetCharHeight()
        if not label.IsShown():
            height /= 2
        return (height, 1, 1, 1)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _update_layout(self):
        """ Synchronizes the drawing of the group box decorations with
        the panel.

        """
        if self._flat:
            self._update_line_geometry()
        else:
            self._update_border_geometry()
        self._update_title_geometry()
        self.Refresh()

    def _update_border_geometry(self):
        """ Updates the geometry of the border.

        """
        width, height = self.GetSizeTuple()
        self._border.SetSizeWH(width, height)

    def _update_line_geometry(self):
        """ Updates the geometry of the line.

        """
        y = self._label_size.GetHeight() / 2
        width, _ = self.GetSizeTuple()
        self._line.SetDimensions(0, y, width, 2)

    def _update_title_geometry(self):
        """ Updates the geometry of the title.

        """
        label = self._label
        flat = self._flat
        align = self._title_alignment
        text_width, _ = self._label_size
        width, _ = self.GetSizeTuple()
        # These offsets are determined empirically to look similar
        # in form to Qt on Windows
        if align == wx.ALIGN_LEFT:
            x = 0 if flat else 8
            label.Move((x, 0))
        elif align == wx.ALIGN_RIGHT:
            right = width
            right -= 0 if flat else 8
            x = right - text_width
            label.Move((x, 0))
        elif align == wx.ALIGN_CENTER:
            label.CenterOnParent(dir=wx.HORIZONTAL)
        else:
            raise ValueError('Invalid title alignment %s' % align)


class WxGroupBox(WxContainer, ProxyGroupBox):
    """ A Wx implementation of an Enaml ProxyGroupBox.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(wxGroupBox)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Creates the underlying QGroupBox control.

        """
        self.widget = wxGroupBox(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(WxGroupBox, self).init_widget()
        d = self.declaration
        self.set_title(d.title, cm_update=False)
        self.set_flat(d.flat)
        self.set_title_align(d.title_align)

    #--------------------------------------------------------------------------
    # Layout Handling
    #--------------------------------------------------------------------------
    def contents_margins(self):
        """ Get the current contents margins for the group box.

        """
        return self.widget.GetContentsMargins()

    #--------------------------------------------------------------------------
    # ProxyGroupBox API
    #--------------------------------------------------------------------------
    def set_title(self, title, cm_update=True):
        """ Update the title of the group box.

        """
        if not cm_update:
            self.widget.SetTitle(title)
            return
        widget = self.widget
        old_margins = widget.GetContentsMargins()
        widget.SetTitle(title)
        new_margins = widget.GetContentsMargins()
        if old_margins != new_margins:
            self.contents_margins_updated()

    def set_flat(self, flat):
        """ Updates the flattened appearance of the group box.

        """
        self.widget.SetFlat(flat)

    def set_title_align(self, align):
        """ Updates the alignment of the title of the group box.

        """
        wx_align = WX_ALIGNMENTS[align]
        self.widget.SetAlignment(wx_align)
