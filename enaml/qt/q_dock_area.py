#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import QMargins, QSize
from PyQt4.QtGui import QFrame, QLayout


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
        self._layout_widget = None

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def layoutWidget(self):
        """ Get the widget implementing the layout for the area.

        Returns
        -------
        result : QWidget or None
            The widget implementing the area, or None if no widget is
            installed.

        """
        return self._layout_widget

    def setLayoutWidget(self, widget):
        """ Set the layout widget for the dock area.

        This method is called by the dock manager which handles the
        dock area. It should not normally be called by user code.

        Parameters
        ----------
        widget : QWidget
            The widget which implements the dock area layout.

        """
        old_widget = self._layout_widget
        if old_widget is not None:
            old_widget.hide()
            old_widget.setParent(None)
        self._layout_widget = widget
        area = self.parentWidget()
        if widget is not None:
            widget.setParent(area)
            if not area.isHidden():
                widget.show()

    def setGeometry(self, rect):
        """ Sets the geometry of all the items in the layout.

        """
        super(QDockAreaLayout, self).setGeometry(rect)
        widget = self._layout_widget
        if widget is not None:
            widget.setGeometry(self.contentsRect())

    def sizeHint(self):
        """ Get the size hint for the layout.

        """
        widget = self._layout_widget
        if widget is not None:
            return widget.sizeHint()
        return QSize(256, 192)

    def minimumSize(self):
        """ Get the minimum size of the layout.

        """
        widget = self._layout_widget
        if widget is not None:
            return widget.minimumSizeHint()
        return QSize(256, 192)

    def maximumSize(self):
        """ Get the maximum size for the layout.

        """
        widget = self._layout_widget
        if widget is not None:
            return widget.maximumSize()
        return QSize(16777215, 16777215)

    #--------------------------------------------------------------------------
    # QLayout Abstract API
    #--------------------------------------------------------------------------
    def addItem(self, item):
        """ A required virtual method implementation.

        This method should not be used. Use `setDockLayout` instead.

        """
        msg = 'Use `setDockLayout` instead.'
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
    """ A custom QFrame which provides an area for docking QDockItems.

    A dock area is used by creating QDockItem instances using the dock
    area as the parent. A DockLayout instance can then be created and
    applied to the dock area with the 'setDockLayout' method. The names
    in the DockLayoutItem objects are used to find the matching dock
    item widget child.

    """
    def __init__(self, parent=None):
        """ Initialize a QDockArea.

        Parameters
        ----------
        parent : QWidget
            The parent of the dock area.

        """
        super(QDockArea, self).__init__(parent)
        layout = QDockAreaLayout()
        layout.setContentsMargins(QMargins(0, 0, 0, 0))
        layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.setLayout(layout)

        # FIXME temporary VS2010-like stylesheet
        from PyQt4.QtGui import QApplication
        QApplication.instance().setStyleSheet("""
            QDockArea {
                padding: 5px;
                background: rgb(41, 56, 85);
            }
            QDockItem {
                background: rgb(237, 237, 237);
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                border-bottom-left-radius: 2px;
                border-bottom-right-radius: 2px;
            }
            QDockItemTitleBar[p_titlePosition="2"] {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 rgb(78, 97, 132),
                            stop:0.5 rgb(66, 88, 124),
                            stop:1.0 rgb(64, 81, 124));
                color: rgb(250, 251, 254);
                border-top: 1px solid rgb(59, 80, 115);
            }
            QDockArea QDockItemTitleBar[p_titlePosition="2"] {
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }
            QSplitterHandle {
                background: rgb(41, 56, 85);
            }
            QDockContainer {
                background: rgb(41, 56, 85);
            }
            """)
