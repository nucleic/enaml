#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from types import BuiltinFunctionType, MethodType

from atom.api import Typed, Coerced, Bool, Unicode, List, Instance

from enaml.styling import StyleCache
from enaml.widgets.widget import Feature, ProxyWidget

from .QtCore import Qt, QSize, QMimeData, QByteArray, QPoint
from .QtGui import QFont, QWidget, QWidgetAction, QApplication

from . import focus_registry
from .q_resource_helpers import get_cached_qcolor, get_cached_qfont
from .qt_toolkit_object import QtToolkitObject
from .styleutil import translate_style


class QtWidget(QtToolkitObject, ProxyWidget):
    """ A Qt implementation of an Enaml ProxyWidget.

    """
    #: A reference to the toolkit widget created by the proxy.
    widget = Typed(QWidget)

    #: A private copy of the declaration features. This ensures that
    #: feature cleanup will proceed correctly in the event that user
    #: code modifies the declaration features value at runtime.
    _features = Coerced(Feature.Flags)

    #: Internal storage for the shared widget action.
    _widget_action = Typed(QWidgetAction)

    #: Internal storage for drag and drop attributes
    _accept_drags = Bool(False)
    _drag_type = Unicode()
    _drag_data = Unicode()
    _drop_types = List()
    _highlight_drop = Bool(False)
    widgetMousePressEvent = Instance((BuiltinFunctionType, MethodType))
    widgetMouseMoveEvent = Instance((BuiltinFunctionType, MethodType))
    selected_type = Unicode()
    original_pos = Typed(QPoint)

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
        widget = self.widget
        focus_registry.register(widget, self)
        self._setup_features()
        d = self.declaration
        if d.background:
            self.set_background(d.background)
        if d.foreground:
            self.set_foreground(d.foreground)
        if d.font:
            self.set_font(d.font)
        if -1 not in d.minimum_size:
            self.set_minimum_size(d.minimum_size)
        if -1 not in d.maximum_size:
            self.set_maximum_size(d.maximum_size)
        if d.tool_tip:
            self.set_tool_tip(d.tool_tip)
        if d.status_tip:
            self.set_status_tip(d.status_tip)
        if d.drag_type:
            self.set_drag_type(d.drag_type)
        if d.drag_data:
            self.set_drag_data(d.drag_data)
        if d.drop_types:
            self.set_drop_types(d.drop_types)
        if d.accept_drops is not None:
            self.set_accept_drops(d.accept_drops)
        if d.accept_drags is not None:
            self.set_accept_drags(d.accept_drags)
        if d.highlight_drop is not None:
            self.set_highlight_drop(d.highlight_drop)
        if not d.enabled:
            self.set_enabled(d.enabled)
        self.refresh_style_sheet()
        # Don't make toplevel widgets visible during init or they will
        # flicker onto the screen. This applies particularly for things
        # like status bar widgets which are created with no parent and
        # then reparented by the status bar. Real top-level widgets must
        # be explicitly shown by calling their .show() method after they
        # are created.
        if widget.parent() or not d.visible:
            self.set_visible(d.visible)

        # XXX: Hack - We cannot subclass QWidget here because it would not
        # be inherited by all subclasses of QtWidget
        self.widgetMousePressEvent = widget.mousePressEvent
        widget.mousePressEvent = self.mousePressEvent

        self.widgetMouseMoveEvent = widget.mouseMoveEvent
        widget.mouseMoveEvent = self.mouseMoveEvent

        widget.dragEnterEvent = self.dragEnterEvent
        widget.dragLeaveEvent = self.dragLeaveEvent
        widget.dropEvent = self.dropEvent

    def destroy(self):
        """ Destroy the underlying QWidget object.

        """
        self._teardown_features()
        focus_registry.unregister(self.widget)
        super(QtWidget, self).destroy()
        # If a QWidgetAction was created for this widget, then it has
        # taken ownership of the widget and the widget will be deleted
        # when the QWidgetAction is garbage collected. This means the
        # superclass destroy() method must run before the reference to
        # the QWidgetAction is dropped.
        del self._widget_action

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _setup_features(self):
        """ Setup the advanced widget feature handlers.

        """
        features = self._features = self.declaration.features
        if not features:
            return
        if features & Feature.FocusTraversal:
            self.hook_focus_traversal()
        if features & Feature.FocusEvents:
            self.hook_focus_events()

    def _teardown_features(self):
        """ Teardowns the advanced widget feature handlers.

        """
        features = self._features
        if not features:
            return
        if features & Feature.FocusTraversal:
            self.unhook_focus_traversal()
        if features & Feature.FocusEvents:
            self.unhook_focus_events()

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

    def tab_focus_request(self, reason):
        """ Handle a custom tab focus request.

        This method is called when focus is being set on the proxy
        as a result of a user-implemented focus traversal handler.
        This can be reimplemented by subclasses as needed.

        Parameters
        ----------
        reason : Qt.FocusReason
            The reason value for the focus request.

        Returns
        -------
        result : bool
            True if focus was set, False otherwise.

        """
        widget = self.focus_target()
        if ((widget.focusPolicy() & Qt.TabFocus) and
            widget.isEnabled() and
            widget.isVisibleTo(widget.window())):
            widget.setFocus(reason)
            return True
        return False

    def focus_target(self):
        """ Return the current focus target for a focus request.

        This can be reimplemented by subclasses as needed. The default
        implementation of this method returns the current proxy widget.

        """
        return self.widget

    def hook_focus_traversal(self):
        """ Install the hooks for focus traversal.

        This method may be overridden by subclasses as needed.

        """
        self.widget.focusNextPrevChild = self.focusNextPrevChild

    def unhook_focus_traversal(self):
        """ Remove the hooks for the next/prev child focusing.

        This method may be overridden by subclasses as needed.

        """
        del self.widget.focusNextPrevChild

    def hook_focus_events(self):
        """ Install the hooks for focus events.

        This method may be overridden by subclasses as needed.

        """
        widget = self.widget
        widget.focusInEvent = self.focusInEvent
        widget.focusOutEvent = self.focusOutEvent

    def unhook_focus_events(self):
        """ Remove the hooks for the focus events.

        This method may be overridden by subclasses as needed.

        """
        widget = self.widget
        del widget.focusInEvent
        del widget.focusOutEvent

    def focusNextPrevChild(self, next_child):
        """ The default 'focusNextPrevChild' implementation.

        """
        fd = focus_registry.focused_declaration()
        if next_child:
            child = self.declaration.next_focus_child(fd)
            reason = Qt.TabFocusReason
        else:
            child = self.declaration.previous_focus_child(fd)
            reason = Qt.BacktabFocusReason
        if child is not None and child.proxy_is_active:
            return child.proxy.tab_focus_request(reason)
        widget = self.widget
        return type(widget).focusNextPrevChild(widget, next_child)

    def focusInEvent(self, event):
        """ The default 'focusInEvent' implementation.

        """
        widget = self.widget
        type(widget).focusInEvent(widget, event)
        self.declaration.focus_gained()

    def focusOutEvent(self, event):
        """ The default 'focusOutEvent' implementation.

        """
        widget = self.widget
        type(widget).focusOutEvent(widget, event)
        self.declaration.focus_lost()

    #--------------------------------------------------------------------------
    # Framework API
    #--------------------------------------------------------------------------
    def get_action(self, create=False):
        """ Get the shared widget action for this widget.

        This API is used to support widgets in tool bars and menus.

        Parameters
        ----------
        create : bool, optional
            Whether to create the action if it doesn't already exist.
            The default is False.

        Returns
        -------
        result : QWidgetAction or None
            The cached widget action or None, depending on arguments.

        """
        action = self._widget_action
        if action is None and create:
            action = self._widget_action = QWidgetAction(None)
            action.setDefaultWidget(self.widget)
        return action

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
        action = self._widget_action
        if action is not None:
            action.setEnabled(enabled)

    def set_visible(self, visible):
        """ Set the visibility of the widget.

        """
        self.widget.setVisible(visible)
        action = self._widget_action
        if action is not None:
            action.setVisible(visible)

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

    def set_accept_drops(self, accept_drops):
        """ Set whether or not the widget accepts drops

        """
        self.widget.setAcceptDrops(accept_drops)

    def set_accept_drags(self, accept_drags):
        """ Set whether or not the widget is draggable.

        """
        self._accept_drags = accept_drags

    def set_drag_type(self, drag_type):
        """ Set the mime-type being dragged

        """
        self._drag_type = drag_type

    def set_drag_data(self, drag_data):
        """ Set the data being dragged

        """
        self._drag_data = drag_data

    def set_drop_types(self, drop_types):
        """ Set the mime-types that are allowed to be dropped on the widget.

        """
        self._drop_types = drop_types

    def set_highlight_drop(self, highlight_drop):
        """ Set whether or not to highlight widgets when dropping

        """
        self._highlight_drop = highlight_drop

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
        action = self._widget_action
        if action is not None:
            action.setVisible(True)

    def ensure_hidden(self):
        """ Ensure the widget is hidden.

        """
        self.widget.setVisible(False)
        action = self._widget_action
        if action is not None:
            action.setVisible(False)

    def restyle(self):
        """ Restyle the widget with the current style data.

        """
        self.refresh_style_sheet()

    def set_focus(self):
        """ Set the keyboard input focus to this widget.

        """
        self.focus_target().setFocus(Qt.OtherFocusReason)

    def clear_focus(self):
        """ Clear the keyboard input focus from this widget.

        """
        self.focus_target().clearFocus()

    def has_focus(self):
        """ Test whether this widget has input focus.

        """
        return self.focus_target().hasFocus()

    def focus_next_child(self):
        """ Give focus to the next widget in the focus chain.

        """
        self.focus_target().focusNextChild()

    def focus_previous_child(self):
        """ Give focus to the previous widget in the focus chain.

        """
        self.focus_target().focusPreviousChild()

    #--------------------------------------------------------------------------
    # Drag and drop
    #--------------------------------------------------------------------------
    def drag_repr(self):
        """ An image representation of the widget. This method can be overridden
        for custom representations.

        """
        return QPixmap.grabWidget(self.widget)

    def hover_enter(self):
        """ Fired when the dragged object enters the widget. This method can be
        overriden for custom styling.

        """
        palette = self.widget.palette()
        palette.setColor(self.widget.backgroundRole(), QColor(0, 0, 255, 25))
        self.widget.setPalette(palette)

    def hover_exit(self):
        """ Fired when the dragged object leaves the widget. This method can be
        overriden for custom styling.

        """
        palette = self.widget.palette()
        palette.setColor(self.widget.backgroundRole(), QColor(0, 0, 0, 0))
        self.widget.setPalette(palette)

    def mousePressEvent(self, event):
        """ Mouse pressed handler

        """
        self.widgetMousePressEvent(event)
        self.original_pos = event.pos()

    def mouseMoveEvent(self, event):
        """ Mouse moved handler

        """
        self.widgetMouseMoveEvent(event)
        if self._accept_drags:
            distance = (event.pos() - self.original_pos).manhattanLength()
            if distance > 20:
                drag = QDrag(self.widget)
                mime_data = QMimeData()
                mime_data.setData(self._drag_type, QByteArray(self._drag_data))
                drag.setMimeData(mime_data)
                drag.setPixmap(self.drag_repr())
                drag.exec_(Qt.CopyAction)

    def dragEnterEvent(self, event):
        """ Fired when a dragged object is hovering over the widget

        """
        if self._highlight_drop:
            self.hover_enter()
        for format in event.mimeData().formats():
            if format in self._drop_types:
                self.selected_type = format
                event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        """ Fire when an object is dragged off the widget

        """
        if self._highlight_drop:
            self.hover_exit()

    def dropEvent(self, event):
        """ Fired when an object is dropped on the widget

        """
        content = {
            'data': event.mimeData().data(self.selected_type).data(),
            'pos': (event.pos().x(), event.pos().y()),
            'type': self.selected_type,
        }
        self.declaration._handle_drop(content)
        event.acceptProposedAction()
        self.hover_exit()
