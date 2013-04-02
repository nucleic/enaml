#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import (
    Callable, Enum, Int, List, ForwardTyped, Typed, set_default
)
from atom.datastructures.api import sortedmap

from enaml.core.declarative import Declarative, d_

from .control import Control, ProxyControl
from .item import Item, ItemModel


class ViewTableModel(ItemModel):
    """ A class which implements an ItemModel for a ViewTable.

    This class is an implementation detail of the View and ViewTable
    classes. It should not typically be used directly by user code.

    """
    #: The orientation of the model. In a horizontal model, the views
    #: are layed out as rows. In a vertical model, the views are layed
    #: out as columns. The default is horizontal.
    orientation = Enum('horizontal', 'vertical')

    #: The list Item instances for the model headers. This list is
    #: manipulated directly by the ViewTable which created the model.
    headers = List()

    #: The list of View instances for the model. This list is
    #: manipulated directly by the ViewTable which created the model.
    views = List()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def view_changed(self, view):
        """ A method which can be called when a View changes.

        This method will emit the 'data_changed' signal on completion.

        Parameters
        ----------
        view : View
            The view object which owns the items which have changed.

        """
        index = view.index
        if self.views[index] is not view:
            view.index = index = self.views.index(view)
        if self.orientation == 'horizontal':
            start = (index, 0)
            end = (index, len(self.headers))
        else:
            start = (0, index)
            end = (len(self.headers), index)
        self.data_changed.emit(start, end)

    def update(self, headers=None, views=None, orientation=None):
        """ Update the data to use for the model.

        This method will emit the 'model_reset' signal on completion.

        Parameters
        ----------
        headers : list or None
            A list of Item instances which are the headers for the model
            or None if the headers should not be updated.

        views : list or None
            A list of View instances which are the views for the model
            or None if the views should not be updated.

        orientation : str or None
            The new orientation of the model, or None if the orientation
            should not be changed.

        """
        if headers is not None:
            self.headers = headers
        if views is not None:
            self.views = views
        if orientation is not None:
            self.orientation = orientation
        self.model_reset.emit()

    #--------------------------------------------------------------------------
    # ItemModel API
    #--------------------------------------------------------------------------
    def row_count(self):
        if self.orientation == 'horizontal':
            return len(self.views)
        return len(self.headers)

    def column_count(self):
        if self.orientation == 'horizontal':
            return len(self.headers)
        return len(self.views)

    def row_header_item(self, row):
        if self.orientation == 'horizontal':
            return None
        return self.headers[row]

    def column_header_item(self, column):
        if self.orientation == 'horizontal':
            return self.headers[column]
        return None

    def item(self, row, column):
        if self.orientation == 'horizontal':
            view = self.views[row]
            header = self.headers[column]
        else:
            view = self.views[column]
            header = self.headers[row]
        return view.item_map.get(header)


class View(Declarative):
    """ A declarative object for defining an item view for a model.

    A View is composed of a model object and Item children. The Item
    children are used to view and edit the data in the model.

    """
    #: The model being handled by this view. This can be redefined in
    #: subclasses and enamldefs to restrict the allowed model types.
    model = d_(Typed(object), final=False)

    #: A reference to the table model which is consuming this view.
    table_model = Typed(ViewTableModel)

    #: The index of the view in the table model. The value is updated
    #: when the view is added to the table model.
    index = Int()

    #: The item map generated for the headers in used by the model.
    #: This should not typically be manipulated by user code.
    item_map = Typed(sortedmap)

    def items(self):
        """ Get the Item children defined on the view.

        Returns
        -------
        result : generator
            A generator which yields the child Item instances.

        """
        for child in self.children:
            if isinstance(child, Item):
                yield child

    def item_changed(self, item):
        """ Handle the item changed notification for a child item.

        """
        # The invalidation occurs on the view level instead of the
        # item level. This removes the need to keep a back mapping
        # from item to header which would be costly in heap size.
        model = self.table_model
        if model is not None:
            model.view_changed(self)

    def resolve(self, headers):
        """ Resolve the item map for the given headers.

        """
        items = {}
        for item in self.items():
            items[item.name] = item
        item_map = self.item_map = sortedmap()
        for header in headers:
            item = items.get(header.name)
            if item is not None:
                item_map[header] = item


class ViewTableHeaders(Declarative):
    """ A declarative class for defining headers for a Table.

    """
    #: A callable which will generate the items for the headers in lieu
    #: of using any items defined as declarative children. The callable
    #: will be passed the list of views and should return a list of Item
    #: instances. The name of the items will be matched against the name
    #: of the view items to determine the item to use for a given cell.
    factory = d_(Callable())

    def items(self):
        """ Get the Item children defined as the headers.

        Returns
        -------
        result : generator
            A generator which yields the child Item instances.

        """
        for child in self.children:
            if isinstance(child, Item):
                yield child

    def resolve(self, views):
        """ Resolve the header items for the given list of views.

        If there is no factory defined for the headers, the child list
        of items will be returned. Otherwise, the factory will be called
        with the given list of views to generate the headers.

        """
        factory = self.factory
        if factory is not None:
            return factory(views)
        return list(self.items())


class ProxyViewTable(ProxyControl):
    """ The abstract definition of a proxy ViewTable object.

    """
    #: A reference to the Table declaration.
    declaration = ForwardTyped(lambda: ViewTable)

    def set_table_model(self, model):
        raise NotImplementedError

    def set_orientation(self, orientation):
        raise NotImplementedError


class ViewTable(Control):
    """ A UI control for displaying a collection of views in a table.

    """
    #: The orientation of the table. In a horizontal table, the views
    #: are layed out as rows. In a vertical table, the views are layed
    #: out as columns. The default is horizontal.
    orientation = d_(Enum('horizontal', 'vertical'))

    #: The list of model objects to display in this view table.
    models = d_(List())

    #: A callable which will be invoked with a model instance and should
    #: return a View instance for viewing the model in the table.
    factory = d_(Callable())

    #: The table model for the control. This model is generated by the
    #: control and should not be manipulated directly by user code.
    table_model = Typed(ViewTableModel, ())

    #: An editor view expands freely in width and height by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #: A reference to the ProxyViewTable object.
    proxy = Typed(ProxyViewTable)

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _observe_orientation(self, change):
        """ An orientation observer.

        This observer will update the orientation of the table model
        and then dispatch to the proxy updater.

        """
        if self.is_initialized:
            self.table_model.update(orientation=self.orientation)
            self._update_proxy(change)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def initialize(self):
        """ Initialize the Table control.

        """
        super(ViewTable, self).initialize()
        factory = self.factory
        views = []
        for model in self.models:
            view = factory(model)
            view.initialize()
            views.append(view)
        headers = []
        for header in self.headers():
            headers.extend(header.resolve(views))
        table_model = self.table_model
        for index, view in enumerate(views):
            view.resolve(headers)
            view.index = index
            view.table_model = table_model
        table_model.update(headers, views, self.orientation)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def headers(self):
        """ Get the TableHeaders defined as children of the table.

        Returns
        -------
        result : generator
            A generator which yields the child TableHeaders.

        """
        for child in self.children:
            if isinstance(child, ViewTableHeaders):
                yield child
