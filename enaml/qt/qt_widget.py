#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, Coerced

from enaml.layout.geometry import Pos
from enaml.styling import StyleCache
from enaml.widgets.widget import Feature, ProxyWidget

from .QtCore import Qt, QSize, QPoint, QMimeData, QByteArray
from .QtGui import QFont, QWidget, QWidgetAction, QApplication, QDrag, QPixmap

from . import focus_registry
from .q_resource_helpers import (get_cached_qcolor, get_cached_qfont,
                                 get_cached_qimage)
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

    #: Internal storage for the drag origin point.
    _drag_origin = Typed(QPoint)

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
        if features & Feature.Drag:
            self.hook_drag()
        if features & Feature.Drop:
            self.hook_drop()

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
        if features & Feature.Drag:
            self.unhook_drag()
        if features & Feature.Drop:
            self.unhook_drop()

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

    def hook_drag(self):
        """ Install hooks for drag operations.

        """
        widget = self.widget
        widget.mousePressEvent = self.mousePressEvent
        widget.mouseMoveEvent = self.mouseMoveEvent

    def unhook_drag(self):
        """ Remove hooks for drag operations.

        """
        widget = self.widget
        del widget.mousePressEvent
        del widget.mouseMoveEvent

    def mousePressEvent(self, event):
        """ On mouse press, record the position to use as the origin for a
        drag operation.

        """
        widget = self.widget
        self._drag_origin = event.pos()
        type(widget).mousePressEvent(widget, event)

    def mouseMoveEvent(self, event):
        """ On mouse move, check the distance from the drag origin and
        initiate a drag operation if necessary.

        """
        widget = self.widget
        d = self.declaration

        if self._drag_origin is not None:
            distance = (event.pos() - self._drag_origin).manhattanLength()
            if distance > QApplication.startDragDistance():
                drag = QDrag(widget)

                dtype, data = d.drag_data()
                mime_data = QMimeData()
                mime_data.setData(dtype, QByteArray(str(data)))
                drag.setMimeData(mime_data)

                image = d.drag_image()
                if image:
                    qimage = get_cached_qimage(image)
                    drag.setPixmap(QPixmap.fromImage(qimage))
                else:
                    drag.setPixmap(QPixmap.grabWidget(widget))

                drag.exec_(Qt.CopyAction)

    def hook_drop(self):
        """ Install hooks for drop operations.

        """
        widget = self.widget
        widget.setAcceptDrops(True)
        widget.dragEnterEvent = self.dragEnterEvent
        widget.dragMoveEvent = self.dragMoveEvent
        widget.dragLeaveEvent = self.dragLeaveEvent
        widget.dropEvent = self.dropEvent

    def unhook_drop(self):
        """ Remove hooks for drop operations.

        """
        widget = self.widget
        widget.setAcceptDrops(False)
        del widget.dragEnterEvent
        del widget.dragMoveEvent
        del widget.dragLeaveEvent
        del widget.dropEvent

    def dragEnterEvent(self, event):
        widget = self.widget
        position = Pos(event.pos().x(), event.pos().y())

        mime_data = event.mimeData()
        dtype = mime_data.formats()[0]
        data = mime_data.data(dtype).data()

        if self.declaration.validate_drop(dtype):
            event.acceptProposedAction()

        type(widget).dragEnterEvent(widget, event)
        self.declaration.drag_enter(data, dtype, position)

    def dragMoveEvent(self, event):
        widget = self.widget
        position = Pos(event.pos().x(), event.pos().y())

        mime_data = event.mimeData()
        dtype = mime_data.formats()[0]
        data = mime_data.data(dtype).data()

        event.acceptProposedAction()
        type(widget).dragMoveEvent(widget, event)
        self.declaration.drag_move(data, dtype, position)

    def dragLeaveEvent(self, event):
        widget = self.widget
        type(widget).dragLeaveEvent(widget, event)
        self.declaration.drag_leave()

    def dropEvent(self, event):
        widget = self.widget
        position = Pos(event.pos().x(), event.pos().y())

        mime_data = event.mimeData()
        dtype = mime_data.formats()[0]
        data = mime_data.data(dtype).data()

        event.acceptProposedAction()
        type(widget).dropEvent(widget, event)
        self.declaration.drop(data, dtype, position)

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
