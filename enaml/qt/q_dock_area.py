#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtGui import QFrame, QLayout

from .q_dock_area_layout import QDockAreaLayout


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
        self.setLayout(QDockAreaLayout())
        self.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)

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

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def dockLayout(self):
        """ Get the dock layout for the dock area.

        Returns
        -------
        result : DockLayoutBase or None
            The dock layout for the dock area, or None.

        """
        return self.layout().dockLayout()

    def setDockLayout(self, layout):
        """ Set the dock layout for the dock area.

        The old layout will be unparented and hidden, but not destroyed.

        Parameters
        ----------
        layout : DockLayoutBase
            The dock layout node to use for the dock area.

        """
        self.layout().setDockLayout(layout)
