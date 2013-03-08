#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .qt.QtCore import QSize
from .qt.QtGui import QListWidget
from .qt_control import QtControl
from .qt_list_item import QtListItem


VIEW_MODES = {
    'list': QListWidget.ListMode,
    'icon': QListWidget.IconMode,
}


RESIZE_MODES = {
    'adjust': QListWidget.Adjust,
    'fixed': QListWidget.Fixed,
}


FLOW_MODES = {
    'left_to_right': QListWidget.LeftToRight,
    'top_to_bottom': QListWidget.TopToBottom,
}


LAYOUT_MODES = {
    'single_pass': QListWidget.SinglePass,
    'batched': QListWidget.Batched,
}


class QtListControl(QtControl):
    """ A Qt implementation of an Enaml ListControl.

    """
    def create_widget(self, parent, tree):
        """ Create the underlying widget.

        """
        # XXX we may want to consider using a QListView with a custom
        # QAbstractListModel, rather than QListWidget. This way maps
        # nicely to the tree structure, but may use more memory than
        # is needed.
        return QListWidget(parent)

    def create(self, tree):
        """ Create and initialize the underlying control.

        """
        super(QtListControl, self).create(tree)
        self.set_view_mode(tree['view_mode'])
        self.set_resize_mode(tree['resize_mode'])
        self.set_flow_mode(tree['flow_mode'])
        self.set_item_wrap(tree['item_wrap'])
        self.set_word_wrap(tree['word_wrap'])
        self.set_item_spacing(tree['item_spacing'])
        self.set_icon_size(tree['icon_size'])
        self.set_uniform_item_sizes(tree['uniform_item_sizes'])
        self.set_layout_mode(tree['layout_mode'])
        self.set_batch_size(tree['batch_size'])

    def init_layout(self):
        """ Initialize the layout of the underlying control.

        """
        super(QtListControl, self).init_layout()
        widget = self.widget()
        for child in self.children():
            if isinstance(child, QtListItem):
                widget.addItem(child.create_item())
                child.initialize_item()

        # Late-bind the signal handlers to avoid doing any unnecessary
        # work while the child items are being intialized.
        widget.itemChanged.connect(self.on_item_changed)
        widget.itemClicked.connect(self.on_item_clicked)
        widget.itemDoubleClicked.connect(self.on_item_double_clicked)

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_removed(self, child):
        """ Handle the child removed event for a QtListControl.

        """
        if not self._destroying and isinstance(child, QtListItem):
            widget = self.widget()
            item = child.item()
            if item is not None:
                row = widget.row(item)
                widget.takeItem(row)

    def child_added(self, child):
        """ Handle the child added event for a QtListControl.

        """
        if isinstance(child, QtListItem):
            row = self.index_of(child)
            item = child.create_item()
            self.widget().insertItem(row, item)
            child.initialize_item()

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
    # Message Handlers
    #--------------------------------------------------------------------------
    def on_action_refresh_items_layout(self, content):
        """ Handle the 'refresh_items_layout' action from the Enaml
        widget.

        """
        self.widget().scheduleDelayedItemsLayout()

    def on_action_set_view_mode(self, content):
        """ Handle the 'set_view_mode' action from the Enaml widget.

        """
        self.set_view_mode(content['view_mode'])

    def on_action_set_resize_mode(self, content):
        """ Handle the 'set_resize_mode' action from the Enaml widget.

        """
        self.set_resize_mode(content['resize_mode'])

    def on_action_set_flow_mode(self, content):
        """ Handle the 'set_flow_mode' action from the Enaml widget.

        """
        self.set_flow_mode(content['flow_mode'])

    def on_action_set_item_wrap(self, content):
        """ Handle the 'set_item_wrap' action from the Enaml widget.

        """
        self.set_item_wrap(content['item_wrap'])

    def on_action_set_word_wrap(self, content):
        """ Handle the 'set_word_wrap' action from the Enaml widget.

        """
        self.set_word_wrap(content['word_wrap'])

    def on_action_set_item_spacing(self, content):
        """ Handle the 'set_item_spacing' action from the Enaml widget.

        """
        self.set_item_spacing(content['item_spacing'])

    def on_action_set_icon_size(self, content):
        """ Handle the 'set_icon_size' action from the Enaml widget.

        """
        self.set_icon_size(content['icon_size'])

    def on_action_set_uniform_item_sizes(self, content):
        """ Handle the 'set_uniform_item_sizes' action from the Enaml
        widget.

        """
        self.set_uniform_item_sizes(content['uniform_item_sizes'])

    def on_action_set_layout_mode(self, content):
        """ Handle the 'set_layout_mode' action from the Enaml widget.

        """
        self.set_layout_mode(content['layout_mode'])

    def on_action_set_batch_size(self, content):
        """ Handle the 'set_batch_size' action from the Enaml widget.

        """
        self.set_batch_size(content['batch_size'])

    #--------------------------------------------------------------------------
    # Widget Update Methods
    #--------------------------------------------------------------------------
    def set_view_mode(self, mode):
        """ Set the view mode of the underlying control.

        """
        # Always set static movement for now. This can be revisited in
        # the future if the need arises to support movable items.
        widget = self.widget()
        widget.setViewMode(VIEW_MODES[mode])
        widget.setMovement(QListWidget.Static)

    def set_resize_mode(self, mode):
        """ Set the resize mode of the underlying control.

        """
        self.widget().setResizeMode(RESIZE_MODES[mode])

    def set_flow_mode(self, mode):
        """ Set the flow mode of the underlying control.

        """
        widget = self.widget()
        if mode == 'default':
            if widget.viewMode() == QListWidget.ListMode:
                qflow = QListWidget.TopToBottom
            else:
                qflow = QListWidget.LeftToRight
        else:
            qflow = FLOW_MODES[mode]
        widget.setFlow(qflow)

    def set_item_wrap(self, wrap):
        """ Set the item wrapping on the underlying control.

        """
        widget = self.widget()
        if wrap is None:
            wrap = widget.viewMode() == QListWidget.IconMode
        widget.setWrapping(wrap)

    def set_word_wrap(self, wrap):
        """ Set the word wrap on the underlying control.

        """
        self.widget().setWordWrap(wrap)

    def set_item_spacing(self, spacing):
        """ Set the item spacing on the underlying control.

        """
        self.widget().setSpacing(spacing)

    def set_icon_size(self, size):
        """ Set the icon size on the underlying control.

        """
        self.widget().setIconSize(QSize(*size))

    def set_uniform_item_sizes(self, uniform):
        """ Set the uniform item sizes flag on the underlying control.

        """
        self.widget().setUniformItemSizes(uniform)

    def set_layout_mode(self, mode):
        """ Set the layout mode on the underlying control.

        """
        self.widget().setLayoutMode(LAYOUT_MODES[mode])

    def set_batch_size(self, size):
        """ Set the batch size on the underlying control.

        """
        self.widget().setBatchSize(size)

