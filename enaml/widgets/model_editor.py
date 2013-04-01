#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import defaultdict
from atom.api import (
    Atom, Callable, Enum, Int, List, ForwardTyped, Str, Typed, Value, observe, set_default
)
from atom.datastructures.api import sortedmap

from enaml.core.declarative import Declarative, d_
from enaml.widgets.control import Control, ProxyControl

from .item import Item, ItemModel


class Group(Declarative):
    """  A declarative object for defining a group of editor items.

    A Group is used to declare a set of related Item instances. These
    items are collected by an EditorView to generate a tabular layout
    for editing models.

    """
    def items(self):
        """ Get the Item children defined on the group.

        Returns
        -------
        result : generator
            A generator which yields the child Item instances.

        """
        for child in self.children:
            if isinstance(child, Item):
                yield child

    def item_changed(self, item):
        """ Handle the item changed notification from a child item.

        This handler forwards the change notification to its parent.

        """
        handler = getattr(self.parent, 'item_changed', None)
        if handler is not None:
            handler(item)


class Editor(Declarative):
    """ A declarative object for defining an editor for a model.

    An Editor is composed of Groups of Items. Multiple Editor instances
    are used by an EditorView to create tabular layout of the items.

    """
    #: The model being edited by this editor. This can be redefined in
    #: subclasses and enamldefs to restrict the allowed model types.
    model = d_(Typed(object), final=False)

    #: A mapping of header item to model item object. This mapping is
    #: built by the editor when the headers are resolved.
    item_map = Typed(sortedmap)

    #: A reference to the item model which reads from the editor. This
    #: value is updated when the item model is created.
    item_model = ForwardTyped(lambda: EditorItemModel)

    #: The index of the editor in the item model. The value is updated
    #: when the editor is added to the item model.
    index = Int()

    def groups(self):
        """ Get the Group children defined on this editor.

        Returns
        -------
        result : generator
            A generator which yields the child Group instances.

        """
        for child in self.children:
            if isinstance(child, Group):
                yield child

    def item_changed(self, item):
        """ Handle the item changed notification for a child item.

        This handler forwards the change the editor manager.

        """
        # TODO: trigger and update signal on the item model.
        pass

    def resolve_items(self, headers):
        """ Create the item map from the given headers.

        Parameters
        ----------
        headers : dict

        """
        self.item_map = item_map = sortedmap()
        for group in self.groups():
            group_headers = headers.get(group.name)
            if group_headers is not None:
                for item in group.items():
                    name = item.name
                    header_items = group_headers.get(name)
                    if header_items is not None:
                        for header in header_items:
                            item_map[header] = item


class EditorItemModel(ItemModel):
    """ A class which implements an ItemModel for an EditorView.

    """
    #: The list Item instances for the model headers.
    _headers = List()

    #: The list of Editor instances for the model.
    _editors = List()

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def add_header(self, item):
        self.insert_header(-1, item)

    def insert_header(self, index, item):
        pass

    def add_editor(self, editor):
        self.insert_editor(-1, editor)

    def insert_editor(self, index, editor):
        pass

    #--------------------------------------------------------------------------
    # ItemModel API
    #--------------------------------------------------------------------------
    def row_count(self):
        return len(self._editors)

    def column_count(self):
        return len(self._headers)

    def row_header_item(self, row):
        return None

    def column_header_item(self, column):
        return self._headers[column]

    def item(self, row, column):
        editor = self._editors[row]
        header = self._headers[column]
        return editor.item_map.get(header)


class ProxyEditorView(ProxyControl):
    """ The abstract definition of a proxy EditorView object.

    """
    #: A reference to the EditorView declaration.
    declaration = ForwardTyped(lambda: EditorView)

    def set_item_model(self, model):
        raise NotImplementedError


class EditorView(Control):
    """

    """
    #: The list of model objects to display in this editor view.
    models = d_(List())

    #: A callable which will be invoked with a model and returns an
    #: Editor instance for editing the provided model.
    factory = d_(Callable())

    #: The mode for header building. The 'explicit' mode indicates that
    #: headers will be explicitly provided by the developer by defining
    #: groups of items as children. The 'implicit' mode indicates that
    #: the headers should be implicitly created based on the structure
    #: of the model editors. The default is 'explicit'.
    header_mode = d_(Enum('explicit', 'implicit'))

    #: The item model for the view. This model is generated by the view
    #: and should not be manipulated directly by user code.
    item_model = Typed(EditorItemModel)

    #: An editor view expands freely in width and height by default.
    hug_width = set_default('ignore')
    hug_height = set_default('ignore')

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def initialize(self):
        super(EditorView, self).initialize()

        # Create the editors for the model.
        factory = self.factory
        editors = [factory(model) for model in self.models]

        # Compute the header dict for the model. Each header is given
        # a temporary index so that the headers can retain order.
        headers = []
        header_dct = {}
        if self.header_mode == 'explicit':
            for group in self.groups():
                group_dct = header_dct.setdefault(group.name, {})
                for item in group.items():
                    group_dct.setdefault(item.name, []).append(item)
                    headers.append(item)

        # Resolve the items for each of the editors.
        for editor in editors:
            editor.initialize()
            editor.resolve_items(header_dct)

        self.item_model = EditorItemModel(_editors=editors, _headers=headers)

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def groups(self):
        """ Get the Group children defined on this editor view.

        Returns
        -------
        result : generator
            A generator which yields the child Group instances.

        """
        for child in self.children:
            if isinstance(child, Group):
                yield child
