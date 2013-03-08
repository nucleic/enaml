#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys

from .qt.QtCore import Qt, QEvent, Signal
from .qt.QtGui import (
    QSplitter, QSplitterHandle, QVBoxLayout, QFrame, QApplication
)
from .qt_constraints_widget import QtConstraintsWidget
from .qt_split_item import QtSplitItem


_ORIENTATION_MAP = {
    'horizontal': Qt.Horizontal,
    'vertical': Qt.Vertical,
}


class QWinSplitterHandle(QSplitterHandle):
    """ A custom QSplitterHandle which is used on win32 platforms.

    The native Windows style draws the splitter handle the same color as
    the widget background, which makes it invisible for most cases. This
    subclass overlays a raised line on the splitter to provide a little
    bit of visual feedback.

    """
    def __init__(self, orientation, parent=None):
        super(QWinSplitterHandle, self).__init__(orientation, parent)
        self._frame = frame = QFrame(self)
        l = QVBoxLayout()
        l.addWidget(frame)
        l.setSpacing(0)
        l.setContentsMargins(0, 0, 0, 0)
        self.setLayout(l)
        self.updateFrame()

    def updateFrame(self):
        """ Update the internal frame style for the current orientation.

        """
        orientation = self.orientation()
        s = QFrame.VLine if orientation == Qt.Horizontal else QFrame.HLine
        self._frame.setFrameStyle(s | QFrame.Raised)


class QCustomSplitter(QSplitter):
    """ A custom QSplitter which handles children of type QSplitItem.

    """
    #: A signal emitted when a LayoutRequest event is posted to the
    #: splitter widget. This will typically occur when the size hint
    #: of the splitter is no longer valid.
    layoutRequested = Signal()

    def createHandle(self):
        """ A reimplemented virtual method to create splitter handles.

        On win32 platforms, this will return a custom QSplitterHandle
        which works around an issue with handle not drawing nicely. On
        all other platforms, a normal QSplitterHandler widget.

        """
        if sys.platform == 'win32':
            return QWinSplitterHandle(self.orientation(), self)
        return QSplitterHandle(self.orientation(), self)

    def setOrientation(self, orientation):
        """ Set the orientation of the splitter.

        This overriden method will call the `updateFrame` method of the
        splitter handles when running on win32 platforms. On any other
        platform, this method simply calls the superclass method.

        """
        old = self.orientation()
        if old != orientation:
            super(QCustomSplitter, self).setOrientation(orientation)
            if sys.platform == 'win32':
                for idx in xrange(self.count()):
                    handle = self.handle(idx)
                    handle.updateFrame()

    def event(self, event):
        """ A custom event handler which handles LayoutRequest events.

        When a LayoutRequest event is posted to this widget, it will
        emit the `layoutRequested` signal. This allows an external
        consumer of this widget to update their external layout.

        """
        res = super(QCustomSplitter, self).event(event)
        if event.type() == QEvent.LayoutRequest:
            self.layoutRequested.emit()
        return res


class QtSplitter(QtConstraintsWidget):
    """ A Qt implementation of an Enaml Splitter.

    """
    #--------------------------------------------------------------------------
    # Setup methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Creates the underlying QSplitter control.

        """
        return QCustomSplitter(parent)

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(QtSplitter, self).create(tree)
        self.set_orientation(tree['orientation'])
        self.set_live_drag(tree['live_drag'])

    def init_layout(self):
        """ Handle the layout initialization for the splitter.

        """
        super(QtSplitter, self).init_layout()
        widget = self.widget()
        for child in self.children():
            if isinstance(child, QtSplitItem):
                widget.addWidget(child.widget())
        widget.layoutRequested.connect(self.on_layout_requested)

        # On Windows, messages are consumed from three different queues,
        # each with a different priority. The lowest priority is the
        # queue which holds WM_PAINT messages. Dragging the splitter bar
        # generates WM_MOUSEMOVE messages which have a higher priority.
        # These messages (dragging the bar) generate size events in Qt
        # which are delivered immediately. This means that if handling
        # the resize event from the drag takes too long (> ~800us) then
        # another size event will arrive before the paint event, since
        # the new WM_MOUSEMOVE will be processed before the WM_PAINT.
        # So on Windows, the `splitterMoved` signal, which is emitted
        # on every drag, is connected to a handler which will force a
        # repaint if opaque resize is turned on. Since paint event are
        # collapsed, the effect of this is to restore the order of event
        # processing.
        if sys.platform == 'win32':
            widget.splitterMoved.connect(self.on_win32_splitter_moved)

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------

    # QSplitter automatically removes a widget when it's reparented. The
    # base child_removed event will set the parent to None, and that is
    # all that is needed.

    def child_added(self, child):
        """ Handle the child added event for a QtSplitter.

        """
        if isinstance(child, QtSplitItem):
            index = self.index_of(child)
            if index != -1:
                self.widget().insertWidget(index, child.widget())

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_layout_requested(self):
        """ Handle the `layoutRequested` signal from the QSplitter.

        """
        self.size_hint_updated()

    def on_win32_splitter_moved(self):
        """ Handle the 'splitterMoved' signal from the QSplitter.

        This handler is only connected when running on Windows and it
        serves to make sure paint events get processed during heavy
        resize events when opaque resizing is turned on.

        """
        if self.widget().opaqueResize():
            QApplication.sendPostedEvents()

    #--------------------------------------------------------------------------
    # Message Handler Methods
    #--------------------------------------------------------------------------
    def on_action_set_orientation(self, content):
        """ Handle the 'set_orientation' action from the Enaml widget.

        """
        self.set_orientation(content['orientation'])
        self.size_hint_updated()

    def on_action_set_live_drag(self, content):
        """ Handle the 'set_live_drag' action from the Enaml widget.

        """
        self.set_live_drag(content['live_drag'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_orientation(self, orientation):
        """ Update the orientation of the QSplitter.

        """
        q_orientation = _ORIENTATION_MAP[orientation]
        self.widget().setOrientation(q_orientation)

    def set_live_drag(self, live_drag):
        """ Update the dragging mode of the QSplitter.

        """
        self.widget().setOpaqueResize(live_drag)

