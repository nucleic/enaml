#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import wx
import wx.lib.newevent

from atom.api import Typed

from enaml.widgets.page import ProxyPage

from .wx_container import WxContainer
from .wx_widget import WxWidget
from .wx_single_widget_sizer import wxSingleWidgetSizer


#: An event emitted when the notebook page is closed.
wxPageClosedEvent, EVT_PAGE_CLOSED = wx.lib.newevent.NewEvent()


class wxPage(wx.Panel):
    """ A wxPanel subclass which acts as a page in a wx notebook.

    """
    def __init__(self, *args, **kwargs):
        """ Initialize a wxPage.

        Parameters
        ----------
        *args, **kwargs
            The position and keyword arguments required to initialize
            a wxContainer.

        """
        super(wxPage, self).__init__(*args, **kwargs)
        self._title = u''
        self._closable = True
        self._is_enabled = True
        self._is_open = True
        self._page_widget = None
        self.SetSizer(wxSingleWidgetSizer())
        self.Bind(wx.EVT_SHOW, self.OnShow)

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def OnClose(self, event):
        """ Handle the page close event.

        This event handler is called by the parent notebook. The parent
        event is always be vetoed or else Wx will destroy the page. If
        the page is closable, we close the page and emit the custom
        close event.

        """
        event.Veto()
        if self.GetClosable():
            self.Close()
            evt = wxPageClosedEvent()
            wx.PostEvent(self, evt)

    def OnShow(self, event):
        """ Handle the show event.

        Wx will not emit an EVT_SHOW on the child of this page. So, this
        event handler passes the show event along to the contained page
        widget, so that it can disable its layout when not visible.

        """
        page = self._page_widget
        if page:
            wx.PostEvent(page, event)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _PageIndexOperation(self, closure):
        """ A private method which will run the given closure if there
        is a valid index for this page.

        """
        parent = self.GetParent()
        if parent:
            index = parent.GetPageIndex(self)
            if index != -1:
                closure(parent, index)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def GetPageWidget(self):
        """ Get the page widget for this page.

        Returns
        -------
        result : wxWindow or None
            The page widget being managed by this page.

        """
        return self._page_widget

    def SetPageWidget(self, widget):
        """ Set the page widget for this page.

        Parameters
        ----------
        widget : wxWindow
            The wx widget to use as the page widget in this page.

        """
        self._page_widget = widget
        self.GetSizer().Add(widget)

    def IsOpen(self):
        """ Get whether or not the page is open.

        Returns
        -------
        result : bool
            True if the page is open, False otherwise.

        """
        return self._is_open

    def Open(self):
        """ Open the page in the notebook.

        """
        self._is_open = True
        parent = self.GetParent()
        if parent:
            parent.ShowWxPage(self)

    def Close(self):
        """ Close the page in the notebook.

        """
        self._is_open = False
        parent = self.GetParent()
        if parent:
            parent.HideWxPage(self)

    def GetEnabled(self):
        """ Get the enabled state of the page.

        This method should be used in favor of IsEnabled.

        Returns
        -------
        result : bool
            True the page is enabled, False otherwise.

        """
        return self._is_enabled

    def SetEnabled(self, enabled):
        """ Set the enabled state of the page.

        This method should be used in favor of Enable.

        Parameters
        ---------
        enabled : bool
            Whether or not the page should be enabled.

        """
        self._is_enabled = enabled
        def closure(nb, index):
            nb.EnableTab(index, enabled)
        self._PageIndexOperation(closure)

    def GetTitle(self):
        """ Returns tab title for this page.

        Returns
        -------
        result : unicode
            The title string for the page's tab.

        """
        return self._title

    def SetTitle(self, title):
        """ Set the title for this page.

        Parameters
        ----------
        title : unicode
            The string to use for this page's tab title.

        """
        self._title = title
        def closure(nb, index):
            nb.SetPageText(index, title)
        self._PageIndexOperation(closure)

    def GetClosable(self):
        """ Returns whether or not this page is closable.

        Returns
        -------
        result : bool
            True if this page is closable, False otherwise.

        """
        return self._closable

    def SetClosable(self, closable):
        """ Set whether this page is closable.

        Parameters
        ----------
        closable : bool
            True if this page should be closable, False otherwise.

        """
        self._closable = closable
        def closure(nb, index):
            nb.SetCloseButton(index, closable)
        self._PageIndexOperation(closure)


class WxPage(WxWidget, ProxyPage):
    """ A Wx implementation of an Enaml notebook ProxyPage.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(wxPage)

    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying wxPage widget.

        """
        self.widget = wxPage(self.parent_widget())

    def init_widget(self):
        """ Create and initialize the page control.

        """
        super(WxPage, self).init_widget()
        d = self.declaration
        self.set_title(d.title)
        self.set_closable(d.closable)
        if d.icon:
            self.set_icon(d.icon)
        self.widget.Bind(EVT_PAGE_CLOSED, self.on_page_closed)

    def init_layout(self):
        """ Initialize the layout of the notebook page.

        """
        super(WxPage, self).init_layout()
        self.widget.SetPageWidget(self.page_widget())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def page_widget(self):
        """ Find and return the page widget child for this widget.

        """
        p = self.declaration.page_widget()
        if p is not None:
            return p.proxy.widget or None

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a WxPage.

        """
        super(WxPage, self).child_removed(child)
        if isinstance(child, WxContainer):
            self.widget.SetPageWidget(self.page_widget())

    def child_removed(self, child):
        """ Handle the child removed event for a WxPage.

        """
        super(WxPage, self).child_removed(child)
        if isinstance(child, WxContainer):
            self.widget.SetPageWidget(self.page_widget())

    #--------------------------------------------------------------------------
    # Event Handlers
    #--------------------------------------------------------------------------
    def on_page_closed(self, event):
        """ The event handler for the EVT_PAGE_CLOSED event.

        """
        self.declaration._handle_close()

    #--------------------------------------------------------------------------
    # ProxyPage API
    #--------------------------------------------------------------------------
    def set_visible(self, visible):
        """ An overridden visibility setter which to opens|closes the
        notebook page.

        """
        if visible:
            self.widget.Open()
        else:
            self.widget.Close()

    def ensure_visible(self):
        """ An overridden visibility setter which to opens|closes the
        notebook page.

        """
        self.set_visible(True)

    def ensure_hidden(self):
        """ An overridden visibility setter which to opens|closes the
        notebook page.

        """
        self.set_visible(False)

    def set_enabled(self, enabled):
        """ An overridden enabled setter which sets the tab enabled
        state.

        """
        self.widget.SetEnabled(enabled)

    def set_title(self, title):
        """ Set the title of the tab for this page.

        """
        self.widget.SetTitle(title)

    def set_icon(self, icon):
        """ Sets the widget's icon to the provided image.

        This is not supported on Wx.

        """
        pass

    def set_closable(self, closable):
        """ Set whether or not this page is closable.

        """
        self.widget.SetClosable(closable)
