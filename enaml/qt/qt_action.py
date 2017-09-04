#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int, Typed

from enaml.widgets.action import ProxyAction

from .QtGui import QIcon, QKeySequence
from .QtWidgets import QAction

from .q_resource_helpers import get_cached_qicon
from .qt_toolkit_object import QtToolkitObject


# cyclic notification guard flags
CHECKED_GUARD = 0x1


class QtAction(QtToolkitObject, ProxyAction):
    """ A Qt implementation of an Enaml ProxyAction.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QAction)

    #: Cyclic notification guard. This a bitfield of multiple guards.
    _guard = Int(0)

    # FIXME Currently, the checked state of the action is lost when
    # switching from checkable to non-checkable and back again.
    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QAction object.

        """
        self.widget = QAction(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying control.

        """
        super(QtAction, self).init_widget()
        d = self.declaration
        if d.text:
            self.set_text(d.text)
        if d.tool_tip:
            self.set_tool_tip(d.tool_tip)
        if d.status_tip:
            self.set_status_tip(d.status_tip)
        if d.icon:
            self.set_icon(d.icon)
        self.set_checkable(d.checkable)
        self.set_checked(d.checked)
        self.set_enabled(d.enabled)
        self.set_visible(d.visible)
        self.set_separator(d.separator)
        widget = self.widget
        widget.triggered.connect(self.on_triggered)
        widget.toggled.connect(self.on_toggled)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_triggered(self):
        """ The signal handler for the 'triggered' signal.

        """
        # PySide does pass the 'checked' arg to the slot like PyQt, so
        # grab the checked attribute directly, which works on both.
        checked = self.widget.isChecked()
        if not self._guard & CHECKED_GUARD:
            self.declaration.checked = checked
            self.declaration.triggered(checked)

    def on_toggled(self, checked):
        """ The signal handler for the 'toggled' signal.

        """
        if not self._guard & CHECKED_GUARD:
            self.declaration.checked = checked
            self.declaration.toggled(checked)

    #--------------------------------------------------------------------------
    # ProxyAction API
    #--------------------------------------------------------------------------
    def set_text(self, text):
        """ Set the text on the underlying control.

        """
        widget = self.widget
        widget.setText(text)
        parts = text.split('\t')
        if len(parts) > 1:
            shortcut = QKeySequence(parts[-1])
            widget.setShortcut(shortcut)

    def set_tool_tip(self, tool_tip):
        """ Set the tool tip on the underlying control.

        """
        self.widget.setToolTip(tool_tip)

    def set_status_tip(self, status_tip):
        """ Set the status tip on the underyling control.

        """
        self.widget.setStatusTip(status_tip)

    def set_icon(self, icon):
        """ Set the icon for the action.

        """
        if icon:
            qicon = get_cached_qicon(icon)
        else:
            qicon = QIcon()
        self.widget.setIcon(qicon)

    def set_checkable(self, checkable):
        """ Set the checkable state on the underlying control.

        """
        self.widget.setCheckable(checkable)

    def set_checked(self, checked):
        """ Set the checked state on the underlying control.

        """
        self._guard |= CHECKED_GUARD
        try:
            self.widget.setChecked(checked)
        finally:
            self._guard &= ~CHECKED_GUARD

    def set_enabled(self, enabled):
        """ Set the enabled state on the underlying control.

        """
        self.widget.setEnabled(enabled)

    def set_visible(self, visible):
        """ Set the visible state on the underlying control.

        """
        self.widget.setVisible(visible)

    def set_separator(self, separator):
        """ Set the separator state on the underlying control.

        """
        self.widget.setSeparator(separator)
