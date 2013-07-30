#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import deque
import sys
import warnings

from atom.api import Atom, Int, Bool, Coerced, Enum, List, Unicode

from enaml.nodevisitor import NodeVisitor

from .geometry import Rect


def _coerce_rect(value):
    """ Coerce a value to a Rect object.

    This function is a private implementation detail.

    """
    if isinstance(value, (list, tuple)):
        return Rect(*value)
    msg = "cannot coerce '%s' to a 'Rect'"
    raise TypeError(msg % type(value).__name__)


class LayoutNode(Atom):
    """ A base class for defining layout nodes.

    This class provides basic traversal functionality.

    """
    def children(self):
        """ Get the children of the node.

        Returns
        -------
        result : list
            The list of LayoutNode children of the node. The default
            implementation returns an empty list.

        """
        return []

    def traverse(self, depth_first=False):
        """ Yield all of the nodes in the layout, from this node down.

        Parameters
        ----------
        depth_first : bool, optional
            If True, yield the nodes in depth first order. If False,
            yield the nodes in breadth first order. Defaults to False.

        Returns
        -------
        result : generator
            A generator which yields 2-tuples of (parent, node) for all
            nodes in the layout.

        """
        if depth_first:
            stack = [(None, self)]
            stack_pop = stack.pop
            stack_extend = stack.extend
        else:
            stack = deque([(None, self)])
            stack_pop = stack.popleft
            stack_extend = stack.extend
        while stack:
            parent, node = stack_pop()
            yield parent, node
            stack_extend((node, child) for child in node.children())

    def find(self, kind):
        """ Find the first layout node of the given kind.

        Parameters
        ----------
        kind : type or tuple of types
            The type of the layout node to find.

        Returns
        -------
        result : LayoutNode or None
            The first layout node of the given type in the tree. The
            search is performed breadth-first.

        """
        for parent, node in self.traverse():
            if isinstance(node, kind):
                return node

    def find_all(self, kind):
        """ Find the layout nodes of the given kind.

        Parameters
        ----------
        kind : type or tuple of types
            The type of the layout nodes to find.

        Returns
        -------
        result : list
            The list of the layout nodes in the tree which are of the
            request type. They are ordered breadth-first.

        """
        res = []
        for parent, node in self.traverse():
            if isinstance(node, kind):
                res.append(node)
        return res


class ItemLayout(LayoutNode):
    """ A layout object for defining an item layout.

    """
    #: The name of the DockItem to which this layout item applies.
    name = Unicode()

    #: Whether or not the item is floating. An ItemLayout defined as
    #: a toplevel item in a DockLayout should be marked as floating.
    floating = Bool(False)

    #: The geometry to apply to the item. This is expressed in desktop
    #: coordinates and only applies if the item is floating.
    geometry = Coerced(Rect, (-1, -1, -1, -1), coercer=_coerce_rect)

    #: Whether or not the item is linked with its floating neighbors.
    #: This value will only have an effect if the item is floating.
    linked = Bool(False)

    #: Whether or not the item is maximized. This value will only have
    #: effect if the item is floating or docked in a SplitLayout.
    maximized = Bool(False)

    def __init__(self, name, **kwargs):
        super(ItemLayout, self).__init__(name=name, **kwargs)


class TabLayout(LayoutNode):
    """ A layout object for defining tabbed dock layouts.

    """
    #: The position of the tabs in the tab layout.
    tab_position = Enum('top', 'bottom', 'left', 'right')

    #: The index of the currently selected tab.
    index = Int(0)

    #: The list of item layouts to include in the tab layout.
    items = List(Coerced(ItemLayout))

    def __init__(self, *items, **kwargs):
        super(TabLayout, self).__init__(items=list(items), **kwargs)

    def children(self):
        """ Get the list of children of the tab layout.

        """
        return self.items[:]


class _SplitLayoutItem(object):
    """ A private class which performs type checking for split layouts.

    """
    class __metaclass__(type):

        def __instancecheck__(cls, instance):
            return isinstance(instance, (ItemLayout, TabLayout, SplitLayout))

        def __call__(cls, item):
            if isinstance(item, basestring):
                return ItemLayout(item)
            msg = "cannot coerce '%s' to a 'SplitLayout' item"
            raise TypeError(msg % type(item).__name__)


class SplitLayout(LayoutNode):
    """ A layout object for defining split dock layouts.

    """
    #: The orientation of the split layout.
    orientation = Enum('horizontal', 'vertical')

    #: The default sizes to apply to the items in the splitter. If
    #: provided, the length must be equal to the number of items.
    sizes = List(Int())

    #: This list of split layout items to include in the split layout.
    items = List(Coerced(_SplitLayoutItem))

    def __init__(self, *items, **kwargs):
        super(SplitLayout, self).__init__(items=list(items), **kwargs)

    def children(self):
        """ Get the list of children of the split layout.

        """
        return self.items[:]


class HSplitLayout(SplitLayout):
    """ A split layout which defaults to 'horizonal' orientation.

    """
    def __init__(self, *items, **kwargs):
        kwargs['orientation'] = 'horizontal'
        super(HSplitLayout, self).__init__(*items, **kwargs)


class VSplitLayout(SplitLayout):
    """ A split layout which defaults to 'vertical' orientation.

    """
    def __init__(self, *items, **kwargs):
        kwargs['orientation'] = 'vertical'
        super(VSplitLayout, self).__init__(*items, **kwargs)


class DockBarLayout(LayoutNode):
    """ A layout object for defining a dock bar layout.

    """
    #: The position of the tool bar in its area. Only one tool bar may
    #: occupy a given position at any one time.
    position = Enum('top', 'right', 'bottom', 'left')

    #: The list of item layouts to include in the tab layout.
    items = List(Coerced(ItemLayout))

    def __init__(self, *items, **kwargs):
        super(DockBarLayout, self).__init__(items=list(items), **kwargs)

    def children(self):
        """ Get the list of children of the dock bar layout.

        """
        return self.items[:]


class _AreaLayoutItem(object):
    """ A private class which performs type checking for area layouts.

    """
    class __metaclass__(type):

        def __instancecheck__(cls, instance):
            allowed = (type(None), ItemLayout, TabLayout, SplitLayout)
            return isinstance(instance, allowed)

        def __call__(cls, item):
            if isinstance(item, basestring):
                return ItemLayout(item)
            msg = "cannot coerce '%s' to an 'AreaLayout' item"
            raise TypeError(msg % type(item).__name__)


class AreaLayout(LayoutNode):
    """ A layout object for defining a dock area layout.

    """
    #: The main layout item to include in the area layout.
    item = Coerced(_AreaLayoutItem)

    #: The dock bar layouts to include in the area layout.
    dock_bars = List(DockBarLayout)

    #: Whether or not the area is floating. A DockLayout should have
    #: at most one non-floating area layout.
    floating = Bool(False)

    #: The geometry to apply to the area. This is expressed in desktop
    #: coordinates and only applies if the area is floating.
    geometry = Coerced(Rect, (-1, -1, -1, -1), coercer=_coerce_rect)

    #: Whether or not the area is linked with its floating neighbors.
    #: This only has an effect if the area is a floating.
    linked = Bool(False)

    #: Whether or not the area is maximized. This only has an effect if
    #: the area is a floating.
    maximized = Bool(False)

    def __init__(self, item=None, **kwargs):
        super(AreaLayout, self).__init__(item=item, **kwargs)

    def children(self):
        """ Get the list of children of the area layout.

        """
        item = self.item
        base = [item] if item is not None else []
        return base + self.dock_bars


class _DockLayoutItem(object):
    """ A private class which performs type checking for dock layouts.

    """
    class __metaclass__(type):

        def __instancecheck__(cls, instance):
            return isinstance(instance, (ItemLayout, AreaLayout))

        def __call__(cls, item):
            if isinstance(item, basestring):
                return ItemLayout(item)
            if isinstance(item, (SplitLayout, TabLayout)):
                return AreaLayout(item)
            msg = "cannot coerce '%s' to a 'DockLayout' item"
            raise TypeError(msg % type(item).__name__)


class DockLayout(LayoutNode):
    """ The layout object for defining toplevel dock layouts.

    """
    #: The layout items to include in the dock layout.
    items = List(Coerced(_DockLayoutItem))

    def __init__(self, *items, **kwargs):
        super(DockLayout, self).__init__(items=list(items), **kwargs)

    def children(self):
        """ Get the list of children of the dock layout.

        """
        return self.items[:]


class DockLayoutWarning(UserWarning):
    """ A custom user warning for use with dock layouts.

    """
    pass


class DockLayoutValidator(NodeVisitor):
    """ A node visitor which validates a layout.

    If an irregularity or invalid condition is found in the layout, a
    warning is emitted. Such conditions can result in undefined layout
    behavior.

    """
    def __init__(self, available):
        """ Initialize a DockLayoutValidator.

        Parameters
        ----------
        available : iterable
            An iterable of strings which represent the available dock
            item names onto which the layout will be applied. These are
            used to validate the set of visited ItemLayout instances.

        """
        self._available = set(available)

    def warn(self, message):
        """ Emit a dock layout warning with the given message.

        """
        f_globals = self._caller.f_globals
        f_lineno = self._caller.f_lineno
        f_mod = f_globals.get('__name__', '<string>')
        f_name = f_globals.get('__file__')
        if f_name:
            if f_name.lower().endswith((".pyc", ".pyo")):
                f_name = f_name[:-1]
        else:
            if f_mod == "__main__":
                f_name = sys.argv[0]
            if not f_name:
                f_name = f_mod
        warnings.warn_explicit(
            message, DockLayoutWarning, f_name, f_lineno, f_mod, f_globals
        )

    def setup(self, node):
        """ Setup the dock layout validator.

        """
        self._caller = sys._getframe(2)
        self._seen_items = set()
        self._cant_maximize = {}

    def teardown(self, node):
        """ Teardown the dock layout validator.

        """
        for name in self._available - self._seen_items:
            msg = "item '%s' is not referenced by the layout"
            self.warn(msg % name)
        for name in self._seen_items - self._available:
            msg = "item '%s' is not an available layout item"
            self.warn(msg % name)
        del self._caller
        del self._seen_items
        del self._cant_maximize

    def visit_ItemLayout(self, node):
        """ The visitor method for an ItemLayout node.

        """
        if node.name in self._seen_items:
            self.warn("duplicate use of ItemLayout name '%s'" % node.name)
        self._seen_items.add(node.name)
        if not node.floating:
            if -1 not in node.geometry:
                self.warn("non-floating ItemLayout with specific geometry")
            if node.linked:
                self.warn("non-floating ItemLayout marked as linked")
            if node.maximized and node in self._cant_maximize:
                msg = "ItemLayout contained in %s marked as maximized"
                self.warn(msg % self._cant_maximize[node])

    def visit_TabLayout(self, node):
        """ The visitor method for a TabLayout node.

        """
        for item in node.items:
            self._cant_maximize[item] = 'TabLayout'
            self.visit(item)

    def visit_SplitLayout(self, node):
        """ The visitor method for a SplitLayout node.

        """
        if len(node.sizes) > 0:
            if len(node.sizes) != len(node.items):
                self.warn("SplitLayout sizes length != items length")
        for item in node.items:
            if isinstance(item, SplitLayout):
                if item.orientation == node.orientation:
                    msg = "child SplitLayout has same orientation as parent"
                    self.warn(msg)
            self.visit(item)

    def visit_DockBarLayout(self, node):
        """ The visitor method for a DockBarLayout node.

        """
        for item in node.items:
            self._cant_maximize[item] = 'DockBarLayout'
            self.visit(item)

    def visit_AreaLayout(self, node):
        """ The visitor method for an AreaLayout node.

        """
        if not node.floating:
            if -1 not in node.geometry:
                self.warn("non-floating AreaLayout with specific geometry")
            if node.linked:
                self.warn("non-floating AreaLayout marked as linked")
            if node.maximized:
                self.warn("non-floating AreaLayout marked as maximized")
        if node.item is not None:
            self.visit(node.item)
        seen_positions = set()
        for bar in node.dock_bars:
            if bar.position in seen_positions:
                msg = "multiple DockBarLayout items in '%s' position"
                self.warn(msg % bar.position)
            seen_positions.add(bar.position)
            self.visit(bar)

    def visit_DockLayout(self, node):
        """ The visitor method for a DockLayout node.

        """
        has_non_floating_area = False
        for item in node.items:
            if isinstance(item, ItemLayout):
                if not item.floating:
                    self.warn("non-floating toplevel ItemLayout")
            else:  # must be an AreaLayout
                if not item.floating:
                    if has_non_floating_area:
                        self.warn("multiple non-floating AreaLayout items")
                    has_non_floating_area = True
            self.visit(item)


#------------------------------------------------------------------------------
# Dock Layout Operations
#------------------------------------------------------------------------------
class DockLayoutOp(Atom):
    """ A sentinel base class for defining dock layout operations.

    """
    pass


class InsertItem(DockLayoutOp):
    """ A layout operation which inserts an item into a layout.

    This operation will remove an item from the current layout and
    insert it next to a target item. If the item does not exist, the
    operation is a no-op.

    If the target -

    - is a normally docked item
        The item will be inserted as a new split item.

    - is docked in a tab group
        The item will be inserted as a neighbor of the tab group.

    - is docked in a dock bar
        The item will be appended to the dock bar.

    - is a floating dock item
        A new dock area will be created and the item will be inserted
        as a new split item.

    - does not exist
        The item is inserted into the border of the primary dock area.

    """
    #: The name of the dock item to insert into the layout.
    item = Unicode()

    #: The name of the dock item to use as the target location.
    target = Unicode()

    #: The position relative to the target at which to insert the item.
    position = Enum('left', 'top', 'right', 'bottom')


class InsertBorderItem(DockLayoutOp):
    """ A layout operation which inserts an item into an area border.

    This operation will remove an item from the current layout and
    insert it into the border of a dock area. If the item does not
    exist, the operation is a no-op.

    If the target -

    - is a normally docked item
        The item is inserted into the border of the dock area containing
        the target.

    - is docked in a tab group
        The item is inserted into the border of the dock area containing
        the tab group.

    - is docked in a dock bar
        The item is inserted into the border of the dock area containing
        the dock bar.

    - is a floating dock item
        A new dock area will be created and the item will be inserted
        into the border of the new dock area.

    - does not exist
        The item is inserted into the border of the primary dock area.

    """
    #: The name of the dock item to insert into the layout.
    item = Unicode()

    #: The name of the dock item to use as the target location.
    target = Unicode()

    #: The border position at which to insert the item.
    position = Enum('left', 'top', 'right', 'bottom')


class InsertDockBarItem(DockLayoutOp):
    """ A layout operation which inserts an item into a dock bar.

    This operation will remove an item from the current layout and
    insert it into a dock bar in a dock area. If the item does not
    exist, the operation is a no-op.

    If the target -

    - is a normally docked item
        The item is inserted into the dock bar of the dock area
        containing the target.

    - is docked in a tab group
        The item is inserted into the dock bar of the dock area
        containing the tab group.

    - is docked in a dock bar
        The item is inserted into the dock bar of the dock area
        containing the dock bar.

    - is a floating dock item
        A new dock area will be created and the item will be inserted
        into the dock bar of the new dock area.

    - does not exist
        The item is inserted into the dock bar of the primary dock
        area.

    """
    #: The name of the dock item to insert into the layout.
    item = Unicode()

    #: The name of the dock item to use as the target location.
    target = Unicode()

    #: The dock bar position at which to insert the item.
    position = Enum('right', 'left', 'bottom', 'top')

    #: The index at which to insert the dock bar item.
    index = Int(-1)


class InsertTab(DockLayoutOp):
    """ A layout operation which inserts a tab into a tab group.

    This operation will remove an item from the current layout and
    insert it into a tab group in a dock area. If the item does not
    exist, the operation is a no-op.

    If the target -

    - is a normally docked item
        The target and item will be merged into a new tab group
        using the default tab position.

    - is docked in a tab group
        The item will be inserted into the tab group.

    - is docked in a dock bar
        The item will be appended to the dock bar.

    - is a floating dock item
        A new dock area will be created and the target and item will
        be merged into a new tab group.

    - does not exist
        The item is inserted into the left border of the primary dock
        area.

    """
    #: The name of the dock item to insert into the tab group.
    item = Unicode()

    #: The name of an existing dock item in the tab group of interest.
    target = Unicode()

    #: The index at which to insert the dock item.
    index = Int(-1)

    #: The position of the tabs for a newly created tab group.
    tab_position = Enum('default', 'top', 'bottom', 'left', 'right')


class FloatItem(DockLayoutOp):
    """ A layout operation which creates a floating dock item.

    This operation will remove an item from the current layout and
    insert convert it into a floating item. If the item does not
    exist, the operation is a no-op.

    """
    #: The item layout to use when configuring the floating item.
    item = Coerced(ItemLayout)


class FloatArea(DockLayoutOp):
    """ A layout operation which creates a new floating dock area.

    This layout operation will create a new floating dock area using
    the given area layout specification.

    """
    #: The area layout to use when building the new dock area.
    area = Coerced(AreaLayout)


class RemoveItem(DockLayoutOp):
    """ A layout operation which will remove an item from the layout.

    This layout operation will remove the dock item from the layout
    and hide it. It can be added back to layout later with one of the
    other layout operations.

    """
    #: The name of the dock item to remove from the layout.
    item = Unicode()


class ExtendItem(DockLayoutOp):
    """ A layout operation which extends an item in a dock bar.

    This layout operation will cause the named item to be extended to
    from its dock bar. If the item does not exist in a dock bar, this
    operation is a no-op.

    """
    #: The name of the dock item to extend from its dock bar.
    item = Unicode()


class RetractItem(DockLayoutOp):
    """ A layout operation which retracts an item into a dock bar.

    This layout operation will cause the named item to be retracted
    into its dock bar. If the item does not exist in a dock bar, this
    operation is a no-op.

    """
    #: The name of the dock item to retract into its dock bar.
    item = Unicode()


#------------------------------------------------------------------------------
# Deprecated Layout Classes
#------------------------------------------------------------------------------
import os
if os.environ.get('ENAML_DEPRECATED_DOCK_LAYOUT'):

    class dockitem(Atom):
        """ This class is deprecated. Use ItemLayout instead.

        """
        name = Unicode()
        geometry = Coerced(Rect, (-1, -1, -1, -1), coercer=_coerce_rect)
        maximized = Bool(False)
        linked = Bool(False)
        def __init__(self, name, **kwargs):
            super(dockitem, self).__init__(name=name, **kwargs)
        def traverse(self):
            yield self


    def _coerce_item(thing):
        """ This function is deprecated.

        """
        if isinstance(thing, basestring):
            return dockitem(thing)
        msg = "cannot coerce '%s' to a 'dockitem'"
        raise TypeError(msg % type(thing).__name__)


    class docktabs(Atom):
        """ This class is deprecated. Use TabLayout instead.

        """
        tab_position = Enum('top', 'bottom', 'left', 'right')
        index = Int(0)
        children = List(Coerced(dockitem, coercer=_coerce_item))
        def __init__(self, *children, **kwargs):
            super(docktabs, self).__init__(children=list(children), **kwargs)
        def traverse(self):
            yield self
            for child in self.children:
                for item in child.traverse():
                    yield item


    class _splitnode(object):
        """ This class is deprecated.

        """
        class __metaclass__(type):
            def __instancecheck__(cls, instance):
                return isinstance(instance, (dockitem, docktabs, docksplit))
            def __call__(cls, item):
                if isinstance(item, basestring):
                    return dockitem(item)
                msg = "cannot coerce '%s' to a 'docksplit' child"
                raise TypeError(msg % type(item).__name__)


    class docksplit(Atom):
        """ This class is deprecated. Use SplitLayout instead.

        """
        orientation = Enum('horizontal', 'vertical')
        sizes = List(int)
        children = List(Coerced(_splitnode))
        def __init__(self, *children, **kwargs):
            super(docksplit, self).__init__(children=list(children), **kwargs)
        def traverse(self):
            yield self
            for child in self.children:
                for item in child.traverse():
                    yield item


    def hdocksplit(*args, **kwargs):
        """ This function is deprecated.

        """
        kwargs.setdefault('orientation', 'horizontal')
        return docksplit(*args, **kwargs)


    def vdocksplit(*args, **kwargs):
        """ This function is deprecated.

        """
        kwargs.setdefault('orientation', 'vertical')
        return docksplit(*args, **kwargs)


    class _areanode(object):
        """ This class is deprecated.

        """
        class __metaclass__(type):
            def __instancecheck__(cls, instance):
                return isinstance(instance, (dockitem, docktabs, docksplit))
            def __call__(cls, item):
                if isinstance(item, basestring):
                    return dockitem(item)
                msg = "cannot coerce '%s' to a 'dockarea' child"
                raise TypeError(msg % type(item).__name__)


    class dockarea(Atom):
        """ This class is deprecated. Use LayoutArea instead.

        """
        geometry = Coerced(Rect, (-1, -1, -1, -1), coercer=_coerce_rect)
        maximized = Bool(False)
        maximized_item = Unicode()
        linked = Bool(False)
        child = Coerced(_areanode)
        def __init__(self, child, **kwargs):
            super(dockarea, self).__init__(child=child, **kwargs)
        def traverse(self):
            yield self
            for item in self.child.traverse():
                yield item


    class _primarynode(object):
        """ This class is deprecated.

        """
        class __metaclass__(type):
            def __instancecheck__(cls, instance):
                return isinstance(instance, (type(None), dockarea, dockitem))
            def __call__(cls, item):
                if isinstance(item, basestring):
                    return dockitem(item)
                if isinstance(item, (docksplit, docktabs)):
                    return dockarea(item)
                msg = "cannot coerce '%s' to a primary 'docklayout' child"
                raise TypeError(msg % type(item).__name__)


    class _secondarynode(object):
        """ This class is deprecated.

        """
        class __metaclass__(type):
            def __instancecheck__(cls, instance):
                return isinstance(instance, (dockarea, dockitem))
            def __call__(cls, item):
                if isinstance(item, basestring):
                    return dockitem(item)
                if isinstance(item, (docksplit, docktabs)):
                    return dockarea(item)
                msg = "cannot coerce '%s' to a secondary 'docklayout' child"
                raise TypeError(msg % type(item).__name__)


    class docklayout(Atom):
        """ This class is deprecated. Use DockLayout instead.

        """
        primary = Coerced(_primarynode)
        secondary = List(Coerced(_secondarynode))
        def __init__(self, primary, *secondary, **kwargs):
            sup = super(docklayout, self)
            sup.__init__(primary=primary, secondary=list(secondary), **kwargs)
        def traverse(self):
            yield self
            if self.primary is not None:
                for item in self.primary.traverse():
                    yield item
            for secondary in self.secondary:
                for item in secondary.traverse():
                    yield item


    def convert_to_new_docklayout(layout):
        """ A function which converts a 'docklayout' to a 'DockLayout'.

        """
        assert isinstance(layout, docklayout)

        def h_generic(item):
            if isinstance(item, dockitem):
                return h_dockitem(item)
            if isinstance(item, docktabs):
                return h_docktabs(item)
            if isinstance(item, docksplit):
                return h_docksplit(item)
            if isinstance(item, dockarea):
                return h_dockarea(item)
            return h_docklayout(item)

        def h_dockitem(item):
            n_item = ItemLayout(item.name)
            n_item.geometry = item.geometry
            n_item.maximized = item.maximized
            n_item.linked = item.linked
            return n_item

        def h_docktabs(tabs):
            n_tabs = TabLayout()
            n_tabs.items = [h_dockitem(i) for i in tabs.children]
            n_tabs.tab_position = tabs.tab_position
            n_tabs.index = tabs.index
            return n_tabs

        def h_docksplit(split):
            n_split = SplitLayout()
            n_split.items = [h_generic(i) for i in split.children]
            n_split.orientation = split.orientation
            n_split.sizes = split.sizes
            return n_split

        def h_dockarea(area):
            h_area = AreaLayout()
            h_area.item = h_generic(area.child)
            h_area.geometry = area.geometry
            h_area.linked = area.linked
            h_area.maximized = area.maximized
            if area.maximized_item:
                for item in h_area.find_all(ItemLayout):
                    if item.name == area.maximized_item:
                        item.maximized = True
                        break
            return h_area

        def h_docklayout(layout):
            h_layout = DockLayout()
            if layout.primary is not None:
                h_layout.items.append(h_generic(layout.primary))
            for other in layout.secondary:
                h_item = h_generic(other)
                h_item.floating = True
                h_layout.items.append(h_item)
            return h_layout

        return h_generic(layout)

    def convert_to_old_docklayout(layout):
        """ A function which converts a 'DockLayout' to a 'docklayout'.

        """
        assert isinstance(layout, DockLayout)

        def h_generic(item):
            if isinstance(item, ItemLayout):
                return h_ItemLayout(item)
            if isinstance(item, TabLayout):
                return h_TabLayout(item)
            if isinstance(item, SplitLayout):
                return h_SplitLayout(item)
            if isinstance(item, AreaLayout):
                return h_AreaLayout(item)
            return h_DockLayout(item)

        def h_ItemLayout(item):
            n_item = dockitem(item.name)
            n_item.geometry = item.geometry
            n_item.maximized = item.maximized
            n_item.linked = item.linked
            return n_item

        def h_TabLayout(tabs):
            n_tabs = docktabs()
            n_tabs.children = [h_ItemLayout(i) for i in tabs.items]
            n_tabs.tab_position = tabs.tab_position
            n_tabs.index = tabs.index
            return n_tabs

        def h_SplitLayout(split):
            n_split = docksplit()
            n_split.children = [h_generic(i) for i in split.items]
            n_split.orientation = split.orientation
            n_split.sizes = split.sizes
            return n_split

        def h_AreaLayout(area):
            if area.item is None:
                n_area = dockarea(None)
            else:
                n_area = dockarea(h_generic(area.item))
            n_area.geometry = area.geometry
            n_area.linked = area.linked
            n_area.maximized = area.maximized
            for item in area.find_all(ItemLayout):
                if item.maximized:
                    n_area.maximized_item = item.name
                    break
            return n_area

        def h_DockLayout(layout):
            primary = None
            secondary = []
            for item in layout.items:
                n_item = h_generic(item)
                if item.floating or primary is not None:
                    secondary.append(n_item)
                else:
                    primary = n_item
            return docklayout(primary, *secondary)

        return h_generic(layout)
