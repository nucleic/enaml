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

    #: Whether or not the item is free floating.
    floating = Bool(False)

    #: The geometry to apply to the item if it is floating.
    geometry = Coerced(Rect, (-1, -1, -1, -1), coercer=_coerce_rect)

    #: Whether or not the item is maximized.
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
    #: Whether or not the dock area is floating.
    floating = Bool(False)

    #: The geometry to apply to the area if it is floating.
    geometry = Coerced(Rect, (-1, -1, -1, -1), coercer=_coerce_rect)

    #: Whether or not the dock area is maximized.
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


class _layoutnode(object):
    """ A typeclass which implements type checking for dock layouts.

    This class is a private implementation detail.

    """
    class __metaclass__(type):

        def __instancecheck__(cls, instance):
            return isinstance(instance, (dockarea, dockitem))

        def __call__(cls, item):
            if isinstance(item, basestring):
                return dockitem(item)
            msg = "cannot coerce '%s' to a 'docklayout' child"
            raise TypeError(msg % type(item).__name__)


class docklayout(Atom):
    """ The toplevel layout node for declaring dock layouts.

    """
    #: The child layout areas to use with the dock layout.
    children = List(Coerced(_layoutnode))

    def __init__(self, *children, **kwargs):
        """ Initialize a docklayout.

        Parameters
        ----------
        *children
            The child layout areas to use in the layout. The allowed
            types are 'basestring', 'dockarea', and 'dockitem'. Only
            one non-floating dockarea is allowed; all others will be
            made floating. All dockitem instances will be floated.

        **kwargs
            Additional configuration data for the layout.

        """
        super(docklayout, self).__init__(children=list(children), **kwargs)
