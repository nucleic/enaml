#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Bool, Coerced, Enum, Range, Int, List, Typed, ForwardTyped, observe,
    set_default
)

from enaml.application import ScheduledTask, schedule
from enaml.core.declarative import d_
from enaml.layout.geometry import Size

from .control import Control, ProxyControl
from .item import Item, ItemModel


class ProxyListControl(ProxyControl):
    """ The abstract definition of a proxy ListControl object.

    """
    #: A reference to the ListControl declaration.
    declaration = ForwardTyped(lambda: ListControl)

    def set_item_model(self, model):
        raise NotImplementedError

    def set_model_column(self, column):
        raise NotImplementedError

    def set_view_mode(self, mode):
        raise NotImplementedError

    def set_resize_mode(self, mode):
        raise NotImplementedError

    def set_flow_mode(self, mode):
        raise NotImplementedError

    def set_item_wrap(self, wrap):
        raise NotImplementedError

    def set_word_wrap(self, wrap):
        raise NotImplementedError

    def set_item_spacing(self, spacing):
        raise NotImplementedError

    def set_icon_size(self, size):
        raise NotImplementedError

    def set_uniform_item_sizes(self, uniform):
        raise NotImplementedError

    def set_layout_mode(self, mode):
        raise NotImplementedError

    def set_batch_size(self, size):
        raise NotImplementedError

    def refresh_items_layout(self):
        raise NotImplementedError


class ListControlItemModel(ItemModel):
    """ A simple item model for use with the ListControl.

    This model provides a simplistic default model implementation for
    the list control which uses the items declared as children of the
    control. For complex use cases, the developer should implement
    their own item model.

    """
    #: The list of items being handled by the model.
    items = List()

    def row_count(self):
        """ Get the row count of the model.

        """
        return len(self.items)

    def column_count(self):
        """ Get the column count of the model.

        """
        return 1

    def item(self, row, column):
        """ Get the item for the given row and column.

        """
        if column == 0:
            return self.items[row]


class ListControl(Control):
    """ A control for displaying a list of Item instances.

    """
    #: The item model to use for the list. If not explicitly given,
    #: one will be created using any given Item children.
    item_model = d_(Typed(ItemModel))

    def _default_item_model(self):
        return ListControlItemModel(items=list(self.items()))

    #: The column index to use for pulling items from the model.
    model_column = d_(Int(0))

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
    icon_size = d_(Coerced(Size, (-1, -1)))

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

    #: A reference to the ProxyListControl object.
    proxy = Typed(ProxyListControl)

    #: A private scheduled task which collapses refresh requests when
    #: the children change and the default list model is in use.
    _refresh_task = Typed(ScheduledTask)

    def items(self):
        """ Get the items defined as children of this control.

        Returns
        -------
        result : generator
            A generator which yields the children which are instances
            of Item.

        """
        for child in self.children:
            if isinstance(child, Item):
                yield child

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe(('item_model', 'model_column', 'view_mode', 'resize_mode',
        'flow_mode', 'item_wrap', 'word_wrap', 'item_spacing', 'icon_size',
        'layout_mode', 'uniform_item_sizes', 'batch_size'))
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(ListControl, self)._update_proxy(change)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def refresh_items_layout(self):
        """ Request an items layout refresh from the client widget.

        """
        if self.proxy_is_active:
            self.proxy.refresh_items_layout()

    def refresh_default_model(self):
        """ Refresh the default item model.

        This method is called automatically at the appropriate times.
        It should rarely need to be called by user code.

        """
        model = self.item_model
        if isinstance(model, ListControlItemModel):
            model.items = list(self.items())
            model.model_reset.emit()

    #--------------------------------------------------------------------------
    # Reimplementations
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event.

        This will trigger an items refresh if the default item model
        is in use. The refresh is collapsed using a scheduled task.

        """
        super(ListControl, self).child_added(child)
        self._refresh_if_needed()

    def child_removed(self, child):
        """ Handle the child added event.

        This will trigger an items refresh if the default item model
        is in use. The refresh is collapsed using a scheduled task.

        """
        super(ListControl, self).child_removed(child)
        self._refresh_if_needed()

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _refresh_if_needed(self):
        """ Trigger a refresh the default item model if needed.

        """
        if self.is_initialized:
            if isinstance(self.item_model, ListControlItemModel):
                if self._refresh_task is None:
                    task = schedule(self.refresh_default_model)
                    task.notify(lambda res: delattr(self, '_refresh_task'))
                    self._refresh_task = task
