#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Coerced, Enum, Range, observe, set_default

from enaml.core.declarative import d_
from enaml.layout.geometry import Size

from .control import Control
from .list_item import ListItem


class ListControl(Control):
    """ A `ListControl` displays a collection `ListItem` children.

    `ListItem` objects are flexible and convenient, but they are also
    fairly heavy weight. `ListControl` is well suited for use when the
    number of `ListItem` children is under ~1000.

    """
    #: The viewing mode of the list control. The 'list' mode arranges
    #: all items in a vertical list with small icons. The 'icon' mode
    #: uses large icons and a grid layout.
    view_mode = d_(Enum('list', 'icon'))

    #: Whether the items are fixed in place or adjusted during a resize.
    #: A relayout can be manually triggered at any time by calling the
    #: `refresh_item_layout()` method.
    resize_mode = d_(Enum('adjust', 'fixed'))

    #: The flow direction for the layout. A value of 'default' will
    #: allow the toolkit to choose an appropriate value based on the
    #: chosen view mode.
    flow_mode = d_(Enum('default', 'top_to_bottom', 'left_to_right'))

    #: Whether or not the layout items should wrap around at the widget
    #: boundaries. A value of None indicates the toolkit should choose
    #: proper value based on the view mode.
    item_wrap = d_(Enum(None, True, False))

    #: Whether or not the text in the items should wrap at word
    #: boundaries when there is not enough horizontal space.
    word_wrap = d_(Bool(False))

    #: The spacing to place between the items in the widget.
    item_spacing = d_(Range(low=0, value=0))

    #: The size to render the icons in the list control. The default
    #: indicates that the toolkit is free to choose a proper size.
    icon_size = d_(Coerced(Size, factory=lambda: Size(-1, -1)))

    #: Whether or not the items in the model have uniform sizes. If
    #: all the items have uniform size, then the layout algorithm
    #: can be much more efficient on large models. If this is set
    #: to True, but the items do not have uniform sizes, then the
    #: behavior of the layout is undefined.
    uniform_item_sizes = d_(Bool(False))

    #: The behavior used when laying out the items. In 'single_pass'
    #: mode, all items are laid out at once. In 'batch' mode, the
    #: items are laid out in batches of 'batch_size'. Batching can
    #: help make large models appear more interactive, but is not
    #: usually required for moderately sized models.
    layout_mode = d_(Enum('single_pass', 'batched'))

    #: The size of the layout batch when in 'batched' layout mode.
    batch_size = d_(Range(low=0, value=100))

    #: A list control expands freely in height and width by default.
    hug_width = set_default('weak')
    hug_height = set_default('weak')

    @property
    def list_items(self):
        """ A read only property which returns a generator.

        The generator will yield the children of the control which are
        instances of ListItem.

        """
        isinst = isinstance
        target = ListItem
        return (child for child in self.children if isinst(child, target))

    #--------------------------------------------------------------------------
    # Messenger API
    #--------------------------------------------------------------------------
    def snapshot(self):
        """ Returns the snapshot dictionary for the list control.

        """
        snap = super(ListControl, self).snapshot()
        snap['view_mode'] = self.view_mode
        snap['resize_mode'] = self.resize_mode
        snap['flow_mode'] = self.flow_mode
        snap['item_wrap'] = self.item_wrap
        snap['word_wrap'] = self.word_wrap
        snap['item_spacing'] = self.item_spacing
        snap['icon_size'] = self.icon_size
        snap['uniform_item_sizes'] = self.uniform_item_sizes
        snap['layout_mode'] = self.layout_mode
        snap['batch_size'] = self.batch_size
        return snap

    @observe(r'^(view_mode|resize_mode|flow_mode|item_wrap|word_wrap|'
             r'item_spacing|icon_size|uniform_item_sizes|layout_mode|'
             r'batch_size)$', regex=True)
    def send_member_change(self, change):
        """ An observer which sends state change to the client.

        """
        # The superclass handler implementation is sufficient.
        super(ListControl, self).send_member_change(change)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def refresh_items_layout(self):
        """ Request an items layout refresh from the client widget.

        """
        self.send_action('refresh_items_layout', {})

