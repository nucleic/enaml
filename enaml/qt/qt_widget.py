#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, Coerced, Bool, Unicode, List, Instance

from enaml.drag import Drag
from enaml.styling import StyleCache
from enaml.widgets.widget import Feature, ProxyWidget
from enaml.validator import Validator

from .QtCore import (Qt, QSize, QObject, Signal, QEvent, QMimeData, QByteArray,
                     QPoint)
from .QtGui import (QFont, QWidget, QWidgetAction, QApplication, QDrag,
                    QPixmap, QColor)

from . import focus_registry
from .q_resource_helpers import (get_cached_qcolor, get_cached_qfont,
                                 get_cached_qimage)
from .qt_toolkit_object import QtToolkitObject
from .styleutil import translate_style


class DragDropEventFilter(QObject):
    """ An event filter for mouse and drag/drop events.

    """
    mousePressed = Signal(object)
    mouseMoved = Signal(object)
    dragEntered = Signal(object)
    dragLeft = Signal(object)
    dragMoved = Signal(object)
    dropped = Signal(object)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonPress:
            self.mousePressed.emit(event)
            return False

        elif event.type() == QEvent.MouseMove:
            self.mouseMoved.emit(event)
            return False

        elif event.type() == QEvent.DragMove:
            self.dragMoved.emit(event)
            return False

        elif event.type() == QEvent.DragEnter:
            self.dragEntered.emit(event)
            return False

        elif event.type() == QEvent.DragLeave:
            self.dragLeft.emit(event)
            return False

        elif event.type() == QEvent.Drop:
            self.dropped.emit(event)
            return False

        else:
            return super(DragDropEventFilter, self).eventFilter(obj, event)


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

    #: Internal storage for the drag object
    _drag = Typed(Drag)

    #: The function to check whether a drop is supported.
    _accept_drops = Typed(Validator)

    #: An event filter for catching mouse events
    _drag_drop_filter = Typed(DragDropEventFilter)

    #: The position where the drag event started.
    _drag_origin = Typed(QPoint)

    #: The type of data being dragged.
    _drag_type = Unicode()

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
        self._drag_drop_filter = DragDropEventFilter()
        widget.installEventFilter(self._drag_drop_filter)
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
        if d.drag:
            self.set_drag(d.drag)
        if d.accept_drops:
            self.set_accept_drops(d.accept_drops)
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
        self._accept_drops = accept_drops

        if accept_drops is not None:
            self.widget.setAcceptDrops(True)
            self._drag_drop_filter.dragEntered.connect(self._on_drag_enter)
            self._drag_drop_filter.dragMoved.connect(self._on_drag_move)
            self._drag_drop_filter.dragLeft.connect(self._on_drag_leave)
            self._drag_drop_filter.dropped.connect(self._on_drop)

        else:
            self.widget.setAcceptDrops(False)
            self._drag_drop_filter.dragEntered.disconnect()
            self._drag_drop_filter.dragLeft.disconnect()
            self._drag_drop_filter.dropped.disconnect()

    def set_drag(self, drag):
        """ Set the drag object for the widget.

        """
        self._drag = drag

        if drag is not None:
            self._drag_drop_filter.mousePressed.connect(self._on_mouse_press)
            self._drag_drop_filter.mouseMoved.connect(self._on_mouse_move)

        else:
            self._drag_drop_filter.mousePressed.disconnect()
            self._drag_drop_filter.mouseMoved.disconnect()

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
    def _on_mouse_press(self, event):
        """ Handler for the mouseButtonPress event.

        """
        self._drag_origin = event.pos()

    def _on_mouse_move(self, event):
        """ Handler for the mouseMove event.

        """
        if self._drag is not None:
            distance = (event.pos() - self._drag_origin).manhattanLength()
            if distance > QApplication.startDragDistance():
                drag = QDrag(self.widget)

                mime_data = QMimeData()
                mime_data.setData(self._drag.type,
                                  QByteArray(str(self._drag.data)))
                drag.setMimeData(mime_data)

                if self._drag.image:
                    qimage = get_cached_qimage(self._drag.image)
                    drag.setPixmap(QPixmap.fromImage(qimage))
                else:
                    drag.setPixmap(QPixmap.grabWidget(self.widget))

                drag.exec_(Qt.CopyAction)

    def _on_drag_enter(self, event):
        """ Fired when a dragged object is hovering over the widget

        """
        for format in event.mimeData().formats():
            if self._accept_drops.validate(format):
                self._drag_type = format
                event.acceptProposedAction()
                break

        content = {
            'data': event.mimeData().data(self._drag_type).data(),
            'pos': (event.pos().x(), event.pos().y()),
            'type': self._drag_type,
        }
        self.declaration._handle_drag_enter(content)

    def _on_drag_leave(self, event):
        """ Fired when an object is dragged off the widget

        """
        self.declaration._handle_drag_leave({})

    def _on_drag_move(self, event):
        """ Fired when an object is moved while dragging

        """
        content = {
            'data': event.mimeData().data(self._drag_type).data(),
            'pos': (event.pos().x(), event.pos().y()),
            'type': self._drag_type,
        }
        self.declaration._handle_drag_move(content)

    def _on_drop(self, event):
        """ Fired when an object is dropped on the widget

        """
        content = {
            'data': event.mimeData().data(self._drag_type).data(),
            'pos': (event.pos().x(), event.pos().y()),
            'type': self._drag_type,
        }
        self.declaration._handle_drop(content)
        event.acceptProposedAction()
