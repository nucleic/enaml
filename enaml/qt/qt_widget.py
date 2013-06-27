#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys

from atom.api import Typed

from enaml.widgets.widget import ProxyWidget

from .QtCore import Qt, QSize
from .QtGui import QFont, QWidget, QWidgetItem, QApplication

from .q_resource_helpers import get_cached_qcolor, get_cached_qfont
from .qt_toolkit_object import QtToolkitObject


class QtWidget(QtToolkitObject, ProxyWidget):
    """ A Qt implementation of an Enaml ProxyWidget.

    """
    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(QWidget)

    #: A QWidgetItem created on-demand for the widget. This is used by
    #: the layout engine to compute correct size hints for the widget.
    widget_item = Typed(QWidgetItem)

    def _default_widget_item(self):
        return QWidgetItem(self.widget)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QWidget object.

        """
        self.widget = QWidget(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying QWidget object.

        """
        super(QtWidget, self).init_widget()
        d = self.declaration
        if d.background:
            self.set_background(d.background)
        if d.foreground:
            self.set_foreground(d.foreground)
        if d.font:
            self.set_font(d.font)
        if d.show_focus_rect is not None:
            self.set_show_focus_rect(d.show_focus_rect)
        if -1 not in d.minimum_size:
            self.set_minimum_size(d.minimum_size)
        if -1 not in d.maximum_size:
            self.set_maximum_size(d.maximum_size)
        if d.tool_tip:
            self.set_tool_tip(d.tool_tip)
        if d.status_tip:
            self.set_status_tip(d.status_tip)
        self.set_enabled(d.enabled)
        # Don't make toplevel widgets visible during init or they will
        # flicker onto the screen. This applies particularly for things
        # like status bar widgets which are created with no parent and
        # then reparented by the status bar. Real top-level widgets must
        # be explicitly shown by calling their .show() method after they
        # are created.
        if self.widget.parent() or not d.visible:
            self.set_visible(d.visible)

    #--------------------------------------------------------------------------
    # ProxyWidget API
    #--------------------------------------------------------------------------
    def set_minimum_size(self, min_size):
        """ Sets the minimum size of the widget.

        """
        # QWidget uses (0, 0) as the minimum size.
        if -1 in min_size:
            min_size = (0, 0)
        self.widget.setMinimumSize(QSize(*min_size))

    def set_maximum_size(self, max_size):
        """ Sets the maximum size of the widget.

        """
        # QWidget uses 16777215 as the max size
        if -1 in max_size:
            max_size = (16777215, 16777215)
        self.widget.setMaximumSize(QSize(*max_size))

    def set_enabled(self, enabled):
        """ Set the enabled state of the widget.

        """
        self.widget.setEnabled(enabled)

    def set_visible(self, visible):
        """ Set the visibility of the widget.

        """
        self.widget.setVisible(visible)

    def set_background(self, background):
        """ Set the background color of the widget.

        """
        widget = self.widget
        role = widget.backgroundRole()
        if background is not None:
            qcolor = get_cached_qcolor(background)
            widget.setAutoFillBackground(True)
        else:
            app_palette = QApplication.instance().palette(widget)
            qcolor = app_palette.color(role)
            widget.setAutoFillBackground(False)
        palette = widget.palette()
        palette.setColor(role, qcolor)
        widget.setPalette(palette)

    def set_foreground(self, foreground):
        """ Set the foreground color of the widget.

        """
        widget = self.widget
        role = widget.foregroundRole()
        if foreground is not None:
            qcolor = get_cached_qcolor(foreground)
        else:
            app_palette = QApplication.instance().palette(widget)
            qcolor = app_palette.color(role)
        palette = widget.palette()
        palette.setColor(role, qcolor)
        widget.setPalette(palette)

    def set_font(self, font):
        """ Set the font of the widget.

        """
        widget = self.widget
        if font is not None:
            widget.setFont(get_cached_qfont(font))
        else:
            widget.setFont(QFont())

    def set_show_focus_rect(self, show):
        """ Set whether or not to show the focus rect.

        This is currently only supported on OSX.

        """
        if sys.platform == 'darwin':
            self.widget.setAttribute(Qt.WA_MacShowFocusRect, bool(show))

    def set_tool_tip(self, tool_tip):
        """ Set the tool tip for the widget.

        """
        self.widget.setToolTip(tool_tip)

    def set_status_tip(self, status_tip):
        """ Set the status tip for the widget.

        """
        self.widget.setStatusTip(status_tip)

    def ensure_visible(self):
        """ Ensure the widget is visible.

        """
        self.widget.setVisible(True)

    def ensure_hidden(self):
        """ Ensure the widget is hidden.

        """
        self.widget.setVisible(False)
