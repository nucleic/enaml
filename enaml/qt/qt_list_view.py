#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import QSize
from PyQt4.QtGui import QListView

from atom.api import Typed

from enaml.widgets.list_view import ProxyListView

from .q_item_model_wrapper import QItemModelWrapper
from .qt_control import QtControl


VIEW_MODES = {
    'list': QListView.ListMode,
    'icon': QListView.IconMode,
}


RESIZE_MODES = {
    'adjust': QListView.Adjust,
    'fixed': QListView.Fixed,
}


FLOW_MODES = {
    'left_to_right': QListView.LeftToRight,
    'top_to_bottom': QListView.TopToBottom,
}


LAYOUT_MODES = {
    'single_pass': QListView.SinglePass,
    'batched': QListView.Batched,
}


class QtListView(QtControl, ProxyListView):
    """ A Qt implementation of an Enaml ProxyListView.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QListView)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying widget.

        """
        self.widget = QListView(self.parent_widget())

    def init_widget(self):
        """ Create and initialize the underlying control.

        """
        super(QtListView, self).init_widget()
        d = self.declaration
        self.set_item_model(d.item_model)
        self.set_model_column(d.model_column)
        self.set_view_mode(d.view_mode)
        self.set_resize_mode(d.resize_mode)
        self.set_flow_mode(d.flow_mode)
        self.set_item_wrap(d.item_wrap)
        self.set_word_wrap(d.word_wrap)
        self.set_item_spacing(d.item_spacing)
        self.set_icon_size(d.icon_size)
        self.set_uniform_item_sizes(d.uniform_item_sizes)
        self.set_layout_mode(d.layout_mode)
        self.set_batch_size(d.batch_size)

    #--------------------------------------------------------------------------
    # Signal Handlers
    #--------------------------------------------------------------------------
    def on_item_changed(self, item):
        """ The signal handler for the `itemChanged` signal.

        This handler forwards the call to the item that was changed.

        """
        owner = getattr(item, 'item_owner', None)
        if owner is not None:
            owner.on_changed()

    def on_item_clicked(self, item):
        """ The signal handler for the `itemClicked` signal.

        This handler forwards the call to the item that was clicked.

        """
        owner = getattr(item, 'item_owner', None)
        if owner is not None:
            owner.on_clicked()

    def on_item_double_clicked(self, item):
        """ The signal handler for the `itemDoubleClicked` signal.

        This handler forwards the call to the item that was clicked.

        """
        owner = getattr(item, 'item_owner', None)
        if owner is not None:
            owner.on_double_clicked()

    #--------------------------------------------------------------------------
    # ProxyListView API
    #--------------------------------------------------------------------------
    def set_item_model(self, model):
        """ Set the item model for the widget.

        """
        if not model:
            self.widget.setModel(None)
        else:
            self.widget.setModel(QItemModelWrapper(model))

    def set_model_column(self, column):
        """ Set the model column for the widget.

        """
        self.widget.setModelColumn(column)

    def set_view_mode(self, mode):
        """ Set the view mode of the underlying control.

        """
        # Always set static movement for now. This can be revisited in
        # the future if the need arises to support movable items.
        widget = self.widget
        widget.setViewMode(VIEW_MODES[mode])
        widget.setMovement(QListView.Static)

    def set_resize_mode(self, mode):
        """ Set the resize mode of the underlying control.

        """
        self.widget.setResizeMode(RESIZE_MODES[mode])

    def set_flow_mode(self, mode):
        """ Set the flow mode of the underlying control.

        """
        if mode == 'default':
            if self.widget.viewMode() == QListView.ListMode:
                qflow = QListView.TopToBottom
            else:
                qflow = QListView.LeftToRight
        else:
            qflow = FLOW_MODES[mode]
        self.widget.setFlow(qflow)

    def set_item_wrap(self, wrap):
        """ Set the item wrapping on the underlying control.

        """
        if wrap is None:
            wrap = self.widget.viewMode() == QListView.IconMode
        self.widget.setWrapping(wrap)

    def set_word_wrap(self, wrap):
        """ Set the word wrap on the underlying control.

        """
        self.widget.setWordWrap(wrap)

    def set_item_spacing(self, spacing):
        """ Set the item spacing on the underlying control.

        """
        self.widget.setSpacing(spacing)

    def set_icon_size(self, size):
        """ Set the icon size on the underlying control.

        """
        self.widget.setIconSize(QSize(*size))

    def set_uniform_item_sizes(self, uniform):
        """ Set the uniform item sizes flag on the underlying control.

        """
        self.widget.setUniformItemSizes(uniform)

    def set_layout_mode(self, mode):
        """ Set the layout mode on the underlying control.

        """
        self.widget.setLayoutMode(LAYOUT_MODES[mode])

    def set_batch_size(self, size):
        """ Set the batch size on the underlying control.

        """
        self.widget.setBatchSize(size)

    def refresh_items_layout(self):
        """ Refresh the items layout.

        """
        pass
