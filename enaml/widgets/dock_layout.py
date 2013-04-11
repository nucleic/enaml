#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Enum, List, Str, Bool


class DockLayout(Atom):
    """ A base class for defining dock layout models.

    """
    @classmethod
    def from_dict(cls, dct):
        """ Convert a layout dict into a DockLayout struct.

        """
        pass

    def to_dict(self):
        """ Convert the DockLayout struct into a serializable dict.

        """
        raise NotImplementedError


class DockLayoutItem(DockLayout):
    """ A dock layout class which represents a single named item.

    """
    #: The name of the item referenced by this dock item.
    name = Str()

    def __init__(self, name):
        """ Initialize a DockItem.

        Parameters
        ----------
        name : str
            The name of the dock item in the UI tree to include
            in this location in the layout.

        """
        super(DockLayoutItem, self).__init__(name=name)


class SplitLayout(DockLayout):
    """ A dock layout which arranges its items in a splitter.

    """
    #: The orientation of the splitter.
    orientation = Enum('horizontal', 'vertical')

    #: The items to display in the splitter.
    items = List(DockLayout)

    #: The list of integer sizes to apply to the items in the splitter.
    sizes = List(int)

    def __init__(self, *items, **metadata):
        """ Initialize a SplitLayout.

        Parameters
        ----------
        *items
            The DockLayout items to include in the splitter.

        **metadata
            Additional configuration data for the splitter.

        """
        super(SplitLayout, self).__init__(**metadata)
        assert all(isinstance(item, DockLayout) for item in items)
        self.items = list(items)


class TabbedLayout(DockLayout):
    """ A dock layout which arranges its items in a tabbed notebook.

    """
    #: The style of tabs to use for the tab layout.
    tab_style = Enum('document', 'preferences')

    #: The position of the tabs on the tab widget.
    tab_position = Enum('top', 'bottom', 'left', 'right')

    #: Whether or not the tabs are movable.
    tabs_movable = Bool(True)

    #: The DockLayoutItem instances to include in the tabbed layout.
    items = List(DockLayoutItem)

    def __init__(self, *items, **metadata):
        """ Initialze a TabbedLayout instance.

        Parameters
        ----------
        *items
            The DockLayoutItem items to include in the tabbed layout.

        **metadata
            Additional configuration data for the tabbed layout.

        """
        super(TabbedLayout, self).__init__(**metadata)
        assert all(isinstance(item, DockLayoutItem) for item in items)
        self.items = list(items)


def hsplit(*items, **metadata):
    """ A convenience factory for creating a horizontal SplitLayout.

    Parameters
    ----------
    *items
        The items to include in the splitter. Strings will be promoted
        to DockLayoutItem instances automatically.

    **metadata
        Additional configuration data to pass to the SplitLayout.

    """
    nitems = []
    for item in items:
        if isinstance(item, str):
            item = DockLayoutItem(item)
        nitems.append(item)
    metadata.setdefault('orientation', 'horizontal')
    return SplitLayout(*nitems, **metadata)


def vsplit(*items, **metadata):
    """ A convenience factory for creating a vertical SplitLayout.

    Parameters
    ----------
    *items
        The items to include in the splitter. Strings will be promoted
        to DockLayoutItem instances automatically.

    **metadata
        Additional configuration data to pass to the SplitLayout.

    """
    nitems = []
    for item in items:
        if isinstance(item, str):
            item = DockLayoutItem(item)
        nitems.append(item)
    metadata.setdefault('orientation', 'vertical')
    return SplitLayout(*nitems, **metadata)


def tabbed(*items, **metadata):
    """ A convenience factory for creating a TabbedLayout

    Parameters
    ----------
    *items
        The items to include in the splitter. Strings will be promoted
        to DockLayoutItem instances automatically.

    **metadata
        Additional configuration data to pass to the SplitLayout.

    """
    nitems = []
    for item in items:
        if isinstance(item, str):
            item = DockLayoutItem(item)
        nitems.append(item)
    return TabbedLayout(*nitems, **metadata)
