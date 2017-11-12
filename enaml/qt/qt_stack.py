#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Int, IntEnum, Typed

from enaml.widgets.stack import ProxyStack

from .QtCore import QTimer, QEvent, Signal
from .QtGui import QPixmap
from .QtWidgets import QStackedWidget

from .q_pixmap_painter import QPixmapPainter
from .q_pixmap_transition import (
    QDirectedTransition, QSlideTransition, QWipeTransition, QIrisTransition,
    QFadeTransition, QCrossFadeTransition
)
from .qt_constraints_widget import QtConstraintsWidget
from .qt_stack_item import QtStackItem


TRANSITION_TYPE = {
    'slide': QSlideTransition,
    'wipe': QWipeTransition,
    'iris': QIrisTransition,
    'fade': QFadeTransition,
    'crossfade': QCrossFadeTransition,
}


TRANSITION_DIRECTION = {
    'left_to_right': QDirectedTransition.LeftToRight,
    'right_to_left': QDirectedTransition.RightToLeft,
    'top_to_bottom': QDirectedTransition.TopToBottom,
    'bottom_to_top': QDirectedTransition.BottomToTop,
}


def make_transition(transition):
    """ Make a QPixmapTransition from an Enaml Transition.

    Parameters
    ----------
    transition : Transition
        The Enaml Transition object.

    Returns
    -------
    result : QPixmapTransition
        A QPixmapTransition to use as the transition.

    """
    qtransition = TRANSITION_TYPE[transition.type]()
    qtransition.setDuration(transition.duration)
    if isinstance(qtransition, QDirectedTransition):
        qtransition.setDirection(TRANSITION_DIRECTION[transition.direction])
    return qtransition


class QStack(QStackedWidget):
    """ A QStackedWidget subclass which adds support for transitions.

    """
    class SizeHintMode(IntEnum):
        """ An int enum defining the size hint modes of the stack.

        """
        #: The size hint is the union of all stack items.
        Union = 0

        #: The size hint is the size hint of the current stack item.
        Current = 1

    #: Proxy the SizeHintMode values as if it were an anonymous enum.
    Union = SizeHintMode.Union
    Current = SizeHintMode.Current

    #: A signal emitted when a LayoutRequest event is posted to the
    #: stack widget. This will typically occur when the size hint of
    #: the stack is no longer valid.
    layoutRequested = Signal()

    def __init__(self, *args, **kwargs):
        """ Initialize a QStack.

        Parameters
        ----------
        *args, **kwargs
            The positional and keyword arguments needed to initalize
            a QStackedWidget.

        """
        super(QStack, self).__init__(*args, **kwargs)
        self._painter = None
        self._transition = None
        self._transition_index = 0
        self._size_hint_mode = QStack.Union

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _onTransitionFinished(self):
        """ A signal handler for the `finished` signal of the transition.

        This method resets the internal painter and triggers the normal
        index change for the stacked widget.

        """
        painter = self._painter
        if painter is not None:
            painter.setTargetWidget(None)
        self._painter = None
        self.setCurrentIndex(self._transition_index)
        # This final show() makes sure the underlyling widget is visible.
        # If transitions are being fired rapidly, it's possible that the
        # current index and the transition index will be the same when
        # the call above is invoked. In such cases, Qt short circuits the
        # evaluation and the current widget is not shown.
        self.currentWidget().show()

    def _runTransition(self):
        """ A private method which runs the transition effect.

        The `_transition_index` attribute should be set before calling
        this method. If no transition object exists for this widget,
        then it is equivalent to calling `setCurrentIndex`. If the new
        index is not different from the current index the transition
        will not be performed.

        """
        from_index = self.currentIndex()
        to_index = self._transition_index

        # If the index hasn't changed, there is nothing to update.
        if from_index == to_index:
            return

        # If there is no transition applied, just change the index.
        transition = self._transition
        if transition is None:
            self.setCurrentIndex(to_index)
            return

        # Otherwise, grab the pixmaps for the start and ending states
        # and set them on the transtion. The widgets are resized to the
        # current size so that the pixmaps are grabbed in a good state.
        src_widget = self.widget(from_index)
        dst_widget = self.widget(to_index)
        size = self.size()
        src_widget.resize(size)
        dst_widget.resize(size)
        src_pixmap = QPixmap.grabWidget(src_widget)
        dst_pixmap = QPixmap.grabWidget(dst_widget)
        out_pixmap = QPixmap(size)
        transition.setPixmaps(src_pixmap, dst_pixmap, out_pixmap)

        # Hide both of the constituent widgets so that the painter has
        # a clean widget on which to draw.
        src_widget.setVisible(False)
        dst_widget.setVisible(False)

        # Hookup the pixmap painter and start the transition.
        painter = self._painter = QPixmapPainter()
        painter.setTargetWidget(self)
        transition.pixmapUpdated.connect(painter.drawPixmap)
        transition.start()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def event(self, event):
        """ A custom event handler which handles LayoutRequest events.

        When a LayoutRequest event is posted to this widget, it will
        emit the `layoutRequested` signal. This allows an external
        consumer of this widget to update their external layout.

        """
        res = super(QStack, self).event(event)
        if event.type() == QEvent.LayoutRequest:
            self.layoutRequested.emit()
        return res

    def sizeHint(self):
        """ A reimplemented size hint handler.

        This method will compute the size hint based on the size hint
        of the current tab, instead of the default behavior which is
        the maximum of all the size hints of the tabs.

        """
        if self._size_hint_mode == QStack.Current:
            curr = self.currentWidget()
            if curr is not None:
                return curr.sizeHint()
        return super(QStack, self).sizeHint()

    def minimumSizeHint(self):
        """ A reimplemented minimum size hint handler.

        This method will compute the size hint based on the size hint
        of the current tab, instead of the default behavior which is
        the maximum of all the minimum size hints of the tabs.

        """
        if self._size_hint_mode == QStack.Current:
            curr = self.currentWidget()
            if curr is not None:
                return curr.minimumSizeHint()
        return super(QStack, self).minimumSizeHint()

    def sizeHintMode(self):
        """ Get the size hint mode of the stack.

        Returns
        -------
        result : QStack.SizeHintMode
            The size hint mode enum value for the stack.

        """
        return self._size_hint_mode

    def setSizeHintMode(self, mode):
        """ Set the size hint mode of the stack.

        Parameters
        ----------
        mode : QStack.SizeHintMode
            The size hint mode for the stack.

        """
        assert isinstance(mode, QStack.SizeHintMode)
        self._size_hint_mode = mode

    def transition(self):
        """ Get the transition installed on this widget.

        Returns
        -------
        result : QPixmapTransition or None
            The pixmap transition installed on this widget, or None if
            no transition is being used.

        """
        return self._transition

    def setTransition(self, transition):
        """ Set the transition to be used by this widget.

        Parameters
        ----------
        transition : QPixmapTransition or None
            The transition to use when changing between widgets on this
            stack or None if no transition should be used.

        """
        old = self._transition
        if old is not None:
            old.finished.disconnect(self._onTransitionFinished)
        self._transition = transition
        if transition is not None:
            transition.finished.connect(self._onTransitionFinished)

    def transitionTo(self, index):
        """ Transition the stack widget to the given index.

        If there is no transition object is installed on the widget
        this is equivalent to calling `setCurrentIndex`. Otherwise,
        the change will be animated using the installed transition.

        Parameters
        ----------
        index : int
            The index of the target transition widget.

        """
        if index < 0 or index >= self.count():
            return
        self._transition_index = index
        if self.transition() is not None:
            QTimer.singleShot(0, self._runTransition)
        else:
            self.setCurrentIndex(index)


#: A mapping Enaml -> Qt size hint modes.
SIZE_HINT_MODE = {
    'union': QStack.Union,
    'current': QStack.Current,
}


#: Cyclic notification guard
INDEX_FLAG = 0x1


class QtStack(QtConstraintsWidget, ProxyStack):
    """ A Qt implementation of an Enaml Stack.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QStack)

    #: Cyclic notification guards
    _guard = Int(0)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QStack widget.

        """
        self.widget = QStack(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying control.

        """
        super(QtStack, self).init_widget()
        d = self.declaration
        self.set_transition(d.transition)
        self.set_size_hint_mode(d.size_hint_mode, update=False)

    def init_layout(self):
        """ Initialize the layout of the underlying control.

        """
        super(QtStack, self).init_layout()
        widget = self.widget
        for item in self.stack_items():
            widget.addWidget(item)
        # Bypass the transition effect during initialization.
        widget.setCurrentIndex(self.declaration.index)
        widget.layoutRequested.connect(self.on_layout_requested)
        widget.currentChanged.connect(self.on_current_changed)

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def stack_items(self):
        """ Get the stack items defined on the control.

        """
        for d in self.declaration.stack_items():
            w = d.proxy.widget
            if w is not None:
                yield w

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtStack.

        """
        super(QtStack, self).child_added(child)
        if isinstance(child, QtStackItem):
            for index, dchild in enumerate(self.children()):
                if child is dchild:
                    self.widget.insertWidget(index, child.widget)

    def child_removed(self, child):
        """ Handle the child removed event for a QtStack.

        """
        super(QtStack, self).child_removed(child)
        if isinstance(child, QtStackItem):
            self.widget.removeWidget(child.widget)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_layout_requested(self):
        """ Handle the `layoutRequested` signal from the QStack.

        """
        self.geometry_updated()

    def on_current_changed(self):
        """ Handle the `currentChanged` signal from the QStack.

        """
        if not self._guard & INDEX_FLAG:
            self._guard |= INDEX_FLAG
            try:
                self.declaration.index = self.widget.currentIndex()
            finally:
                self._guard &= ~INDEX_FLAG

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_index(self, index):
        """ Set the current index of the underlying widget.

        """
        if not self._guard & INDEX_FLAG:
            self._guard |= INDEX_FLAG
            try:
                self.widget.transitionTo(index)
            finally:
                self._guard &= ~INDEX_FLAG

    def set_transition(self, transition):
        """ Set the transition on the underlying widget.

        """
        if transition:
            self.widget.setTransition(make_transition(transition))
        else:
            self.widget.setTransition(None)

    def set_size_hint_mode(self, mode, update=True):
        """ Set the size hint mode for the widget.

        """
        self.widget.setSizeHintMode(SIZE_HINT_MODE[mode])
        if update:
            self.geometry_updated()
