#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.mdi_area import ProxyMdiArea

from .QtWidgets import QMdiArea

from .qt_constraints_widget import QtConstraintsWidget
from .qt_mdi_window import QtMdiWindow


class QtMdiArea(QtConstraintsWidget, ProxyMdiArea):
    """ A Qt implementation of an Enaml ProxyMdiArea.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QMdiArea)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QMdiArea widget.

        """
        self.widget = QMdiArea(self.parent_widget())

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(QtMdiArea, self).init_layout()
        widget = self.widget
        for window in self.mdi_windows():
            widget.addSubWindow(window)
        widget.subWindowActivated.connect(self.on_subwindow_activated)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def mdi_windows(self):
        """ Get the mdi windows defined for the area.

        """
        for window in self.declaration.mdi_windows():
            widget = window.proxy.widget
            if widget:
                yield widget

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_subwindow_activated(self, window):
        """ The handler for the 'subWindowActivated' signal.

        """
        # On OSX there is painting bug where a subwindow is not repainted
        # properly when it is activated. This handler ensures an update.
        if window:
            window.update()

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtMdiArea.

        """
        # The size hint of a QMdiArea is typically quite large and the
        # size hint constraints are usually ignored. There is no need
        # to notify of a change in size hint here.
        super(QtMdiArea, self).child_added(child)
        if isinstance(child, QtMdiWindow):
            self.widget.addSubWindow(child.widget)

    def child_removed(self, child):
        """ Handle the child removed event for a QtMdiArea.

        """
        if isinstance(child, QtMdiWindow):
            self.widget.removeSubWindow(child.widget)
        else:
            super(QtMdiArea, self).child_removed(child)
