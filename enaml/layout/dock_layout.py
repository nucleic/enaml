#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys
import warnings

from atom.api import Atom, Int, Bool, Coerced, Enum, List, Unicode

from .geometry import Rect


def _coerce_rect(value):
    """ Coerce a value to a Rect object.

    This function is a private implementation detail.

    """
    if isinstance(value, (list, tuple)):
        return Rect(*value)
    msg = "cannot coerce '%s' to a 'Rect'"
    raise TypeError(msg % type(value).__name__)


class ItemLayout(Atom):
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


class TabLayout(Atom):
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


class SplitLayout(Atom):
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


class DockBarLayout(Atom):
    """ A layout object for defining a dock bar layout.

    """
    #: The position of the tool bar in its area. Only one tool bar may
    #: occupy a given position at any one time.
    position = Enum('top', 'right', 'bottom', 'left')

    #: The list of item layouts to include in the tab layout.
    items = List(Coerced(ItemLayout))

    def __init__(self, *items, **kwargs):
        super(DockBarLayout, self).__init__(items=list(items), **kwargs)


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


class AreaLayout(Atom):
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


class DockLayout(Atom):
    """ The layout object for defining toplevel dock layouts.

    """
    #: The layout items to include in the dock layout.
    items = List(Coerced(_DockLayoutItem))

    def __init__(self, *items, **kwargs):
        super(DockLayout, self).__init__(items=list(items), **kwargs)


class DockLayoutVisitor(object):
    """ A base class for implementing dock layout visitors.

    Subclasses should implement visitor methods using the naming
    scheme 'visit_<name>' where `<name>` is the class name of the
    node of interest.

    """
    def run(self, node):
        """ The main entry point of the visitor class.

        This method should be called to execute the logic of the
        visitor. It will call the setup and teardown methods before
        and after invoking the visit method on the node.

        Parameter
        ---------
        node : object
            An instance of one of the dock layout classes over which
            the visitor should be run.

        """
        self.setup(node)
        self.visit(node)
        self.teardown(node)

    def setup(self, node):
        """ Perform any necessary setup before running the visitor.

        This method is invoked before the visitor is executed over
        a particular node. The default implementation does nothing.

        Parameters
        ----------
        node : object
            The dock layout node passed to the 'run' method.

        """
        pass

    def teardown(self, node):
        """ Perform any necessary cleanup when the visitor is finished.

        This method is invoked after the visitor is executed over a
        particular node. The default implementation does nothing.

        Parameters
        ----------
        node : object
            The dock layout node passed to the 'run' method.

        """
        pass

    def visit(self, node):
        """ The main visitor dispatch method.

        Parameters
        ----------
        node : object
            An instance of a dock layout class.

        """
        for cls in type(node).mro():
            visitor_name = 'visit_' + cls.__name__
            visitor = getattr(self, visitor_name, None)
            if visitor is not None:
                visitor(node)
                return
        self.default_visit(node)

    def default_visit(self, node):
        """ The default node visitor method.

        This method is invoked when no named visitor method is found
        for a given node. This default behavior raises an exception
        for the missing handler. Subclasses may reimplement this
        method for custom default behavior.

        """
        msg = "no visitor found for node of type `%s`"
        raise TypeError(msg % type(node).__name__)


class DockLayoutWarning(warnings.UserWarning):
    """ A custom user warning for use with dock layouts.

    """
    pass


class DockLayoutValidator(DockLayoutVisitor):
    """ A layout visitor which validates a layout.

    If an irregularity or invalid condition is found in the layout, a
    warning is emitted. These warnings should be heeded, since the
    condition can lead to undefined layout behavior.

    """
    def warn(self, message):
        """ Emit a dock layout warning with the given message.

        """
        code = self._caller.f_code
        f_name = code.co_filename
        f_lineno = code.co_firstlineno
        warnings.warn_explicit(message, DockLayoutWarning, f_name, f_lineno)

    def setup(self, node):
        """ Setup the dock layout validator.

        """
        self._caller = sys._getframe(3) # caller->run()->setup()
        self._seen_items = set()
        self._cant_maximize = {}

    def teardown(self, node):
        """ Teardown the dock layout validator.

        """
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
                msg = "ItemLayout used in %s but marked as maximized"
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
            if len(node.size) != len(node.items):
                self.warn("SplitLayout sizes length != items length")
        for item in node.items:
            self.visit(item)

    def visit_DockBarLayout(self, node):
        """ The visitor method for a DockBarLayout node.

        """
        for item in node.items:
            self._cant_maximize[node] = 'DockBarLayout'
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
# Deprecated Layout Classes
#------------------------------------------------------------------------------
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
