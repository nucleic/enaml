#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed, ForwardTyped, observe, set_default

from enaml.core.declarative import d_
from enaml.itemmodels.abstractitemmodel import AbstractItemModel


from .control import Control, ProxyControl


class ProxyTableView(ProxyControl):
    """ The abstract definition of a proxy ListView object.

    """
    #: A reference to the ListView declaration.
    declaration = ForwardTyped(lambda: TableView)

    def set_item_model(self, model):
        raise NotImplementedError


class TableView(Control):
    """ A control for displaying a list of data.

    """
    #: The data model to use for the list. If not explicitly given,
    #: one will be created using any given ListItem children.
    item_model = d_(Typed(AbstractItemModel))

    #: A reference to the ProxyListView object.
    proxy = Typed(ProxyTableView)

    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #--------------------------------------------------------------------------
    # Observers
    #--------------------------------------------------------------------------
    @observe('item_model')
    def _update_proxy(self, change):
        """ An observer which sends state change to the proxy.

        """
        # The superclass handler implementation is sufficient.
        super(TableView, self)._update_proxy(change)
