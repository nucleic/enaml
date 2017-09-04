#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys
from weakref import WeakKeyDictionary

from atom.api import Int, IntEnum, Typed

from enaml.widgets.notebook import ProxyNotebook

from .QtCore import Qt, QEvent, QSize, Signal
from .QtGui import QResizeEvent
from .QtWidgets import (
    QTabWidget, QTabBar, QApplication, QStackedWidget
)

from .qt_constraints_widget import QtConstraintsWidget
from .qt_page import QtPage


TAB_POSITIONS = {
    'top': QTabWidget.North,
    'bottom': QTabWidget.South,
    'left': QTabWidget.West,
    'right': QTabWidget.East,
}


DOCUMENT_MODES = {
    'document': True,
    'preferences': False,
}


class QNotebook(QTabWidget):
    """ A custom QTabWidget which handles children of type QPage.

    """
    class SizeHintMode(IntEnum):
        """ An int enum defining the size hint modes of the notebook.

        """
        #: The size hint is the union of all tabs.
        Union = 0

        #: The size hint is the size hint of the current tab.
        Current = 1

    #: Proxy the SizeHintMode values as if it were an anonymous enum.
    Union = SizeHintMode.Union
    Current = SizeHintMode.Current

    #: A signal emitted when a LayoutRequest event is posted to the
    #: notebook widget. This will typically occur when the size hint
    #: of the notebook is no longer valid.
    layoutRequested = Signal()

    def __init__(self, *args, **kwargs):
        """ Initialize a QNotebook.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to create
            a QTabWidget.

        """
        super(QNotebook, self).__init__(*args, **kwargs)
        self.tabCloseRequested.connect(self.onTabCloseRequested)
        self._hidden_pages = WeakKeyDictionary()
        self._size_hint = QSize()
        self._min_size_hint = QSize()
        self._size_hint_mode = QNotebook.Union

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _refreshTabBar(self):
        """ Trigger an immediate relayout and refresh of the tab bar.

        """
        # The public QTabBar api does not provide a way to trigger the
        # 'layoutTabs' method of QTabBarPrivate and there are certain
        # operations (such as modifying a tab close button) which need
        # to have that happen. This method provides a workaround by
        # sending a dummy resize event to the tab bar, followed by one
        # to the tab widget.
        app = QApplication.instance()
        if app is not None:
            bar = self.tabBar()
            size = bar.size()
            event = QResizeEvent(size, size)
            app.sendEvent(bar, event)
            size = self.size()
            event = QResizeEvent(size, size)
            app.sendEvent(self, event)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def onTabCloseRequested(self, index):
        """ The handler for the 'tabCloseRequested' signal.

        """
        self.widget(index).requestClose()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def event(self, event):
        """ A custom event handler which handles LayoutRequest events.

        When a LayoutRequest event is posted to this widget, it will
        emit the `layoutRequested` signal. This allows an external
        consumer of this widget to update their external layout.

        """
        res = super(QNotebook, self).event(event)
        if event.type() == QEvent.LayoutRequest:
            self._size_hint = QSize()
            self._min_size_hint = QSize()
            self.layoutRequested.emit()
        return res

    def sizeHint(self):
        """ A reimplemented size hint handler.

        """
        # Cached for performance. Invalidated on a layout request.
        hint = self._size_hint
        if hint.isValid():
            return hint
        # QTabWidget does not allow assigning a custom QStackedWidget,
        # so the default sizeHint is computed, and the effects of the
        # stack size hint are replaced by the current tab's size hint.
        hint = super(QNotebook, self).sizeHint()
        if self._size_hint_mode == QNotebook.Current:
            stack = self.findChild(QStackedWidget)
            if stack is not None:
                curr = stack.currentWidget()
                if curr is not None:
                    hint -= stack.sizeHint()
                    hint += curr.sizeHint()
        self._size_hint = hint
        return hint

    def minimumSizeHint(self):
        """ A reimplemented minimum size hint handler.

        """
        # Cached for performance. Invalidated on a layout request.
        hint = self._size_hint
        if hint.isValid():
            return hint
        # QTabWidget does not allow assigning a custom QStackedWidget,
        # so the default minimumSizeHint is computed, and the effects
        # of the stack size hint are replaced by the current tab's
        # minimum size hint.
        hint = super(QNotebook, self).minimumSizeHint()
        if self._size_hint_mode == QNotebook.Current:
            stack = self.findChild(QStackedWidget)
            if stack is not None:
                curr = stack.currentWidget()
                if curr is not None:
                    hint -= stack.minimumSizeHint()
                    hint += curr.minimumSizeHint()
        self._size_hint = hint
        return hint

    def sizeHintMode(self):
        """ Get the size hint mode of the notebook.

        Returns
        -------
        result : QNotebook.SizeHintMode
            The size hint mode enum value for the notebook.

        """
        return self._size_hint_mode

    def setSizeHintMode(self, mode):
        """ Set the size hint mode of the notebook.

        Parameters
        ----------
        mode : QNotebook.SizeHintMode
            The size hint mode for the notebook.

        """
        assert isinstance(mode, QNotebook.SizeHintMode)
        self._size_hint = QSize()
        self._min_size_hint = QSize()
        self._size_hint_mode = mode

    def showPage(self, page):
        """ Show a hidden QPage instance in the notebook.

        If the page is not owned by the notebook, this is a no-op.

        Parameters
        ----------
        page : QPage
            The hidden QPage instance to show in the notebook.

        """
        index = self.indexOf(page)
        if index == -1:
            index = self._hidden_pages.pop(page, -1)
            if index != -1:
                self.insertPage(index, page)

    def hidePage(self, page):
        """ Hide the given QPage instance in the notebook.

        If the page is not owned by the notebook, this is a no-op.

        Parameters
        ----------
        page : QPage
            The QPage instance to hide in the notebook.

        """
        index = self.indexOf(page)
        if index != -1:
            self.removeTab(index)
            page.hide()
            self._hidden_pages[page] = index

    def addPage(self, page):
        """ Add a QPage instance to the notebook.

        This method should be used in favor of the 'addTab' method.

        Parameters
        ----------
        page : QPage
            The QPage instance to add to the notebook.

        """
        self.insertPage(self.count(), page)

    def insertPage(self, index, page):
        """ Insert a QPage instance into the notebook.

        This should be used in favor of the 'insertTab' method.

        Parameters
        ----------
        index : int
            The index at which to insert the page.

        page : QPage
            The QPage instance to add to the notebook.

        """
        if page.isOpen():
            index = min(index, self.count())
            self.insertTab(index, page, page.title())
            self.setTabIcon(index, page.icon())
            self.setTabToolTip(index, page.toolTip())
            self.setTabEnabled(index, page.isTabEnabled())
            self.setTabCloseButtonVisible(index, page.isClosable())
        else:
            page.hide()
            self._hidden_pages[page] = index

    def removePage(self, page):
        """ Remove a QPage instance from the notebook.

        If the page does not exist in the notebook, this is a no-op.

        Parameters
        ----------
        page : QPage
            The QPage instance to remove from the notebook.

        """
        index = self.indexOf(page)
        if index != -1:
            self.removeTab(index)
            page.hide()

    def setTabCloseButtonVisible(self, index, visible, refresh=True):
        """ Set whether the close button for the given tab is visible.

        The 'tabsClosable' property must be set to True for this to
        have effect.

        Parameters
        ----------
        index : int
            The index of the target page.

        visible : bool
            Whether or not the close button for the tab should be
            visible.

        refresh : bool, optional
            Whether or not to refresh the tab bar at the end of the
            operation. The default is True.

        """
        # When changing the visibility of a button, we also change its
        # size so that the tab can layout properly.
        if index >= 0 and index < self.count():
            tabBar = self.tabBar()
            btn1 = tabBar.tabButton(index, QTabBar.LeftSide)
            btn2 = tabBar.tabButton(index, QTabBar.RightSide)
            if btn1 is not None:
                btn1.setVisible(visible)
                if not visible:
                    btn1.resize(0, 0)
                else:
                    btn1.resize(btn1.sizeHint())
            if btn2 is not None:
                btn2.setVisible(visible)
                if not visible:
                    btn2.resize(0, 0)
                else:
                    btn2.resize(btn2.sizeHint())
            if refresh:
                self._refreshTabBar()

    def setTabsClosable(self, closable):
        """ Set the tab closable state for the widget.

        This is an overridden parent class method which extends the
        logic to account for the closable state on the individual
        pages.

        Parameters
        ----------
        closable : bool
            Whether or not the tabs should be closable.

        """
        super(QNotebook, self).setTabsClosable(closable)
        # When setting tabs closable to False, the default logic of
        # QTabBar is to delete the close button on the tab. When the
        # closable flag is set to True a new close button is created
        # for every tab, unless one has already been provided. This
        # means we need to make an extra pass over each tab to sync
        # the state of the buttons when the flag is set to True.
        if closable:
            setVisible = self.setTabCloseButtonVisible
            for index in range(self.count()):
                page = self.widget(index)
                setVisible(index, page.isClosable(), refresh=False)
        self._refreshTabBar()


#: A mapping Enaml -> Qt size hint modes.
SIZE_HINT_MODE = {
    'union': QNotebook.Union,
    'current': QNotebook.Current,
}


#: A guard flag for the tab change
CHANGE_GUARD = 0x01


class QtNotebook(QtConstraintsWidget, ProxyNotebook):
    """ A Qt implementation of an Enaml ProxyNotebook.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QNotebook)

    #: A bitfield of guard flags for the object.
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying notebook widget.

        """
        widget = QNotebook(self.parent_widget())
        if sys.platform == 'darwin':
            # On OSX, the widget item layout rect is too small.
            # Setting this attribute forces the widget item to
            # use the widget rect for layout.
            widget.setAttribute(Qt.WA_LayoutUsesWidgetRect, True)
        self.widget = widget

    def init_widget(self):
        """ Initialize the underyling widget.

        """
        super(QtNotebook, self).init_widget()
        d = self.declaration
        self.set_tab_style(d.tab_style)
        self.set_tab_position(d.tab_position)
        self.set_tabs_closable(d.tabs_closable)
        self.set_tabs_movable(d.tabs_movable)
        self.set_size_hint_mode(d.size_hint_mode, update=False)
        # the selected tab is synchronized during init_layout

    def init_layout(self):
        """ Handle the layout initialization for the notebook.

        """
        super(QtNotebook, self).init_layout()
        widget = self.widget
        for page in self.pages():
            widget.addPage(page)
        self.init_selected_tab()
        widget.layoutRequested.connect(self.on_layout_requested)
        widget.currentChanged.connect(self.on_current_changed)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def pages(self):
        """ Get the pages defined for the notebook.

        """
        for p in self.declaration.pages():
            w = p.proxy.widget
            if w is not None:
                yield w

    def find_page(self, name):
        """ Find the page with the given name.

        Parameters
        ----------
        name : unicode
            The object name for the page of interest.

        Returns
        -------
        result : QPage or None
            The target page or None if one is not found.

        """
        for page in self.pages():
            if page.objectName() == name:
                return page

    def init_selected_tab(self):
        """ Initialize the selected tab.

        This should be called only during widget initialization.

        """
        d = self.declaration
        if d.selected_tab:
            self.set_selected_tab(d.selected_tab)
        else:
            current = self.widget.currentWidget()
            name = current.objectName() if current is not None else u''
            self._guard |= CHANGE_GUARD
            try:
                d.selected_tab = name
            finally:
                self._guard &= ~CHANGE_GUARD

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtNotebook.

        """
        super(QtNotebook, self).child_added(child)
        if isinstance(child, QtPage):
            for index, dchild in enumerate(self.children()):
                if child is dchild:
                    self.widget.insertPage(index, child.widget)

    def child_removed(self, child):
        """ Handle the child removed event for a QtNotebook.

        """
        super(QtNotebook, self).child_removed(child)
        if isinstance(child, QtPage):
            self.widget.removePage(child.widget)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_layout_requested(self):
        """ Handle the `layoutRequested` signal from the QNotebook.

        """
        self.geometry_updated()

    def on_current_changed(self):
        """ Handle the 'currentChanged' signal from the QNotebook.

        """
        if not self._guard & CHANGE_GUARD:
            self._guard |= CHANGE_GUARD
            try:
                page = self.widget.currentWidget()
                name = page.objectName() if page is not None else u''
                self.declaration.selected_tab = name
            finally:
                self._guard &= ~CHANGE_GUARD

    #--------------------------------------------------------------------------
    # ProxyNotebook API
    #--------------------------------------------------------------------------
    def set_tab_style(self, style):
        """ Set the tab style for the tab bar in the widget.

        """
        self.widget.setDocumentMode(DOCUMENT_MODES[style])

    def set_tab_position(self, position):
        """ Set the position of the tab bar in the widget.

        """
        self.widget.setTabPosition(TAB_POSITIONS[position])

    def set_tabs_closable(self, closable):
        """ Set whether or not the tabs are closable.

        """
        self.widget.setTabsClosable(closable)

    def set_tabs_movable(self, movable):
        """ Set whether or not the tabs are movable.

        """
        self.widget.setMovable(movable)

    def set_selected_tab(self, name):
        """ Set the selected tab of the widget.

        """
        if not self._guard & CHANGE_GUARD:
            page = self.find_page(name)
            if page is None:
                import warnings
                msg = "cannot select tab '%s' - tab not found"
                warnings.warn(msg % name, UserWarning)
                return
            self._guard |= CHANGE_GUARD
            try:
                self.widget.setCurrentWidget(page)
            finally:
                self._guard &= ~CHANGE_GUARD

    def set_size_hint_mode(self, mode, update=True):
        """ Set the size hint mode for the widget.

        """
        self.widget.setSizeHintMode(SIZE_HINT_MODE[mode])
        if update:
            self.geometry_updated()
