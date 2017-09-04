#------------------------------------------------------------------------------
# Copyright (c) 2014-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.tool_button import ProxyToolButton

from .QtCore import Qt
from .QtWidgets import QToolButton, QToolBar, QSizePolicy

from .qt_abstract_button import QtAbstractButton
from .qt_menu import QtMenu


#: A mapping of Enaml popup modes to Qt ToolButtonPopupMode
POPUP_MODES = {
    'button': QToolButton.MenuButtonPopup,
    'instant': QToolButton.InstantPopup,
    'delayed': QToolButton.DelayedPopup,
}


#: A mapping from Enaml button style to Qt ToolButtonStyle
BUTTON_STYLES = {
    'icon_only': Qt.ToolButtonIconOnly,
    'text_only': Qt.ToolButtonTextOnly,
    'text_beside_icon': Qt.ToolButtonTextBesideIcon,
    'text_under_icon': Qt.ToolButtonTextUnderIcon,
}


class QtToolButton(QtAbstractButton, ProxyToolButton):
    """ A Qt implementation of an Enaml ProxyToolButton.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QToolButton)

    def create_widget(self):
        """ Create the underlying widget.

        """
        parent = self.parent_widget()
        widget = QToolButton(parent)
        if not isinstance(parent, QToolBar):
            sp = widget.sizePolicy()
            sp.setHorizontalPolicy(QSizePolicy.Minimum)
            widget.setSizePolicy(sp)
        self.widget = widget

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtToolButton, self).init_widget()
        d = self.declaration
        self.set_button_style(d.button_style)
        self.set_auto_raise(d.auto_raise)
        self.set_popup_mode(d.popup_mode)

    def init_layout(self):
        """ Initialize the widget layout.

        """
        super(QtToolButton, self).init_layout()
        for child in self.children():
            if isinstance(child, QtMenu):
                self.widget.setMenu(child.widget)
                break

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for the tool button.

        """
        super(QtToolButton, self).child_added(child)
        if isinstance(child, QtMenu):
            self.widget.setMenu(child.widget)

    def child_removed(self, child):
        """ Handle the child removed event for the tool button.

        """
        super(QtToolButton, self).child_removed(child)
        if isinstance(child, QtMenu):
            if child.widget is self.widget.menu():
                self.widget.setMenu(None)

    #--------------------------------------------------------------------------
    # ProxyToolButton API
    #--------------------------------------------------------------------------
    def set_button_style(self, style):
        """ Set the button style of the widget.

        """
        with self.geometry_guard():
            self.widget.setToolButtonStyle(BUTTON_STYLES[style])

    def set_auto_raise(self, auto):
        """ Set the auto-raise flag on the widget.

        """
        with self.geometry_guard():
            self.widget.setAutoRaise(auto)

    def set_popup_mode(self, mode):
        """ Set the popup mode for the widget menu.

        """
        widget = self.widget
        q_mode = POPUP_MODES[mode]
        if q_mode == widget.popupMode():
            return
        with self.geometry_guard():
            widget.setPopupMode(q_mode)
            widget.setIcon(widget.icon())  # force-resets the internal cache
