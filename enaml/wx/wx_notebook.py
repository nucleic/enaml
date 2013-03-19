#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import weakref
import wx

from atom.api import Instance

from enaml.widgets.notebook import ProxyNotebook

from .wx_constraints_widget import WxConstraintsWidget
from .wx_layout_request import EVT_COMMAND_LAYOUT_REQUESTED
from .wx_page import WxPage
from .wx_upstream import aui


#: A mapping of notebook tab positions for the document style tabs.
#: Wx currently only supports top and bottom tab positions.
_TAB_POSITION_MAP = {
    'top': aui.AUI_NB_TOP,
    'left': aui.AUI_NB_TOP,
    'bottom': aui.AUI_NB_BOTTOM,
    'right': aui.AUI_NB_BOTTOM,
}


#: A mask of notebook tab positions for the document style tabs.
_TAB_POSITION_MASK = aui.AUI_NB_TOP | aui.AUI_NB_BOTTOM


class wxDocumentNotebook(aui.AuiNotebook):
    """ A custom AuiNotebook which handles children of type wxPage.

    This notebook is used to implement 'document' style tabs for an
    Enaml Notebook control.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxDocumentNotebook.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments to pass to the super
            class.

        """
        super(wxDocumentNotebook, self).__init__(*args, **kwargs)
        self.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnPageClose)
        self._hidden_pages = weakref.WeakKeyDictionary()

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def OnPageClose(self, event):
        """ The handler for the EVT_AUINOTEBOOK_PAGE_CLOSE event.

        This handler forwards the event to the wxPage instance.

        """
        self.GetPage(event.GetSelection()).OnClose(event)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def GetBestSize(self):
        """ Overridden GetBestSize method which will return the best
        size for the notebook.

        """
        size = wx.Size(256, 192)
        for idx in xrange(self.GetPageCount()):
            page = self.GetPage(idx)
            psize = page.GetBestSize()
            size.SetWidth(max(size.GetWidth(), psize.GetWidth()))
            size.SetHeight(max(size.GetHeight(), psize.GetHeight()))
        # On windows, there's an off by 2 error in the width.
        height = self.GetHeightForPageHeight(size.GetHeight())
        return wx.Size(size.GetWidth() + 2, height)

    def ShowWxPage(self, page):
        """ Show a hidden wxPage instance in the notebook.

        If the page is not owned by the notebook, this is a no-op.

        Parameters
        ----------
        page : wxPage
            The hidden wxPage instance to show in the notebook.

        """
        index = self.GetPageIndex(page)
        if index == -1:
            index = self._hidden_pages.pop(page, -1)
            if index != -1:
                self.InsertWxPage(index, page)

    def HideWxPage(self, page):
        """ Hide the given wxPage instance in the notebook.

        If the page is not owned by the notebook, this is a no-op.

        Parameters
        ----------
        page : wxPage
            The wxPage instance to hide in the notebook.

        """
        index = self.GetPageIndex(page)
        if index != -1:
            self.RemovePage(index)
            page.Show(False)
            self._hidden_pages[page] = index

    def AddWxPage(self, page):
        """ Add a wxPage instance to the notebook.

        This should be used in favor of AddPage for adding a wxPage
        instance to the notebook, as it takes into account the current
        page state.

        Parameters
        ----------
        page : wxPage
            The wxPage instance to add to the notebook.

        """
        if page.IsOpen():
            self.AddPage(page, page.GetTitle())
            index = self.GetPageIndex(page)
            if not page.GetEnabled():
                self.EnableTab(index, False)
            if not page.GetClosable():
                self.SetCloseButton(index, False)
        else:
            page.Show(False)
            self._hidden_pages[page] = self.GetPageCount()

    def InsertWxPage(self, index, page):
        """ Insert a wxPage instance into the notebook.

        This should be used in favor of InsertPage for inserting a
        wxPage instance into the notebook, as it takes into account the
        current page state.

        Parameters
        ----------
        index : int
            The index at which to insert the page.

        page : wxPage
            The wxPage instance to add to the notebook.

        """
        if page.IsOpen():
            index = min(index, self.GetPageCount())
            self.InsertPage(index, page, page.GetTitle())
            if not page.GetEnabled():
                self.EnableTab(index, False)
            if not page.GetClosable():
                self.SetCloseButton(index, False)
        else:
            page.Show(False)
            self._hidden_pages[page] = index

    def RemoveWxPage(self, page):
        """ Remove a wxPage instance from the notebook.

        If the page does not exist in the notebook, this is a no-op.

        Parameters
        ----------
        page : wxPage
            The wxPage instance to remove from the notebook.

        """
        index = self.GetPageIndex(page)
        if index != -1:
            self.RemovePage(index)
            page.Show(False)


class wxPreferencesNotebook(wx.Notebook):
    """ A custom wx.Notebook which handles children of type wxPage.

    This notebook is used to implement 'document' style tabs for an
    Enaml Notebook control.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxPreferencesNotebook.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments to pass to the super
            class.

        """
        super(wxPreferencesNotebook, self).__init__(*args, **kwargs)
        self._hidden_pages = weakref.WeakKeyDictionary()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def GetBestSize(self):
        """ Overridden GetBestSize method which will return the best
        size for the notebook.

        """
        size = wx.Size(256, 192)
        for idx in xrange(self.GetPageCount()):
            page = self.GetPage(idx)
            psize = page.GetBestSize()
            size.SetWidth(max(size.GetWidth(), psize.GetWidth()))
            size.SetHeight(max(size.GetHeight(), psize.GetHeight()))
        # On windows, the wx.Notebook renders each page with 2 pixels
        # of padding on the top, and bottom, and 4 pixels of padding
        # on the left and right (at least under the Windows 7 theme).
        # We need to compensate for this padding along with the space
        # taken up by the tab bar. The tab bar height was manually
        # measured to be 21 pixels. I've found no way to have wx measure
        # it for me (there's nothing in RendererNative for it), so its
        # just hard-coded for now.
        return wx.Size(size.GetWidth() + 8, size.GetHeight() + 25)

    def ShowWxPage(self, page):
        """ Show a hidden wxPage instance in the notebook.

        If the page is not owned by the notebook, this is a no-op.

        Parameters
        ----------
        page : wxPage
            The hidden wxPage instance to show in the notebook.

        """
        index = self.GetPageIndex(page)
        if index == -1:
            index = self._hidden_pages.pop(page, -1)
            if index != -1:
                self.InsertWxPage(index, page)

    def HideWxPage(self, page):
        """ Hide the given wxPage instance in the notebook.

        If the page is not owned by the notebook, this is a no-op.

        Parameters
        ----------
        page : wxPage
            The wxPage instance to hide in the notebook.

        """
        index = self.GetPageIndex(page)
        if index != -1:
            self.RemovePage(index)
            page.Show(False)
            self._hidden_pages[page] = index

    def AddWxPage(self, page):
        """ Add a wxPage instance to the notebook.

        This should be used in favor of AddPage for adding a wxPage
        instance to the notebook, as it takes into account the current
        page state.

        Parameters
        ----------
        page : wxPage
            The wxPage instance to add to the notebook.

        """
        if page.IsOpen():
            self.AddPage(page, page.GetTitle())
        else:
            page.Show(False)
            self._hidden_pages[page] = self.GetPageCount()

    def InsertWxPage(self, index, page):
        """ Insert a wxPage instance into the notebook.

        This should be used in favor of InsertPage for inserting a
        wxPage instance into the notebook, as it takes into account the
        current page state.

        Parameters
        ----------
        index : int
            The index at which to insert the page.

        page : wxPage
            The wxPage instance to add to the notebook.

        """
        if page.IsOpen():
            index = min(index, self.GetPageCount())
            self.InsertPage(index, page, page.GetTitle())
        else:
            page.Show(False)
            self._hidden_pages[page] = index

    def RemoveWxPage(self, page):
        """ Remove a wxPage instance from the notebook.

        If the page does not exist in the notebook, this is a no-op.

        Parameters
        ----------
        page : wxPage
            The wxPage instance to remove from the notebook.

        """
        index = self.GetPageIndex(page)
        if index != -1:
            self.RemovePage(index)
            page.Show(False)

    def GetPageIndex(self, page):
        """ Returns the index of the page in the control.

        Parameters
        ----------
        page : wxPage
            The wxPage instance in the control.

        Returns
        -------
        result : int
            The index of the page in the control, or -1 if the page
            is not found.

        """
        # Wx has no way of querying for the index of a page, so we must
        # linear search ourselves. Hooray for brain-dead toolkits!
        for idx in xrange(self.GetPageCount()):
            if self.GetPage(idx) == page:
                return idx
        return -1

    def EnableTab(self, index, enabled):
        """ Change the enabled state of the tab at the given index.

        Parameters
        ----------
        index : int
            The index of the target tab.

        enabled : bool
            Whether or not the tab should be enabled.

        """
        if index >= 0 and index < self.GetPageCount():
            page = self.GetPage(index)
            page.Enable(enabled)

    def SetCloseButton(self, index, closable):
        """ A dummy method which makes the wxPreferencesNotebook api
        compatible with the wxDocumentNotebook.

        Close buttons cannot be set on a preferences notebook. This
        method exists soley so that child wxPages do not need to
        special case their implementation based on their parent.

        """
        pass


class WxNotebook(WxConstraintsWidget, ProxyNotebook):
    """ A Wx implementation of an Enaml ProxyNotebook.

    """
    #: A reference to the widget created by the proxy.
    widget = Instance((wxPreferencesNotebook, wxDocumentNotebook))

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying wx notebook widget.

        """
        if self.declaration.tab_style == 'preferences':
            w = wxPreferencesNotebook(self.parent_widget())
        else:
            style = aui.AUI_NB_SCROLL_BUTTONS
            w = wxDocumentNotebook(self.parent_widget(), agwStyle=style)
        self.widget = w

    def init_widget(self):
        """ Create and initialize the notebook control

        """
        super(WxNotebook, self).init_widget()
        d = self.declaration
        self.set_tab_style(d.tab_style)
        self.set_tab_position(d.tab_position)
        self.set_tabs_closable(d.tabs_closable)
        self.set_tabs_movable(d.tabs_movable)

    def init_layout(self):
        """ Handle the layout initialization for the notebook.

        """
        super(WxNotebook, self).init_layout()
        widget = self.widget
        for page in self.pages():
            widget.AddWxPage(page)
        widget.Bind(EVT_COMMAND_LAYOUT_REQUESTED, self.on_layout_requested)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def pages(self):
        """ Get the pages defined for the notebook.

        """
        for p in self.declaration.pages():
            yield p.proxy.widget or None

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a WxNotebook.

        """
        super(WxNotebook, self).child_added(child)
        if isinstance(child, WxPage):
             for index, dchild in enumerate(self.children()):
                if child is dchild:
                    self.widget.InsertWxPage(index, child.widget)

    def child_removed(self, child):
        """ Handle the child removed event for a WxNotebook.

        """
        super(WxNotebook, self).child_removed(child)
        if isinstance(child, WxPage):
            self.widget().RemoveWxPage(child.widget)
            self.size_hint_updated()

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_layout_requested(self, event):
        """ Handle the layout request event from a child page.

        """
        self.size_hint_updated()

    #--------------------------------------------------------------------------
    # ProxyNotebook API
    #--------------------------------------------------------------------------
    def set_tab_style(self, style):
        """ Set the tab style for the underlying widget.

        """
        # Changing the tab style on wx is not supported
        pass

    def set_tab_position(self, position):
        """ Set the position of the tab bar in the widget.

        """
        # Tab position changes only supported on the document notebook.
        widget = self.widget
        if isinstance(widget, wxDocumentNotebook):
            flags = widget.GetAGWWindowStyleFlag()
            flags &= ~_TAB_POSITION_MASK
            flags |= _TAB_POSITION_MAP[position]
            widget.SetAGWWindowStyleFlag(flags)
            widget.Refresh() # Avoids rendering artifacts

    def set_tabs_closable(self, closable):
        """ Set whether or not the tabs are closable.

        """
        # Closable tabs are only supported on the document notebook.
        widget = self.widget
        if isinstance(widget, wxDocumentNotebook):
            flags = widget.GetAGWWindowStyleFlag()
            if closable:
                flags |= aui.AUI_NB_CLOSE_ON_ALL_TABS
            else:
                flags &= ~aui.AUI_NB_CLOSE_ON_ALL_TABS
            widget.SetAGWWindowStyleFlag(flags)

    def set_tabs_movable(self, movable):
        """ Set whether or not the tabs are movable.

        """
        # Movable tabs are only supported on the document notebook.
        widget = self.widget
        if isinstance(widget, wxDocumentNotebook):
            flags = widget.GetAGWWindowStyleFlag()
            if movable:
               flags |= aui.AUI_NB_TAB_MOVE
            else:
               flags &= ~aui.AUI_NB_TAB_MOVE
            widget.SetAGWWindowStyleFlag(flags)
