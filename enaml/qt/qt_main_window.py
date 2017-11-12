#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys

from atom.api import Typed, atomref

from enaml.widgets.main_window import ProxyMainWindow
from enaml.widgets.window import CloseEvent

from .QtCore import Qt
from .QtWidgets import QMainWindow

from .q_deferred_caller import deferredCall
from .qt_container import QtContainer
from .qt_dock_pane import QtDockPane
from .qt_menu_bar import QtMenuBar
from .qt_status_bar import QtStatusBar
from .qt_tool_bar import QtToolBar
from .qt_window import QtWindow, finalize_close


class QCustomMainWindow(QMainWindow):
    """ A custom QMainWindow which adds some Enaml specific features.

    """
    def __init__(self, proxy, parent=None, flags=Qt.Widget):
        """ Initialize a QCustomMainWindow.

        Parameters
        ----------
        proxy : QtMainWindow
            The proxy object which owns this window. Only an atomref
            will be maintained to this object.

        parent : QWidget, optional
            The parent of the window.

        flags : Qt.WindowFlags, optional
            The window flags to pass to the parent constructor.

        """
        super(QCustomMainWindow, self).__init__(parent, Qt.Window | flags)
        self._proxy_ref = atomref(proxy)

    def closeEvent(self, event):
        """ Handle the close event for the window.

        """
        event.accept()
        if not self._proxy_ref:
            return
        proxy = self._proxy_ref()
        d = proxy.declaration
        d_event = CloseEvent()
        d.closing(d_event)
        if d_event.is_accepted():
            deferredCall(finalize_close, d)
        else:
            event.ignore()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def setDockWidgetArea(self, area, dock_widget):
        """ Set the dock area for the given dock widget.

        If the dock widget has not been added to the main window, this
        method is a no-op.

        Parameters
        ----------
        area : QDockWidgetArea
            The dock area to use for the widget.

        dock_widget : QDockWidget
            The dock widget to move to the given area.

        """
        curr = self.dockWidgetArea(dock_widget)
        if curr != Qt.NoDockWidgetArea:
            if curr != area:
                visible = dock_widget.isVisible()
                self.removeDockWidget(dock_widget)
                self.addDockWidget(area, dock_widget)
                dock_widget.setVisible(visible)

    def setToolBarArea(self, area, tool_bar):
        """ Set the tool bar area for the given tool bar.

        If the tool bar has not been added to the main window, this
        method is a no-op.

        Parameters
        ----------
        area : QToolBarArea
            The tool bar area to use for the widget.

        tool_bar : QToolBar
            The tool bar to move to the given area.

        """
        curr = self.toolBarArea(tool_bar)
        if curr != Qt.NoToolBarArea:
            if curr != area:
                visible = tool_bar.isVisible()
                floating = tool_bar.isFloating()
                tool_bar.setVisible(False)
                self.removeToolBar(tool_bar)
                self.addToolBar(area, tool_bar)
                tool_bar.resize(tool_bar.sizeHint())
                tool_bar.setFloating(floating)
                tool_bar.setVisible(visible)


class QtMainWindow(QtWindow, ProxyMainWindow):
    """ A Qt implementation of an Enaml MainWindow.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QCustomMainWindow)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying widget QMainWindow widget.

        """
        flags = self.creation_flags()
        widget = QCustomMainWindow(self, self.parent_widget(), flags)
        widget.setDocumentMode(True)
        widget.setDockNestingEnabled(True)
        self.widget = widget

    def init_layout(self):
        """ Initialize the layout for the underlying widget.

        """
        # The superclass' init_layout() method is explicitly not called
        # since the layout initialization for Window is not appropriate
        # for MainWindow.
        widget = self.widget
        widget.setMenuBar(self.menu_bar())
        widget.setCentralWidget(self.central_widget())
        widget.setStatusBar(self.status_bar())
        for d in self.dock_panes():
            widget.addDockWidget(d.dockArea(), d)
        for d in self.tool_bars():
            # XXX slight hack. When adding the toolbar to the main
            # window, it is forcibly unfloated. In order for the
            # initial floating state to be maintained, it must be
            # re-floating after being added. We do the refloating
            # in the future, so that the main window shows up first.
            floating = d.isFloating()
            widget.addToolBar(d.toolBarArea(), d)
            if floating:
                deferredCall(d.setFloating, True)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def menu_bar(self):
        """ Get the QMenuBar widget defined for the main window.

        """
        d = self.declaration.menu_bar()
        if d is not None:
            return d.proxy.widget

    def dock_panes(self):
        """ Get the QDockWidget widgets defined for the main window.

        """
        for d in self.declaration.dock_panes():
            w = d.proxy.widget
            if w is not None:
                yield w

    def status_bar(self):
        """ Get the status bar widget defined for the main window.

        """
        d = self.declaration.status_bar()
        if d is not None:
            return d.proxy.widget

    def tool_bars(self):
        """ Get the QToolBar widgets defined for the main window.

        """
        for d in self.declaration.tool_bars():
            w = d.proxy.widget
            if w is not None:
                yield w

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtMainWindow.

        """
        if isinstance(child, QtMenuBar):
            self.widget.setMenuBar(self.menu_bar())
        elif isinstance(child, QtContainer):
            self.widget.setCentralWidget(self.central_widget())
        elif isinstance(child, QtDockPane):
            dock_widget = child.widget
            self.widget.addDockWidget(dock_widget.dockArea(), dock_widget)
        elif isinstance(child, QtStatusBar):
            # FIXME Qt will delete the old status bar
            self.widget.setStatusBar(self.status_bar())
        elif isinstance(child, QtToolBar):
            # There are two hacks involved in adding a tool bar. The
            # first is the same hack that is perfomed in the layout
            # method for a floating tool bar. The second is specific
            # to OSX. On that platform, adding a tool bar to main
            # window which is already visible but does not have any
            # current tool bars will cause the main window to be hidden.
            # This will only occur the *first* time a tool bar is added
            # to the window. The hack below is workaround which should
            # be sufficient for most use cases. A bug should really be
            # filed against Qt for this one, since it's reproducible
            # outside of Enaml.
            bar_widget = child.widget
            floating = bar_widget.isFloating()
            self.widget.addToolBar(bar_widget.toolBarArea(), bar_widget)
            if floating:
                deferredCall(bar_widget.setFloating, True)
            if sys.platform == 'darwin':
                self.widget.setVisible(True)
        else:
            super(QtMainWindow, self).child_added(child)

    def child_removed(self, child):
        """ Handle the child removed event for a QtMainWindow.

        """
        if isinstance(child, QtDockPane) and child.widget is not None:
            self.widget.removeDockWidget(child.widget)
        elif isinstance(child, QtToolBar) and child.widget is not None:
            self.widget.removeToolBar(child.widget)
        elif isinstance(child, QtContainer):
            self.widget.setCentralWidget(self.central_widget())
        elif isinstance(child, QtMenuBar):
            self.widget.setMenuBar(self.menu_bar())
        elif isinstance(child, QtStatusBar):
            # FIXME Qt will delete the old status bar
            self.widget.setStatusBar(self.status_bar())
        else:
            super(QtMainWindow, self).child_removed(child)
