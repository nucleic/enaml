#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.mdi_window import ProxyMdiWindow

from .QtGui import QIcon
from .QtWidgets import QMdiSubWindow, QLayout

from .q_resource_helpers import get_cached_qicon
from .qt_widget import QtWidget


class QtMdiWindow(QtWidget, ProxyMdiWindow):
    """ A Qt implementation of an Enaml ProxyMdiWindow.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QMdiSubWindow)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QMdiSubWindow widget.

        """
        # We don't parent the subwindow immediately. It will be added
        # explicitly by the parent QMdiArea during its layout pass.
        # If we set the parent here, Qt will spit out warnings when
        # it's set added to the area later on. We *could* parent it
        # here, and simply not add it explicitly to the mdi area, but
        # this way is more explicit and consistent with the rest of
        # the framework.
        widget = QMdiSubWindow()
        widget.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.widget = widget

    def init_widget(self):
        """ Initialize the widget.

        """
        super(QtMdiWindow, self).init_widget()
        d = self.declaration
        if d.title:
            self.set_title(d.title)
        if d.icon:
            self.set_icon(d.icon)

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(QtMdiWindow, self).init_layout()
        self._set_window_widget(self.mdi_widget())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def mdi_widget(self):
        """ Find and return the mdi widget child for this widget.

        """
        w = self.declaration.mdi_widget()
        if w:
            return w.proxy.widget

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtMdiWindow.

        """
        super(QtMdiWindow, self).child_added(child)
        if isinstance(child, QtWidget):
            self._set_window_widget(self.mdi_widget())

    def child_removed(self, child):
        """ Handle the child removed event for a QtMdiWindow.

        """
        super(QtMdiWindow, self).child_added(child)
        if isinstance(child, QtWidget):
            self._set_window_widget(self.mdi_widget())

    #--------------------------------------------------------------------------
    # ProxyMdiWindow API
    #--------------------------------------------------------------------------
    def set_icon(self, icon):
        """ Set the mdi window icon.

        """
        if icon:
            qicon = get_cached_qicon(icon)
        else:
            qicon = QIcon()
        self.widget.setWindowIcon(qicon)

    def set_title(self, title):
        """ Set the title of the mdi window.

        """
        self.widget.setWindowTitle(title)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _set_window_widget(self, mdi_widget):
        """ A private method which set the child widget on the window.

        Parameters
        ----------
        mdi_widget : QWidget
            The child widget to use in the mdi window.

        """
        # We need to first set the window widget to None, or Qt will
        # complain if a widget is already set on the window.
        widget = self.widget
        widget.setWidget(None)
        if mdi_widget is None:
            return
        # We need to unparent the underlying widget before adding
        # it to the subwindow. Otherwise, children like QMainWindow
        # will persist as top-level non-mdi widgets.
        mdi_widget.setParent(None)
        widget.setWidget(mdi_widget)
        # On OSX, the resize gripper will be obscured unless we
        # lower the widget in the window's stacking order.
        mdi_widget.lower()
