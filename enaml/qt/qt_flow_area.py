#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtGui import QScrollArea, QFrame
from .qt_constraints_widget import QtConstraintsWidget
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
        self._widget = QFrame(self)
        self._layout = QFlowLayout()
        self._widget.setLayout(self._layout)
        self.setWidgetResizable(True)
        self.setWidget(self._widget)

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


class QtFlowArea(QtConstraintsWidget):
    """ A Qt implementation of an Enaml FlowArea.

    """
    #--------------------------------------------------------------------------
    # Setup Methods
    #--------------------------------------------------------------------------
    def create_widget(self, parent, tree):
        """ Create the underlying widget.

        """
        return QFlowArea(parent)

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(QtFlowArea, self).create(tree)
        self.set_direction(tree['direction'])
        self.set_align(tree['align'])
        self.set_horizontal_spacing(tree['horizontal_spacing'])
        self.set_vertical_spacing(tree['vertical_spacing'])
        self.set_margins(tree['margins'])

    def init_layout(self):
        """ Initialize the layout for the underlying control.

        """
        super(QtFlowArea, self).init_layout()
        layout = self.widget().layout()
        for child in self.children():
            if isinstance(child, QtFlowItem):
                layout.addWidget(child.widget())

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtMdiArea.

        """
        if isinstance(child, QtFlowItem):
            self.widget().layout().removeWidget(child.widget())

    def child_added(self, child):
        """ Handle the child added event for a QtMdiArea.

        """
        if isinstance(child, QtFlowItem):
            index = self.index_of(child)
            self.widget().layout().insertWidget(index, child.widget())

    #--------------------------------------------------------------------------
    # Message Handling
    #--------------------------------------------------------------------------
    def on_action_set_direction(self, content):
        """ Handle the 'set_direction' action from the Enaml widget.

        """
        self.set_direction(content['direction'])

    def on_action_set_align(self, content):
        """ Handle the 'set_align' action from the Enaml widget.

        """
        self.set_align(content['align'])

    def on_action_set_horizontal_spacing(self, content):
        """ Handle the 'set_horizontal_spacing' action from the Enaml
        widget.

        """
        self.set_horizontal_spacing(content['horizontal_spacing'])

    def on_action_set_vertical_spacing(self, content):
        """ Handle the 'set_vertical_spacing' action from the Enaml
        widget.

        """
        self.set_vertical_spacing(content['vertical_spacing'])

    def on_action_set_margins(self, content):
        """ Handle the 'set_margins' action from the Enaml widget.

        """
        self.set_margins(content['margins'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_direction(self, direction):
        """ Set the direction for the underlying control.

        """
        self.widget().layout().setDirection(_DIRECTION_MAP[direction])

    def set_align(self, align):
        """ Set the alignment for the underlying control.

        """
        self.widget().layout().setAlignment(_ALIGN_MAP[align])

    def set_horizontal_spacing(self, spacing):
        """ Set the horizontal spacing of the underyling control.

        """
        self.widget().layout().setHorizontalSpacing(spacing)

    def set_vertical_spacing(self, spacing):
        """ Set the vertical spacing of the underlying control.

        """
        self.widget().layout().setVerticalSpacing(spacing)

    def set_margins(self, margins):
        """ Set the margins of the underlying control.

        """
        top, right, bottom, left = margins
        self.widget().layout().setContentsMargins(left, top, right, bottom)

    #--------------------------------------------------------------------------
    # Overrides
    #--------------------------------------------------------------------------
    def replace_constraints(self, old_cns, new_cns):
        """ A reimplemented QtConstraintsWidget layout method.

        Constraints layout may not cross the boundary of a FlowArea,
        so this method is no-op which stops the layout propagation.

        """
        pass

    def clear_constraints(self, cns):
        """ A reimplemented QtConstraintsWidget layout method.

        Constraints layout may not cross the boundary of a FlowArea,
        so this method is no-op which stops the layout propagation.

        """
        pass

