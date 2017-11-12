#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.flow_item import ProxyFlowItem

from .QtCore import QSize, QEvent
from .QtWidgets import QFrame, QLayout

from .q_flow_layout import QFlowLayout, AbstractFlowWidget, FlowLayoutData
from .q_single_widget_layout import QSingleWidgetLayout
from .qt_container import QtContainer
from .qt_widget import QtWidget


_ALIGN_MAP = {
    'leading': QFlowLayout.AlignLeading,
    'trailing': QFlowLayout.AlignTrailing,
    'center': QFlowLayout.AlignCenter,
}


class QFlowItem(QFrame):
    """ A QFrame subclass which acts as an item in a QFlowArea.

    """
    def __init__(self, parent=None):
        """ Initialize a QFlowItem.

        Parameters
        ----------
        parent : QWidget, optional
            The parent of the flow item.

        """
        super(QFlowItem, self).__init__(parent)
        self._flow_widget = None
        self._layout_data = FlowLayoutData()
        self.setLayout(QSingleWidgetLayout())
        self.layout().setSizeConstraint(QLayout.SetMinAndMaxSize)

    def layoutData(self):
        """ Get the layout data associate with this flow item.

        This method implements the AbstractFlowWidget interface.

        Returns
        -------
        result : FlowLayoutData
            The layout data for this flow item.

        """
        return self._layout_data

    def preferredSize(self):
        """ Get the preferred size for this widget.

        Returns
        -------
        result : QSize
            The preferred size of this flow item.

        """
        return self._layout_data.preferred_size

    def setPreferredSize(self, size):
        """ Set the preferred size for this flow item.

        This will trigger an invalidation of the layout data.

        Parameters
        ----------
        size : QSize
            The preferred size for the flow item.

        """
        d = self._layout_data
        d.preferred_size = size
        d.dirty = True
        self.updateGeometry()

    def alignment(self):
        """ Get the alignment for the flow item.

        Returns
        -------
        result : QFlowLayout alignment
            The alignment for the flow item in the layout.

        """
        return self._layout_data.alignment

    def setAlignment(self, alignment):
        """ Set the alignment for the flow item.

        This will trigger an invalidation of the layout data.

        Parameters
        ----------
        alignment : QFlowLayout alignment
            The alignment for the flow item in the layout.

        """
        d = self._layout_data
        d.alignment = alignment
        d.dirty = True
        self.updateGeometry()

    def stretch(self):
        """ Get the stretch factor for the flow item.

        Returns
        -------
        result : int
            The stretch factor for the flow item in the direction of
            the layout flow.

        """
        return self._layout_data.stretch

    def setStretch(self, stretch):
        """ Set the stretch factor for the flow item.

        This will trigger an invalidation of the layout data.

        Parameters
        ----------
        stretch : int
            The stretch factor for the flow item in the direction of
            the layout flow.

        """
        d = self._layout_data
        d.stretch = stretch
        d.dirty = True
        self.updateGeometry()

    def orthoStretch(self):
        """ Get the ortho stretch factor for the flow item.

        Returns
        -------
        result : int
            The stretch factor for the flow item in the direction
            orthogonal to the layout flow.

        """
        return self._layout_data.stretch

    def setOrthoStretch(self, stretch):
        """ Set the ortho stretch factor for the flow item.

        This will trigger an invalidation of the layout data.

        Parameters
        ----------
        stretch : int
            The stretch factor for the flow item in the direction
            orthogonal to the layout flow.

        """
        d = self._layout_data
        d.ortho_stretch = stretch
        d.dirty = True
        self.updateGeometry()

    def flowWidget(self):
        """ Get the flow widget for this flow item.

        Returns
        -------
        result : QWidget or None
            The flow widget being managed by this item.

        """
        return self._flow_widget

    def setFlowWidget(self, widget):
        """ Set the flow widget for this flow item.

        Parameters
        ----------
        widget : QWidget
            The QWidget to use as the flow widget in this item.

        """
        self._flow_widget = widget
        self.layout().setWidget(widget)

    def event(self, event):
        """ A custom event handler which handles LayoutRequest events.

        When a LayoutRequest event is posted to this widget, it will
        emit the `layoutRequested` signal. This allows an external
        consumer of this widget to update their external layout.

        """
        if event.type() == QEvent.LayoutRequest:
            self._layout_data.dirty = True
        return super(QFlowItem, self).event(event)


AbstractFlowWidget.register(QFlowItem)


class QtFlowItem(QtWidget, ProxyFlowItem):
    """ A Qt implementation of an Enaml ProxyFlowItem.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QFlowItem)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QFlowItem widget.

        """
        self.widget = QFlowItem(self.parent_widget())

    def init_widget(self):
        """ Iitialize the underlying control.

        """
        super(QtFlowItem, self).init_widget()
        d = self.declaration
        self.set_preferred_size(d.preferred_size)
        self.set_align(d.align)
        self.set_stretch(d.stretch)
        self.set_ortho_stretch(d.ortho_stretch)

    def init_layout(self):
        """ Initialize the layout for the underyling widget.

        """
        super(QtFlowItem, self).init_layout()
        self.widget.setFlowWidget(self.flow_widget())

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def flow_widget(self):
        """ Find and return the flow widget child for this widget.

        Returns
        -------
        result : QWidget or None
            The flow widget defined for this widget, or None if one is
            not defined.

        """
        d = self.declaration.flow_widget()
        if d is not None:
            return d.proxy.widget

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtFlowItem.

        """
        super(QtFlowItem, self).child_added(child)
        if isinstance(child, QtContainer):
            self.widget.setFlowWidget(self.flow_widget())

    def child_removed(self, child):
        """ Handle the child added event for a QtFlowItem.

        """
        super(QtFlowItem, self).child_removed(child)
        if isinstance(child, QtContainer):
            self.widget.setFlowWidget(self.flow_widget())

    #--------------------------------------------------------------------------
    # ProxyFlowItem API
    #--------------------------------------------------------------------------
    def set_preferred_size(self, size):
        """ Set the preferred size of the underlying widget.

        """
        self.widget.setPreferredSize(QSize(*size))

    def set_align(self, align):
        """ Set the alignment of the underlying widget.

        """
        self.widget.setAlignment(_ALIGN_MAP[align])

    def set_stretch(self, stretch):
        """ Set the stretch factor of the underlying widget.

        """
        self.widget.setStretch(stretch)

    def set_ortho_stretch(self, stretch):
        """ Set the ortho stretch factor of the underling widget.

        """
        self.widget.setOrthoStretch(stretch)
