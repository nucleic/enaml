#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys

from atom.api import Typed, Coerced, Value

from enaml.styling import StyleCache
from enaml.widgets.widget import Feature, ProxyWidget

from .QtCore import Qt, QSize
from .QtGui import QFont, QWidget, QApplication

from .q_resource_helpers import get_cached_qcolor, get_cached_qfont
from .qt_toolkit_object import QtToolkitObject
from .styleutil import translate_style


#: A mapping of Enaml focus policies -> Qt focus policies.
FOCUS_POLICIES = {
    'tab_focus': Qt.TabFocus,
    'click_focus': Qt.ClickFocus,
    'strong_focus': Qt.StrongFocus,
    'wheel_focus': Qt.WheelFocus,
    'no_focus': Qt.NoFocus,
}


class QtWidget(QtToolkitObject, ProxyWidget):
    """ A Qt implementation of an Enaml ProxyWidget.

    """
    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(QWidget)

    #: A private copy of the declaration features. This ensures that
    #: feature cleanup will proceed correctly in the event that user
    #: code modifies the declaration features value at runtime.
    _features = Coerced(Feature.Flags)

    #: An internal cache of the widget's default focus policy.
    _default_focus_policy = Value()

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
        self._install_features()
        d = self.declaration
        if d.background:
            self.set_background(d.background)
        if d.foreground:
            self.set_foreground(d.foreground)
        if d.font:
            self.set_font(d.font)
        if d.show_focus_rect is not None:
            self.set_show_focus_rect(d.show_focus_rect)
        if d.focus_policy != 'default':
            self.set_focus_policy(d.focus_policy)
        if -1 not in d.minimum_size:
            self.set_minimum_size(d.minimum_size)
        if -1 not in d.maximum_size:
            self.set_maximum_size(d.maximum_size)
        if d.tool_tip:
            self.set_tool_tip(d.tool_tip)
        if d.status_tip:
            self.set_status_tip(d.status_tip)
        self.set_enabled(d.enabled)
        self.refresh_style_sheet()
        # Don't make toplevel widgets visible during init or they will
        # flicker onto the screen. This applies particularly for things
        # like status bar widgets which are created with no parent and
        # then reparented by the status bar. Real top-level widgets must
        # be explicitly shown by calling their .show() method after they
        # are created.
        if self.widget.parent() or not d.visible:
            self.set_visible(d.visible)

    def destroy(self):
        """ Destroy the underlying QWidget object.

        """
        self._remove_features()
        super(QtWidget, self).destroy()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _install_features(self):
        """ Install the advanced widget feature handlers.

        """
        features = self._features = self.declaration.features
        if not features:
            return
        widget = self.widget
        if features & Feature.FocusTraversal:
            widget.focusNextPrevChild = self._focusNextPrevChild
        if features & Feature.FocusEvents:
            widget.focusInEvent = self._focusInEvent
            widget.focusOutEvent = self._focusOutEvent

    def _remove_features(self):
        """ Remove the advanced widget feature handlers.

        """
        features = self._features
        if not features:
            return
        widget = self.widget
        if features & Feature.FocusTraversal:
            del widget.focusNextPrevChild
        if features & Feature.FocusEvents:
            del widget.focusInEvent
            del widget.focusOutEvent

    def _focusNextPrevChild(self, next_child):
        """ The duck-punched 'focusNextPrevChild' implementation.

        """
        fw = QApplication.focusWidget()
        fp = fw and getattr(fw, '_d_proxy', None)
        fd = fp and fp.declaration
        if next_child:
            child = self.declaration.next_focus_child(fd)
            reason = Qt.TabFocusReason
        else:
            child = self.declaration.previous_focus_child(fd)
            reason = Qt.BacktabFocusReason
        if child is not None and child.proxy_is_active:
            cw = child.proxy.widget
            if cw.focusPolicy() & Qt.TabFocus:
                cw.setFocus(reason)
                return True
        widget = self.widget
        return type(widget).focusNextPrevChild(widget, next_child)

    def _focusInEvent(self, event):
        """ The duck-punched 'focusInEvent' implementation.

        """
        widget = self.widget
        type(widget).focusInEvent(widget, event)
        self.declaration.focus_gained()

    def _focusOutEvent(self, event):
        """ The duck-punched 'focusOutEvent' implementation.

        """
        widget = self.widget
        type(widget).focusOutEvent(widget, event)
        self.declaration.focus_lost()

    #--------------------------------------------------------------------------
    # Protected API
    #--------------------------------------------------------------------------
    def refresh_style_sheet(self):
        """ Refresh the widget style sheet with the current style data.

        """
        parts = []
        name = self.widget.objectName()
        for style in StyleCache.styles(self.declaration):
            t = translate_style(name, style)
            if t:
                parts.append(t)
        if len(parts) > 0:
            stylesheet = u'\n\n'.join(parts)
        else:
            stylesheet = u''
        self.widget.setStyleSheet(stylesheet)

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
        if font is not None:
            self.widget.setFont(get_cached_qfont(font))
        else:
            self.widget.setFont(QFont())

    def set_show_focus_rect(self, show):
        """ Set whether or not to show the focus rect.

        This is currently only supported on OSX.

        """
        if sys.platform == 'darwin':
            self.widget.setAttribute(Qt.WA_MacShowFocusRect, bool(show))

    def set_focus_policy(self, policy):
        """ Set the focus policy of the widget.

        """
        widget = self.widget
        if self._default_focus_policy is None:
            self._default_focus_policy = widget.focusPolicy()
        if policy == 'default':
            q_policy = self._default_focus_policy
        else:
            q_policy = FOCUS_POLICIES[policy]
        widget.setFocusPolicy(q_policy)

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

    def restyle(self):
        """ Restyle the widget with the current style data.

        """
        self.refresh_style_sheet()

    def set_focus(self):
        """ Set the keyboard input focus to this widget.

        """
        self.widget.setFocus(Qt.OtherFocusReason)

    def clear_focus(self):
        """ Clear the keyboard input focus from this widget.

        """
        self.widget.clearFocus()

    def has_focus(self):
        """ Test whether this widget has input focus.

        """
        return self.widget.hasFocus()

    def focus_next_child(self):
        """ Give focus to the next widget in the focus chain.

        """
        self.widget.focusNextChild()

    def focus_previous_child(self):
        """ Give focus to the previous widget in the focus chain.

        """
        self.widget.focusPreviousChild()
