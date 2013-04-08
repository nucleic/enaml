#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QSize, pyqtSignal, QEvent
from PyQt4.QtGui import QFrame, QLayout, QSplitter, QTabWidget

from atom.api import Atom, List, Enum, ForwardTyped, Typed

from .q_dock_item import QDockItem


class DockLayout(Atom):
    """ A base class for the dock layout classes.

    """
    #: A reference to the parent node for the item.
    parent = ForwardTyped(lambda: DockLayout)

    def widget(self):
        """ Get the widget associated with the layout.

        """
        raise NotImplementedError

    def layout(self):
        """ Rebuild the widget layout for the layout.

        """
        raise NotImplementedError

    def parentWidget(self):
        """ Get the parent widget for the layout.

        """
        parent = self.parent
        if parent is not None:
            return parent.widget()

    def setGeometry(self, rect):
        """ Set the geometry for the layout.

        """
        widget = self.widget()
        if widget is not None:
            widget.setGeometry(rect)

    def sizeHint(self):
        """ Compute the size hint for the layout item.

        """
        widget = self.widget()
        if widget is not None:
            return widget.sizeHint()
        return QSize(0, 0)

    def minimumSize(self):
        """ Compute the minimum size of the layout item.

        """
        widget = self.widget()
        if widget is not None:
            return widget.minimumSizeHint()
        return QSize(0, 0)


class DockItem(DockLayout):
    """ A dock layout which manages a single QDockItem.

    """
    item = Typed(QDockItem)

    def widget(self):
        """ Get the widget associated with the layout.

        """
        return self.item

    def layout(self):
        """ Rebuild the layout for the item.

        """
        # Nothing to do for a plain dock item.
        pass


class DockSplitter(DockLayout):
    """ A dock layout which arranges its items in a splitter.

    """
    #: The orientation of the dock splitter
    orientation = Enum(Qt.Vertical, Qt.Horizontal)

    #: The list of dock layouts managed by the splitter.
    items = List(DockLayout)

    sizes = List(int)

    #: The QSplitter widget used to implement the layout.
    splitter = Typed(QSplitter)

    def widget(self):
        """ Get the widget associated with the layout.

        """
        splitter = self.splitter
        if splitter is None:
            parent = self.parentWidget()
            splitter = self.splitter = QSplitter(self.orientation, parent)
        return splitter

    def layout(self):
        """ Rebuild the layout for the dock splitter.

        """
        old = self.splitter
        if old is not None:
            old.setParent(None)
            del self.splitter
        splitter = self.widget()
        for item in self.items:
            item.layout()
            splitter.addWidget(item.widget())


class DockTabs(DockLayout):
    """ A dock layout which arranges its items in a tabbed container.

    """
    #: The list of dock items managed by the layout.
    items = List(DockItem)

    #: The tab widget used to implement the layout.
    tabs = Typed(QTabWidget)

    def widget(self):
        """ Create the QSplitter widget for the layout.

        """
        tabs = self.tabs
        if tabs is None:
            parent = self.parentWidget()
            tabs = self.tabs = QTabWidget(parent)
            tabs.setDocumentMode(True)
        return tabs

    def layout(self):
        """ Rebuild the layout for the dock tabs.

        """
        old = self.tabs
        if old is not None:
            old.setParent(None)
            del self.tabs
        tabs = self.widget()
        for item in self.items:
            item.widget().titleBarWidget().setVisible(False)
            tabs.addTab(item.widget(), item.widget().title())


class QDockAreaLayout(QLayout):
    """ A custom QLayout which is part of the dock area implementation.

    """
    def __init__(self, parent=None):
        """ Initialize a QDockAreaLayout.

        Parameters
        ----------
        parent : QWidget or None
            The parent of the layout.

        """
        super(QDockAreaLayout, self).__init__(parent)
        self._layout = None

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def setDockLayout(self, layout):
        self._layout = layout
        self._layout.layout()
        self._layout.widget().setParent(self.parentWidget())

    def setGeometry(self, rect):
        """ Sets the geometry of all the items in the layout.

        """
        super(QDockAreaLayout, self).setGeometry(rect)
        layout = self._layout
        if layout is not None:
            layout.setGeometry(rect)

    def sizeHint(self):
        """ Get the size hint for the layout.

        """
        layout = self._layout
        if layout is not None:
            return layout.sizeHint()
        return QSize(256, 192)

    def minimumSize(self):
        """ Get the minimum size of the layout.

        """
        layout = self._layout
        if layout is not None:
            return layout.minimumSize()
        return QSize(256, 192)

    #--------------------------------------------------------------------------
    # QLayout Abstract API
    #--------------------------------------------------------------------------
    def addItem(self, item):
        """ A required virtual method implementation.

        This method should not be used. Use `setDockLayoutItem` instead.

        """
        msg = 'Use `setDockLayoutItem` instead.'
        raise NotImplementedError(msg)

    def count(self):
        """ A required virtual method implementation.

        This method should not be used and returns a constant value.

        """
        return 0

    def itemAt(self, idx):
        """ A virtual method implementation which returns None.

        """
        return None

    def takeAt(self, idx):
        """ A virtual method implementation which does nothing.

        """
        return None


class QDockArea(QFrame):

    def __init__(self, parent=None):
        super(QDockArea, self).__init__(parent)
        self.setLayout(QDockAreaLayout())
        self.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
        # FIXME temporary VS2010-like stylesheet
        self.setStyleSheet("""
            QDockArea {
                padding: 5px;
                background: rgb(41, 56, 85);
            }
            QDockItem {
                background: rgb(237, 237, 237);
                border-bottom-left-radius: 2px;
                border-bottom-right-radius: 2px;
            }
            QSplitter > QDockItem {
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QDockTitleBar[p_titlePosition="2"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgb(78, 97, 132),
                            stop:0.5 rgb(66, 88, 124),
                            stop:1.0 rgb(64, 81, 124));
                color: rgb(250, 251, 254);
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
                border-top: 1px solid rgb(59, 80, 115);
            }
            """)
