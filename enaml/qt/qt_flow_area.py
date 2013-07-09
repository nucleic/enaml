#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from enaml.widgets.flow_area import ProxyFlowArea

from .QtCore import QEvent, QPoint, QRect
from .QtGui import QScrollArea, QWidget, QPainter, QPalette, QApplication

from .qt_frame import QtFrame
from .qt_flow_item import QtFlowItem
from .q_flow_layout import QFlowLayout


_DIRECTION_MAP = {
    'left_to_right': QFlowLayout.LeftToRight,
    'right_to_left': QFlowLayout.RightToLeft,
    'top_to_bottom': QFlowLayout.TopToBottom,
    'bottom_to_top': QFlowLayout.BottomToTop,
}


_ALIGN_MAP = {
    'leading': QFlowLayout.AlignLeading,
    'trailing': QFlowLayout.AlignTrailing,
    'center': QFlowLayout.AlignCenter,
    'justify': QFlowLayout.AlignJustify,
}


class QFlowArea(QScrollArea):
    """ A custom QScrollArea which implements a flowing layout.

    """
    def __init__(self, parent=None):
        """ Initialize a QFlowArea.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget of this widget.

        """
        super(QFlowArea, self).__init__(parent)
        self._widget = QWidget(self)
        self._layout = QFlowLayout()
        self._widget.setLayout(self._layout)
        self.setWidgetResizable(True)
        self.setWidget(self._widget)
        # setWidget sets autoFillBackground to True
        self._widget.setAutoFillBackground(False)

    def event(self, event):
        """ A custom event handler for the flow area.

        This handler paints the empty corner between the scroll bars.

        """
        res = super(QFlowArea, self).event(event)
        if event.type() == QEvent.Paint:
            # Fill in the empty corner area with the app window color.
            color = QApplication.palette().color(QPalette.Window)
            tl = self.viewport().geometry().bottomRight()
            fw = self.frameWidth()
            br = self.rect().bottomRight() - QPoint(fw, fw)
            QPainter(self).fillRect(QRect(tl, br), color)
        return res

    def layout(self):
        """ Get the layout for this flow area.

        The majority of interaction for a QFlowArea takes place through
        its layout, rather than through the widget itself.

        Returns
        -------
        result : QFlowLayout
            The flow layout for this flow area.

        """
        return self._layout

    def setLayout(self, layout):
        """ A reimplemented method. Setting the layout on a QFlowArea
        is not supported.

        """
        raise TypeError("Cannot set layout on a QFlowArea.")


class QtFlowArea(QtFrame, ProxyFlowArea):
    """ A Qt implementation of an Enaml ProxyFlowArea.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QFlowArea)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying widget.

        """
        self.widget = QFlowArea(self.parent_widget())

    def init_widget(self):
        """ Initialize the underlying control.

        """
        super(QtFlowArea, self).init_widget()
        d = self.declaration
        self.set_direction(d.direction)
        self.set_align(d.align)
        self.set_horizontal_spacing(d.horizontal_spacing)
        self.set_vertical_spacing(d.vertical_spacing)
        self.set_margins(d.margins)

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(QtFlowArea, self).init_layout()
        layout = self.widget.layout()
        for child in self.children():
            if isinstance(child, QtFlowItem):
                layout.addWidget(child.widget)

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtMdiArea.

        """
        super(QtFlowArea, self).child_added(child)
        if isinstance(child, QtFlowItem):
            for index, dchild in enumerate(self.children()):
                if dchild is child:
                    self.widget.layout().insertWidget(index, child.widget)

    def child_removed(self, child):
        """ Handle the child removed event for a QtMdiArea.

        """
        super(QtFlowArea, self).child_removed(child)
        if isinstance(child, QtFlowItem) and child.widget is not None:
            self.widget.layout().removeWidget(child.widget)

    #--------------------------------------------------------------------------
    # ProxyFlowArea API
    #--------------------------------------------------------------------------
    def set_direction(self, direction):
        """ Set the direction for the underlying control.

        """
        self.widget.layout().setDirection(_DIRECTION_MAP[direction])

    def set_align(self, align):
        """ Set the alignment for the underlying control.

        """
        self.widget.layout().setAlignment(_ALIGN_MAP[align])

    def set_horizontal_spacing(self, spacing):
        """ Set the horizontal spacing of the underyling control.

        """
        self.widget.layout().setHorizontalSpacing(spacing)

    def set_vertical_spacing(self, spacing):
        """ Set the vertical spacing of the underlying control.

        """
        self.widget.layout().setVerticalSpacing(spacing)

    def set_margins(self, margins):
        """ Set the margins of the underlying control.

        """
        top, right, bottom, left = margins
        self.widget.layout().setContentsMargins(left, top, right, bottom)

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def replace_constraints(self, old_cns, new_cns):
        """ A reimplemented QtConstraintsWidget layout method.

        Constraints layout may not cross the boundary of a FlowArea,
        so this method is no-op which stops the layout propagation.

        """
        pass
