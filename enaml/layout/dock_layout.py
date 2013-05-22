#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
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


class dockitem(Atom):
    """ A layout node for declaring a dock layout item.

    """
    #: The name of the item referenced in the layout.
    name = Unicode()

    #: The geometry to apply to the item. This only has an effect if
    #: the dock item is a floating item.
    geometry = Coerced(Rect, (-1, -1, -1, -1), coercer=_coerce_rect)

    #: Whether or not the item is maximized. This only has an effect
    #: if the dock item is a floating item.
    maximized = Bool(False)

    def __init__(self, name, **kwargs):
        """ Initialize an item.

        Parameters
        ----------
        name : unicode
            The unicode name of the dock item to include in the layout.

        **kwargs
            Additional configuration data for the item layout.

        """
        super(dockitem, self).__init__(name=name, **kwargs)

    def traverse(self):
        """ Traverse the layout in a top-down fashion.

        Returns
        -------
        result : generator
            A generator which will yields the dockitem.

        """
        yield self


def _coerce_item(thing):
    """ A function for coercing a thing into a dockitem.

    This function is a private implementation detail.

    """
    if isinstance(thing, basestring):
        return dockitem(thing)
    msg = "cannot coerce '%s' to a 'dockitem'"
    raise TypeError(msg % type(thing).__name__)


class docktabs(Atom):
    """ A layout node for declaring a tabbed layout item.

    """
    #: The position of the tabs in the widget.
    tab_position = Enum('top', 'bottom', 'left', 'right')

    #: The index of the currently selected tab.
    index = Int(0)

    #: The child layout items to add to the tab layout.
    children = List(Coerced(dockitem, coercer=_coerce_item))

    def __init__(self, *children, **kwargs):
        """ Initialize a docktabs layout.

        Parameters
        ----------
        *children
            The child layout items to add to the layout. The allowed
            types are 'basestring' and 'dockitem'.

        **kwargs
            Additional configuration data for the layout.

        """
        super(docktabs, self).__init__(children=list(children), **kwargs)

    def traverse(self):
        """ Traverse the layout in a top-down fashion.

        Returns
        -------
        result : generator
            A generator which will yield all of the layout nodes in
            the docktabs.

        """
        yield self
        for child in self.children:
            for item in child.traverse():
                yield item


class _splitnode(object):
    """ A typeclass which implements type checking for dock splits.

    This class is a private implementation detail.

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
    """ A layout node for declaring a splitter layout item.

    """
    #: The orientation of the splitter.
    orientation = Enum('horizontal', 'vertical')

    #: The default sizes to apply to the splitter. The length should
    #: be equal to the number of children declared for the splitter.
    sizes = List(int)

    #: The child layout items to add to the splitter.
    children = List(Coerced(_splitnode))

    def __init__(self, *children, **kwargs):
        """ Initialize a split layout.

        Parameters
        ----------
        *children
            The children to add to the layout. The allowed child types
            are 'basestring', 'docksplit', 'docktabs', and 'dockitem'.

        **kwargs
            Additional configuration data for the layout.

        """
        super(docksplit, self).__init__(children=list(children), **kwargs)

    def traverse(self):
        """ Traverse the layout in a top-down fashion.

        Returns
        -------
        result : generator
            A generator which will yield all of the layout nodes in
            the docksplit.

        """
        yield self
        for child in self.children:
            for item in child.traverse():
                yield item


def hdocksplit(*args, **kwargs):
    """ A convenience function for creating a horizontal docksplit.

    """
    kwargs.setdefault('orientation', 'horizontal')
    return docksplit(*args, **kwargs)


def vdocksplit(*args, **kwargs):
    """ A convenience function for creating a vertical docksplit.

    """
    kwargs.setdefault('orientation', 'vertical')
    return docksplit(*args, **kwargs)


class _areanode(object):
    """ A typeclass which implements type checking for dock areas.

    This class is a private implementation detail.

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
    """ A layout node for declaring a dock layout area.

    """
    #: The geometry to apply to the area. This only has an effect if
    #: the dock area is a floating area.
    geometry = Coerced(Rect, (-1, -1, -1, -1), coercer=_coerce_rect)

    #: Whether or not the dock area is maximized. This only has an
    #: effect if the dock area is a floating area.
    maximized = Bool(False)

    #: The name of the dock item that is maximized in the dock area.
    maximized_item = Unicode()

    #: The child layout node for the area.
    child = Coerced(_areanode)

    def __init__(self, child, **kwargs):
        """ Initialize a floatarea.

        Parameters
        ----------
        child : basestring, docksplit, docktabs, or dockitem
            The primary child layout to use for the float area.

        **kwargs
            Additional configuration data for the layout.

        """
        super(dockarea, self).__init__(child=child, **kwargs)

    def traverse(self):
        """ Traverse the layout in a top-down fashion.

        Returns
        -------
        result : generator
            A generator which will yield all of the layout nodes in
            the dockarea.

        """
        yield self
        for item in self.child.traverse():
            yield item


class _primarynode(object):
    """ A typeclass which implements type checking for dock layouts.

    This class is a private implementation detail.

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
    """ A typeclass which implements type checking for dock layouts.

    This class is a private implementation detail.

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
    """ The toplevel layout node for declaring dock layouts.

    """
    #: The primary, non-floating dock layout node.
    primary = Coerced(_primarynode)

    #: The secondary, floating dock layout nodes.
    secondary = List(Coerced(_secondarynode))

    def __init__(self, primary, *secondary, **kwargs):
        """ Initialize a docklayout.

        Parameters
        ----------
        primary : dockarea, dockitem, or basetring
            The primary non-floating dock layout node.

        *floating
            The secondary floating dock layout nodes. The allowed types
            are the same as for the 'primary' node.

        **kwargs
            Additional configuration data for the layout.

        """
        sup = super(docklayout, self)
        sup.__init__(primary=primary, secondary=list(secondary), **kwargs)

    def traverse(self):
        """ Traverse the layout in a top-down fashion.

        Returns
        -------
        result : generator
            A generator which will yield all of the layout nodes in
            the docklayout.

        """
        yield self
        if self.primary is not None:
            for item in self.primary.traverse():
                yield item
        for secondary in self.secondary:
            for item in secondary.traverse():
                yield item
