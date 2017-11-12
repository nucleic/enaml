#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, Value

from enaml.widgets.scroll_area import ProxyScrollArea

from .QtCore import Qt, QEvent, QSize, QRect, QPoint, Signal
from .QtGui import QPainter, QPalette
from .QtWidgets import QApplication, QScrollArea

from .qt_container import QtContainer
from .qt_frame import QtFrame


POLICIES = {
    'as_needed': Qt.ScrollBarAsNeeded,
    'always_off': Qt.ScrollBarAlwaysOff,
    'always_on': Qt.ScrollBarAlwaysOn
}


class QCustomScrollArea(QScrollArea):
    """ A custom QScrollArea for use with the QtScrollArea.

    This subclass fixes some bugs related to size hints.

    """
    #: A signal emitted when a LayoutRequest event is posted to the
    #: scroll area. This will typically occur when the size hint of
    #: the scroll area is no longer valid.
    layoutRequested = Signal()

    #: A private internally cached size hint.
    _size_hint = QSize()

    def event(self, event):
        """ A custom event handler for the scroll area.

        This handler dispatches layout requests and paints the empty
        corner between the scroll bars.

        """
        res = super(QCustomScrollArea, self).event(event)
        event_t = event.type()
        if event_t == QEvent.Paint:
            # Fill in the empty corner area with the app window color.
            color = QApplication.palette().color(QPalette.Window)
            tl = self.viewport().geometry().bottomRight()
            fw = self.frameWidth()
            br = self.rect().bottomRight() - QPoint(fw, fw)
            QPainter(self).fillRect(QRect(tl, br), color)
        elif event_t == QEvent.LayoutRequest:
            self._size_hint = QSize()
            self.layoutRequested.emit()
        return res

    def setWidget(self, widget):
        """ Set the widget for this scroll area.

        This is a reimplemented parent class method which invalidates
        the cached size hint before setting the widget.

        """
        self._size_hint = QSize()
        self.takeWidget()  # Let Python keep ownership of the old widget
        super(QCustomScrollArea, self).setWidget(widget)

    def sizeHint(self):
        """ Get the size hint for the scroll area.

        This reimplemented method fixes a Qt bug where the size hint
        is not updated after the scroll widget is first shown. The
        bug is documented on the Qt bug tracker:
        https://bugreports.qt-project.org/browse/QTBUG-10545

        """
        # This code is ported directly from QScrollArea.cpp but instead
        # of caching the size hint of the scroll widget, it caches the
        # size hint for the entire scroll area, and invalidates it when
        # the widget is changed or it receives a LayoutRequest event.
        hint = self._size_hint
        if hint.isValid():
            return QSize(hint)
        fw = 2 * self.frameWidth()
        hint = QSize(fw, fw)
        font_height = self.fontMetrics().height()
        widget = self.widget()
        if widget is not None:
            if self.widgetResizable():
                hint += widget.sizeHint()
            else:
                hint += widget.size()
        else:
            hint += QSize(12 * font_height, 8 * font_height)
        if self.verticalScrollBarPolicy() == Qt.ScrollBarAlwaysOn:
            vbar = self.verticalScrollBar()
            hint.setWidth(hint.width() + vbar.sizeHint().width())
        if self.horizontalScrollBarPolicy() == Qt.ScrollBarAlwaysOn:
            hbar = self.horizontalScrollBar()
            hint.setHeight(hint.height() + hbar.sizeHint().height())
        hint = hint.boundedTo(QSize(36 * font_height, 24 * font_height))
        self._size_hint = hint
        return QSize(hint)


class QtScrollArea(QtFrame, ProxyScrollArea):
    """ A Qt implementation of an Enaml ProxyScrollArea.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QCustomScrollArea)

    #: A private cache of the old size hint for the scroll area.
    _old_hint = Value()

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QScrollArea widget.

        """
        self.widget = QCustomScrollArea(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtScrollArea, self).init_widget()
        d = self.declaration
        self.set_horizontal_policy(d.horizontal_policy)
        self.set_vertical_policy(d.vertical_policy)
        self.set_widget_resizable(d.widget_resizable)

    def init_layout(self):
        """ Initialize the layout of the underlying widget.

        """
        super(QtScrollArea, self).init_layout()
        widget = self.widget
        widget.setWidget(self.scroll_widget())
        widget.layoutRequested.connect(self.on_layout_requested)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def scroll_widget(self):
        """ Find and return the scroll widget child for this widget.

        """
        w = self.declaration.scroll_widget()
        if w is not None:
            return w.proxy.widget

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtScrollArea.

        """
        super(QtScrollArea, self).child_added(child)
        if isinstance(child, QtContainer):
            self.widget.setWidget(self.scroll_widget())

    def child_removed(self, child):
        """ Handle the child removed event for a QtScrollArea.

        """
        super(QtScrollArea, self).child_removed(child)
        if isinstance(child, QtContainer):
            self.widget.setWidget(self.scroll_widget())

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_layout_requested(self):
        """ Handle the `layoutRequested` signal from the QScrollArea.

        """
        new_hint = self.widget.sizeHint()
        if new_hint != self._old_hint:
            self._old_hint = new_hint
            self.geometry_updated()

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def replace_constraints(self, old_cns, new_cns):
        """ A reimplemented QtConstraintsWidget layout method.

        Constraints layout may not cross the boundary of a ScrollArea,
        so this method is no-op which stops the layout propagation.

        """
        pass

    #--------------------------------------------------------------------------
    # ProxyScrollArea API
    #--------------------------------------------------------------------------
    def set_horizontal_policy(self, policy):
        """ Set the horizontal scrollbar policy of the widget.

        """
        self.widget.setHorizontalScrollBarPolicy(POLICIES[policy])

    def set_vertical_policy(self, policy):
        """ Set the vertical scrollbar policy of the widget.

        """
        self.widget.setVerticalScrollBarPolicy(POLICIES[policy])

    def set_widget_resizable(self, resizable):
        """ Set whether or not the scroll widget is resizable.

        """
        self.widget.setWidgetResizable(resizable)
