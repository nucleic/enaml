#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtCore import QTimer, QEvent, Signal
from .qt.QtGui import QStackedWidget, QPixmap
from .qt_constraints_widget import QtConstraintsWidget
from .qt_stack_item import QtStackItem
from .q_pixmap_painter import QPixmapPainter
from .q_pixmap_transition import (
    QDirectedTransition, QSlideTransition, QWipeTransition, QIrisTransition,
    QFadeTransition, QCrossFadeTransition
)


_TRANSITION_TYPES = {
    'slide': QSlideTransition,
    'wipe': QWipeTransition,
    'iris': QIrisTransition,
    'fade': QFadeTransition,
    'crossfade': QCrossFadeTransition,
}


_TRANSITION_DIRECTIONS = {
    'left_to_right': QDirectedTransition.LeftToRight,
    'right_to_left': QDirectedTransition.RightToLeft,
    'top_to_bottom': QDirectedTransition.TopToBottom,
    'bottom_to_top': QDirectedTransition.BottomToTop,
}


def make_transition(info):
    """ Make a QPixmapTransition from a description dictionary.

    Parameters
    ----------
    info : dict
        A dictionary sent by an Enaml widget which represents a
        transition.

    Returns
    -------
    result : QPixmapTransition or None
        A QPixmapTransition to use as the transition, or None if one
        could not be created for the given dict.

    """
    type_ = info.get('type')
    if type_ in _TRANSITION_TYPES:
        transition = _TRANSITION_TYPES[type_]()
        duration = info.get('duration')
        if duration is not None:
            transition.setDuration(duration)
        if isinstance(transition, QDirectedTransition):
            direction = info.get('direction')
            if direction in _TRANSITION_DIRECTIONS:
                transition.setDirection(_TRANSITION_DIRECTIONS[direction])
        return transition


class QStack(QStackedWidget):
    """ A QStackedWidget subclass which adds support for transitions.

    """
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
        self._transition_index = index
        if self.transition() is not None:
            QTimer.singleShot(0, self._runTransition)
        else:
            self.setCurrentIndex(index)


class QtStack(QtConstraintsWidget):
    """ A Qt implementation of an Enaml Stack.

    """
    #: The initial selected index in the stack.
    _initial_index = 0

    def create_widget(self, parent, tree):
        """ Create the underlying QStack widget.

        """
        return QStack(parent)

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(QtStack, self).create(tree)
        self.set_transition(tree['transition'])
        self._initial_index = tree['index']

    def init_layout(self):
        """ Initialize the layout of the underlying control.

        """
        super(QtStack, self).init_layout()
        widget = self.widget()
        for child in self.children():
            if isinstance(child, QtStackItem):
                widget.addWidget(child.widget())
        # Bypass the transition effect during initialization.
        widget.setCurrentIndex(self._initial_index)
        widget.layoutRequested.connect(self.on_layout_requested)
        widget.currentChanged.connect(self.on_current_changed)

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtStack.

        """
        if isinstance(child, QtStackItem):
            self.widget().removeWidget(child.widget())

    def child_added(self, child):
        """ Handle the child added event for a QtStack.

        """
        if isinstance(child, QtStackItem):
            index = self.index_of(child)
            if index != -1:
                self.widget().insertWidget(index, child.widget())

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_layout_requested(self):
        """ Handle the `layoutRequested` signal from the QStack.

        """
        self.size_hint_updated()

    def on_current_changed(self):
        """ Handle the `currentChanged` signal from the QStack.

        """
        if 'index' not in self.loopback_guard:
            index = self.widget().currentIndex()
            self.send_action('index_changed', {'index': index})

    #--------------------------------------------------------------------------
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_set_index(self, content):
        """ Handle the 'set_index' action from the Enaml widget.

        """
        with self.loopback_guard('index'):
            self.set_index(content['index'])

    def on_action_set_transition(self, content):
        """ Handle the 'set_transition' action from the Enaml widget.

        """
        self.set_transition(content['transition'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_index(self, index):
        """ Set the current index of the underlying widget.

        """
        self.widget().transitionTo(index)

    def set_transition(self, transition):
        """ Set the transition on the underlying widget.

        """
        self.widget().setTransition(make_transition(transition))

