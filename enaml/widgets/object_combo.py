#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from future.builtins import str
from atom.api import (
    Bool, Callable, List, Value, Typed, ForwardTyped, set_default, observe
)

from enaml.core.declarative import d_

from .control import Control, ProxyControl


class ProxyObjectCombo(ProxyControl):
    """ The abstract definition of a proxy ObjectCombo object.

    """
    #: A reference to the ObjectCombo declaration.
    declaration = ForwardTyped(lambda: ObjectCombo)

    def set_selected(self, selected):
        raise NotImplementedError

    def set_editable(self, editable):
        raise NotImplementedError

    def request_items_refresh(self):
        raise NotImplementedError


class ObjectCombo(Control):
    """ A drop-down list from which one item can be selected at a time.

    Use a combo box to select a single item from a collection of items.

    """
    #: The list of items to display in the combo box.
    items = d_(List())

    #: The selected item from the list of items. The default will be
    #: the first item in the list of items, or None.
    selected = d_(Value())

    #: The callable to use to convert the items into strings
    #: for display. The default is the builtin 'str'.
    to_string = d_(Callable(str))

    #: The callable to use to convert the items into icons for
    #: display. The default is a lambda which returns None.
    to_icon = d_(Callable(lambda item: None))

    #: Whether the text in the combo box can be edited by the user.
    editable = d_(Bool(False))

    #: A combo box hugs its width weakly by default.
    hug_width = set_default('weak')

    #: A reference to the ProxyObjectCombo object.
    proxy = Typed(ProxyObjectCombo)

    #--------------------------------------------------------------------------
    # Default Value Handlers
    #--------------------------------------------------------------------------
    def _default_selected(self):
        """ The default value handler for the 'selected' member.

        """
        items = self.items
        if len(items) > 0:
            return items[0]

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('items', 'to_string', 'to_icon')
    def _refresh_proxy(self, change):
        """ An observer which requests an items refresh from the proxy.

        """
        if change['type'] == 'update' and self.proxy_is_active:
            self.proxy.request_items_refresh()

    @observe('selected', 'editable')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(ObjectCombo, self)._update_proxy(change)
