#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QTabWidget

from enaml.layout.dock_layout import dockitem, docksplit, docktabs

from .q_dock_container import QDockContainer
from .q_dock_splitter import QDockSplitter, QDockSplitterHandle
from .q_dock_tab_widget import QDockTabWidget
from .q_guide_rose import QGuideRose


#: A mapping of qt orientation to layout orientation.
ORIENTATION = {
    Qt.Horizontal: 'horizontal',
    Qt.Vertical: 'vertical',
    'horizontal': Qt.Horizontal,
    'vertical': Qt.Vertical,
}


#: A mapping of qt tab position to layout tab position.
TAB_POSITION = {
    QTabWidget.North: 'top',
    QTabWidget.South: 'bottom',
    QTabWidget.West: 'left',
    QTabWidget.East: 'right',
    'top': QTabWidget.North,
    'bottom': QTabWidget.South,
    'left': QTabWidget.West,
    'right': QTabWidget.East,
}


#------------------------------------------------------------------------------
# Public API
#------------------------------------------------------------------------------
def build_layout(layout, containers):
    """ Build the root layout widget for the layout description.

    Parameters
    ----------
    layout : docktabs, docksplit, or dockitem
        The layout node which describes the widget to be built.

    containers : iterable
        An iterable of QDockContainer instances to use as the
        available containers for the layout.

    Returns
    -------
    result : QDockTabWidget, QDockSplitter, or QDockContainer
        A widget which implements the dock area.

    """
    types = (docktabs, docksplit, dockitem)
    assert isinstance(layout, types), "build_layout() called with invalid type"
    mapping = dict((c.objectName(), c) for c in containers)
    return _build_layout(layout, mapping)


def save_layout(widget):
    """ Save the layout contained in the dock area.

    Parameters
    ----------
    widget : QDockTabWidget, QDockSplitter, or QDockContainer
        The dock widget which should be converted into a layout.

    Returns
    -------
    result : docktabs, docksplit, or dockitem
        A layout node which describes the provided layout widget.

    """
    types = (QDockSplitter, QDockTabWidget, QDockContainer)
    assert isinstance(widget, types), "save_layout() called with invalid type"
    return _save_layout(widget)


def unplug_container(area, container):
    """ Unplug a container from a dock area.

    Parameters
    ----------
    area : QDockArea
        The dock area in which the container lives.

    container : QDockContainer
        The container to remove from the dock area.

    Returns
    -------
    result : bool
        True on success, False otherwise.

    """
    root = area.layoutWidget()
    if root is None:
        return False
    if root is container:
        root.hide()
        root.setParent(None)
        area.setLayoutWidget(None)
        return True
    success, replace = _unplug(root, container)
    if not success:
        return False
    if replace is not None:
        area.setLayoutWidget(replace)
    return True


def plug_container(area, widget, container, guide):
    """ Plug a dock container into a dock area.

    Parameters
    ----------
    area : QDockArea
        The dock area which owns the layout into which the
        container is being plugged.

    widget : QWidget
        The widget under the mouse. This should be one of
        QDockSplitterHandle, QDockTabWidget, or QDockContainer.

    guide : QGuideRose.Guide
        The guide rose guide which indicates how to perform
        the plugging.

    Returns
    -------
    result : bool
        True if the plugging was successful, False otherwise.

    """
    Guide = QGuideRose.Guide
    if guide == Guide.AreaCenter:
        res = _plug_area_center(area, widget, container)
    elif guide == Guide.CompassCenter:
        default = widget if isinstance(widget, QDockTabWidget) else area
        res = _plug_center(area, widget, container, default.tabPosition())
    elif guide == Guide.CompassExNorth:
        res = _plug_center(area, widget, container, QTabWidget.North)
    elif guide == Guide.CompassExEast:
        res = _plug_center(area, widget, container, QTabWidget.East)
    elif guide == Guide.CompassExSouth:
        res = _plug_center(area, widget, container, QTabWidget.South)
    elif guide == Guide.CompassExWest:
        res = _plug_center(area, widget, container, QTabWidget.West)
    elif guide == Guide.CompassNorth:
        res = _plug_north(area, widget, container)
    elif guide == Guide.CompassEast:
        res = _plug_east(area, widget, container)
    elif guide == Guide.CompassSouth:
        res = _plug_south(area, widget, container)
    elif guide == Guide.CompassWest:
        res = _plug_west(area, widget, container)
    elif guide == Guide.BorderNorth:
        res = _plug_border_north(area, container)
    elif guide == Guide.BorderEast:
        res = _plug_border_east(area, container)
    elif guide == Guide.BorderSouth:
        res = _plug_border_south(area, container)
    elif guide == Guide.BorderWest:
        res = _plug_border_west(area, container)
    elif guide == Guide.SplitHorizontal:
        res = _plug_split(widget, container, guide)
    elif guide == Guide.SplitVertical:
        res = _plug_split(widget, container, guide)
    else:
        res = False
    return res


def iter_handles(area):
    """ Iterate the splitter handles in a dock layout.

    Parameters
    ----------
    area : QDockArea
        The dock area containing the dock layout of interest.

    Returns
    -------
    result : generator
        A generator which yields the QDockSplitterHandle instances
        contained within the dock area layout.

    """
    stack = [area.layoutWidget()]
    while stack:
        widget = stack.pop()
        if isinstance(widget, QDockSplitter):
            for index in xrange(1, widget.count()):
                yield widget.handle(index)
            for index in xrange(widget.count()):
                stack.append(widget.widget(index))


def iter_tabs(area):
    """ Iterate the tab widgets in a dock layout.

    Parameters
    ----------
    area : QDockArea
        The dock area containing the dock layout of interest.

    Returns
    -------
    result : generator
        A generator which yields the QDockTabWidget instances contained
        within the dock area layout.

    """
    stack = [area.layoutWidget()]
    while stack:
        widget = stack.pop()
        if isinstance(widget, QDockTabWidget):
            yield widget
        elif isinstance(widget, QDockSplitter):
            for index in xrange(widget.count()):
                stack.append(widget.widget(index))


def iter_containers(area):
    """ Iterate the dock containers in a dock layout.

    Parameters
    ----------
    area : QDockArea
        The dock area containing the dock layout of interest.

    Returns
    -------
    result : generator
        A generator which yields the QDockContainer instances
        contained within the dock area layout.

    """
    stack = [area.layoutWidget()]
    while stack:
        widget = stack.pop()
        if isinstance(widget, QDockContainer):
            yield widget
        elif isinstance(widget, (QDockSplitter, QDockTabWidget)):
            for index in xrange(widget.count()):
                stack.append(widget.widget(index))


def layout_hit_test(area, pos):
    """ Hit test a dock area for a relevant dock target.

    Parameters
    ----------
    area : QDockArea
        The dock area of interest.

    pos : QPoint
        The point of interest expressed in local area coordinates.

    Returns
    -------
    result : QWidget or None
        The relevant dock target under the position. This will be
        a QDockContainer, QDockTabWidget, or QDockSplitterHandle.

    """
    # Splitter handles have priority. Their active area is smaller
    # and overlaps that of other widgets. Giving dock containers
    # priority would make it difficult to hit a splitter reliably.
    # In certain configurations, there may be more than one handle
    # in the hit box, in which case the one closest to center wins.
    hits = []
    for handle in iter_handles(area):
        pt = handle.mapFrom(area, pos)
        rect = handle.rect().adjusted(-20, -20, 20, 20)
        if rect.contains(pt):
            dist = (rect.center() - pt).manhattanLength()
            hits.append((dist, handle))
    if len(hits) > 0:
        hits.sort()
        return hits[0][1]

    # Check for tab widgets next. A tab widget has dock containers,
    # but should have priority over the dock containers themselves.
    for tab_widget in iter_tabs(area):
        pt = tab_widget.mapFrom(area, pos)
        if tab_widget.rect().contains(pt):
            return tab_widget

    # Check for QDockContainers last. The are the most common case,
    # but also have the least precedence compared to the others.
    for dock_container in iter_containers(area):
        pt = dock_container.mapFrom(area, pos)
        if dock_container.rect().contains(pt):
            if not dock_container.isHidden():  # hidden tab
                return dock_container


#------------------------------------------------------------------------------
# Private API
#------------------------------------------------------------------------------
def _build_layout(layout, containers):
    """ The main layout builder dispatch method.

    This method dispatches to the widget-specific handlers.

    """
    if isinstance(layout, dockitem):
        return _build_dockitem(layout, containers)
    if isinstance(layout, docksplit):
        return _build_docksplit(layout, containers)
    if isinstance(layout, docktabs):
        return _build_docktabs(layout, containers)
    raise TypeError("unhandled layout type '%s'" % type(layout).__name__)


def _build_dockitem(layout, containers):
    """ The handler method for a dockitem layout description.

    This handler will pop and return the named container.

    """
    return containers.pop(layout.name, None)


def _build_docksplit(layout, containers):
    """ The handler method for a split layout description.

    This handler will build and populate a QDockSplitter which holds
    the items declared in the layout.

    """
    children = (_build_layout(child, containers) for child in layout.children)
    children = filter(None, children)
    if len(children) == 0:
        return None
    if len(children) == 1:
        return children[0]
    splitter = QDockSplitter(ORIENTATION[layout.orientation])
    for child in children:
        splitter.addWidget(child)
    sizes = layout.sizes
    if sizes and len(sizes) >= len(children):
        splitter.setSizes(sizes)
    return splitter


def _build_docktabs(layout, containers):
    """ The handler method for a tabbed layout description.

    This handler will build and populate a QDockTabWidget which holds
    the items declared in the layout.

    """
    children = (_build_layout(child, containers) for child in layout.children)
    children = filter(None, children)
    if len(children) == 0:
        return None
    if len(children) == 1:
        return children[0]
    tab_widget = QDockTabWidget()
    tab_widget.setMovable(True)
    tab_widget.setDocumentMode(True)
    tab_widget.setTabPosition(TAB_POSITION[layout.tab_position])
    for child in children:
        child.hideTitleBar()
        tab_widget.addTab(child, child.icon(), child.title())
    tab_widget.setCurrentIndex(layout.index)
    return tab_widget


def _save_layout(widget):
    """ The main save dispatch method.

    This method dispatches to the widget-specific handlers.

    """
    if isinstance(widget, QDockContainer):
        return _save_container(widget)
    if isinstance(widget, QDockTabWidget):
        return _save_tabs(widget)
    if isinstance(widget, QDockSplitter):
        return _save_split(widget)
    raise TypeError("unhandled layout widget '%s'" % type(widget).__name__)


def _save_container(widget):
    """ The save handler for a QDockContainer layout widget.

    """
    return dockitem(widget.objectName())


def _save_tabs(widget):
    """ The save handler for a QDockTabWidget layout widget.

    """
    children = []
    for index in xrange(widget.count()):
        children.append(_save_layout(widget.widget(index)))
    layout = docktabs(*children)
    layout.index = widget.currentIndex()
    layout.tab_position = TAB_POSITION[widget.tabPosition()]
    return layout


def _save_split(widget):
    """ The save handler for a QDockSplitter layout widget.

    """
    children = []
    for index in xrange(widget.count()):
        children.append(_save_layout(widget.widget(index)))
    layout = docksplit(*children)
    layout.orientation = ORIENTATION[widget.orientation()]
    layout.sizes = widget.sizes()
    return layout


def _unplug(widget, container):
    """ The main unplug dispatch method.

    This method dispatches to the widget-specific handlers.

    """
    if isinstance(widget, QDockContainer):
        return _unplug_container(widget, container)
    if isinstance(widget, QDockTabWidget):
        return _unplug_tab_widget(widget, container)
    if isinstance(widget, QDockSplitter):
        return _unplug_splitter(widget, container)
    raise TypeError("unhandled layout widget '%s'" % type(widget).__name__)


def _unplug_splitter(widget, container):
    """ The handler for a QDockSplitter widget.

    This method will dispatch to the child handlers, and then clean
    up the splitter if there is only a single child remaining.

    """
    for index in xrange(widget.count()):
        success, replace = _unplug(widget.widget(index), container)
        if success:
            if replace is not None:
                widget.insertWidget(index, replace)
                replace.show()
            replace = None
            if widget.count() == 1:
                replace = widget.widget(0)
                replace.hide()
                replace.setParent(None)
                widget.hide()
                widget.setParent(None)
            return True, replace
    return False, None


def _unplug_tab_widget(widget, container):
    """ The handler for a QDockTabWidget widget.

    This method will dispatch to the child handlers, and then clean
    up the tab widget if there is only a single child remaining.

    """
    for index in xrange(widget.count()):
        success, replace = _unplug(widget.widget(index), container)
        if success:
            assert replace is None  # tabs never hold replaceable items
            if widget.count() == 1:
                replace = widget.widget(0)
                replace.hide()
                replace.setParent(None)
                replace.showTitleBar()
                widget.hide()
                widget.setParent(None)
            return True, replace
    return False, None


def _unplug_container(widget, container):
    """ The handler for a QDockContainer widget.

    If the widget matches the container, this handler will hide and
    unparent the container.

    """
    if widget is container:
        widget.hide()
        widget.showTitleBar()
        widget.setParent(None)
        return True, None
    return False, None


def _plug_area_center(area, widget, container):
    """ Plug the container as the area center.

    """
    if widget is not None:
        return False
    container.unfloat()
    area.setLayoutWidget(container)
    container.show()
    return True


def _plug_center(area, widget, container, tab_pos):
    """ Create a tab widget from the widget and container.

    """
    if isinstance(widget, QDockTabWidget):
        if widget.tabPosition() != tab_pos:
            return False
        container.unfloat()
        container.hideTitleBar()
        widget.addTab(container, container.icon(), container.title())
        widget.setCurrentIndex(widget.count() - 1)
        container.show()
        return True
    if not isinstance(widget, QDockContainer):
        return False
    root = area.layoutWidget()
    if widget is not root:
        if not isinstance(widget.parent(), QDockSplitter):
            return False
    tab_widget = QDockTabWidget()
    tab_widget.setMovable(True)
    tab_widget.setDocumentMode(True)
    tab_widget.setTabPosition(tab_pos)
    if widget is root:
        area.setLayoutWidget(tab_widget)
    else:
        splitter = widget.parent()
        index = splitter.indexOf(widget)
        splitter.insertWidget(index, tab_widget)
    widget.hideTitleBar()
    tab_widget.addTab(widget, widget.icon(), widget.title())
    container.unfloat()
    container.hideTitleBar()
    tab_widget.addTab(container, container.icon(), container.title())
    tab_widget.setCurrentIndex(1)
    container.show()
    return True


def _plug_north(area, widget, container):
    """ Plug the container to the north of the widget.

    """
    root = area.layoutWidget()
    if widget is root:
        return _split_root(area, Qt.Vertical, container, False)
    return _split_widget(Qt.Vertical, widget, container, False)


def _plug_east(area, widget, container):
    """ Plug the container to the east of the widget.

    """
    root = area.layoutWidget()
    if widget is root:
        return _split_root(area, Qt.Horizontal, container, True)
    return _split_widget(Qt.Horizontal, widget, container, True)


def _plug_south(area, widget, container):
    """ Plug the container to the south of the widget.

    """
    root = area.layoutWidget()
    if widget is root:
        return _split_root(area, Qt.Vertical, container, True)
    return _split_widget(Qt.Vertical, widget, container, True)


def _plug_west(area, widget, container):
    """ Plug the container to the west of the widget.

    """
    root = area.layoutWidget()
    if widget is root:
        return _split_root(area, Qt.Horizontal, container, False)
    return _split_widget(Qt.Horizontal, widget, container, False)


def _plug_border_north(area, container):
    """ Plug the container to the north border of the area.

    """
    return _split_root(area, Qt.Vertical, container, False)


def _plug_border_east(area, container):
    """ Plug the container to the east border of the area.

    """
    return _split_root(area, Qt.Horizontal, container, True)


def _plug_border_south(area, container):
    """ Plug the container to the south border of the area.

    """
    return _split_root(area, Qt.Vertical, container, True)


def _plug_border_west(area, container):
    """ Plug the container to the west border of the area.

    """
    return _split_root(area, Qt.Horizontal, container, False)


def _split_root(area, orientation, container, append):
    """ Split the root layout widget according the orientation.

    """
    root = area.layoutWidget()
    is_splitter = isinstance(root, QDockSplitter)
    if not is_splitter or root.orientation() != orientation:
        new = QDockSplitter(orientation)
        area.setLayoutWidget(new)
        new.addWidget(root)
        root.show()
        root = new
    container.unfloat()
    if append:
        root.addWidget(container)
    else:
        root.insertWidget(0, container)
    container.show()
    return True


def _split_widget(orientation, widget, container, append):
    """ Split the widget according the orientation.

    """
    splitter = widget.parent()
    if not isinstance(splitter, QDockSplitter):
        return False
    index = splitter.indexOf(widget)
    if splitter.orientation() == orientation:
        if append:
            index += 1
        container.unfloat()
        splitter.insertWidget(index, container)
        container.show()
        return True
    new = QDockSplitter(orientation)
    new.addWidget(widget)
    splitter.insertWidget(index, new)
    container.unfloat()
    if append:
        new.addWidget(container)
    else:
        new.insertWidget(0, container)
    container.show()
    return True


def _plug_split(handle, container, guide):
    """ Plug the container onto a splitter handle.

    """
    Guide = QGuideRose.Guide
    if not isinstance(handle, QDockSplitterHandle):
        return False
    orientation = handle.orientation()
    if orientation == Qt.Horizontal:
        if guide != Guide.SplitHorizontal:
            return False
    elif guide != Guide.SplitVertical:
        return False
    splitter = handle.parent()
    for index in xrange(1, splitter.count()):
        if splitter.handle(index) is handle:
            container.unfloat()
            splitter.insertWidget(index, container)
            container.show()
            return True
    return False
