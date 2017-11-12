#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from enaml.qt.QtCore import Qt, QEvent
from enaml.qt.QtWidgets import QApplication

from .event_types import DockAreaContentsChanged
from .q_dock_bar import QDockBar
from .q_dock_container import QDockContainer
from .q_dock_splitter import QDockSplitter, QDockSplitterHandle
from .q_dock_tab_widget import QDockTabWidget
from .q_dock_window import QDockWindow


#------------------------------------------------------------------------------
# Public API
#------------------------------------------------------------------------------
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
    root = area.centralWidget()
    if root is None:
        return False
    if root is container:
        root.hide()
        root.setParent(None)
        area.setCentralWidget(None)
        QApplication.sendEvent(area, QEvent(DockAreaContentsChanged))
        return True
    success, replace = _unplug(root, container)
    if not success:
        return False
    if replace is not None:
        area.setCentralWidget(replace)
    QApplication.sendEvent(area, QEvent(DockAreaContentsChanged))
    return True


def plug_frame(area, widget, frame, guide):
    """ Plug a dock frame into a dock area.

    Parameters
    ----------
    area : QDockArea
        The dock area which owns the layout into which the
        container is being plugged.

    widget : QWidget
        The widget under the mouse. This should be one of
        QDockSplitterHandle, QDockTabWidget, or QDockContainer.

    frame : QDockContainer or QDockWindow
        The dock container or window to be plugged into the area.
        This should already be unplugged from any other layout.

    guide : QGuideRose.Guide
        The guide rose guide which indicates how to perform
        the plugging.

    Returns
    -------
    result : bool
        True if the plugging was successful, False otherwise.

    """
    if not isinstance(frame, (QDockContainer, QDockWindow)):
        return False
    res = _PLUG_HANDLERS[guide](area, widget, frame, guide)
    if res:
        QApplication.sendEvent(area, QEvent(DockAreaContentsChanged))
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
    stack = [area.centralWidget()]
    while stack:
        widget = stack.pop()
        if isinstance(widget, QDockSplitter):
            for index in range(1, widget.count()):
                yield widget.handle(index)
            for index in range(widget.count()):
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
    stack = [area.centralWidget()]
    while stack:
        widget = stack.pop()
        if isinstance(widget, QDockTabWidget):
            yield widget
        elif isinstance(widget, QDockSplitter):
            for index in range(widget.count()):
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
    stack = [area.centralWidget()]
    while stack:
        widget = stack.pop()
        if isinstance(widget, QDockContainer):
            yield widget
        elif isinstance(widget, (QDockSplitter, QDockTabWidget)):
            for index in range(widget.count()):
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
# Layout Unplugging
#------------------------------------------------------------------------------
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
    sizes = widget.sizes()
    for index in range(widget.count()):
        success, replace = _unplug(widget.widget(index), container)
        if success:
            if replace is not None:
                widget.insertWidget(index, replace)
                replace.show()
                widget.setSizes(sizes)
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
    for index in range(widget.count()):
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


#------------------------------------------------------------------------------
# Layout Plugging
#------------------------------------------------------------------------------
def _merge_dock_bars(first, second):
    """ Merge the dock bars from the second area into the first.

    """
    for container, position in second.dockBarContainers():
        container.unplug()
        first.addToDockBar(container, position)


def _merge_splitter(first, index, second):
    """ Merge one splitter into another at a given index.

    """
    if first.orientation() != second.orientation():
        first.insertWidget(index, second)
        second.show()
    else:
        items = [second.widget(i) for i in range(second.count())]
        for item in reversed(items):
            first.insertWidget(index, item)
            item.show()


def _splitter_insert_frame(area, splitter, index, frame):
    """ Insert a frame into a splitter at a given index.

    """
    if isinstance(frame, QDockWindow):
        temp_area = frame.dockArea()
        frame.setDockArea(None)
        _merge_dock_bars(area, temp_area)
        widget = temp_area.centralWidget()
        if isinstance(widget, QDockSplitter):
            _merge_splitter(splitter, index, widget)
        elif widget is not None:
            splitter.insertWidget(index, widget)
            widget.show()
    else:
        if frame.isWindow():
            frame.unfloat()
        splitter.insertWidget(index, frame)
        frame.show()


def _split_root_helper(area, orientation, frame, append):
    """ Split the root layout widget according the orientation.

    """
    widget = area.centralWidget()
    is_splitter = isinstance(widget, QDockSplitter)
    if not is_splitter or widget.orientation() != orientation:
        new = QDockSplitter(orientation)
        area.setCentralWidget(new)
        new.inheritOpaqueResize()
        new.addWidget(widget)
        widget.show()
        widget = new
    index = widget.count() if append else 0
    _splitter_insert_frame(area, widget, index, frame)
    return True


def _plug_border_north(area, widget, frame, guide):
    """ Plug the frame to the north border of the area.

    """
    return _split_root_helper(area, Qt.Vertical, frame, False)


def _plug_border_east(area, widget, frame, guide):
    """ Plug the frame to the east border of the area.

    """
    return _split_root_helper(area, Qt.Horizontal, frame, True)


def _plug_border_south(area, widget, frame, guide):
    """ Plug the frame to the south border of the area.

    """
    return _split_root_helper(area, Qt.Vertical, frame, True)


def _plug_border_west(area, widget, frame, guide):
    """ Plug the frame to the west border of the area.

    """
    return _split_root_helper(area, Qt.Horizontal, frame, False)


def _split_widget_helper(area, orientation, widget, frame, append):
    """ Split the widget according the orientation.

    """
    splitter = widget.parent()
    if not isinstance(splitter, QDockSplitter):
        return False
    index = splitter.indexOf(widget)
    if splitter.orientation() == orientation:
        index += 1 if append else 0
        _splitter_insert_frame(area, splitter, index, frame)
        return True
    sizes = splitter.sizes()
    new = QDockSplitter(orientation)
    new.addWidget(widget)
    splitter.insertWidget(index, new)
    new.inheritOpaqueResize()
    index = new.count() if append else 0
    _splitter_insert_frame(area, new, index, frame)
    splitter.setSizes(sizes)
    return True


def _plug_compass_north(area, widget, frame, guide):
    """ Plug the frame to the north of the widget.

    """
    root = area.centralWidget()
    if widget is root:
        return _split_root_helper(area, Qt.Vertical, frame, False)
    return _split_widget_helper(area, Qt.Vertical, widget, frame, False)


def _plug_compass_east(area, widget, frame, guide):
    """ Plug the frame to the east of the widget.

    """
    root = area.centralWidget()
    if widget is root:
        return _split_root_helper(area, Qt.Horizontal, frame, True)
    return _split_widget_helper(area, Qt.Horizontal, widget, frame, True)


def _plug_compass_south(area, widget, frame, guide):
    """ Plug the frame to the south of the widget.

    """
    root = area.centralWidget()
    if widget is root:
        return _split_root_helper(area, Qt.Vertical, frame, True)
    return _split_widget_helper(area, Qt.Vertical, widget, frame, True)


def _plug_compass_west(area, widget, frame, guide):
    """ Plug the frame to the west of the widget.

    """
    root = area.centralWidget()
    if widget is root:
        return _split_root_helper(area, Qt.Horizontal, frame, False)
    return _split_widget_helper(area, Qt.Horizontal, widget, frame, False)


def _tabs_add_frame(area, tabs, frame):
    """ Add a frame to a dock tab widget.

    """
    containers = []
    if isinstance(frame, QDockWindow):
        temp_area = frame.dockArea()
        frame.setDockArea(None)
        _merge_dock_bars(area, temp_area)
        containers.extend(iter_containers(temp_area))
    else:
        containers.append(frame)
    for container in containers:
        if container.isWindow():
            container.unfloat()
        container.hideTitleBar()
        tabs.addTab(container, container.icon(), container.title())
        container.show()
    tabs.setCurrentIndex(tabs.count() - 1)


def _tabify_helper(area, widget, frame, tab_pos):
    """ Create a tab widget from the widget and frame.

    """
    if isinstance(widget, QDockTabWidget):
        if widget.tabPosition() != tab_pos:
            return False
        _tabs_add_frame(area, widget, frame)
        return True
    if not isinstance(widget, QDockContainer):
        return False
    root = area.centralWidget()
    if widget is not root:
        if not isinstance(widget.parent(), QDockSplitter):
            return False
    tabs = QDockTabWidget()
    tabs.setTabPosition(tab_pos)
    if widget is root:
        area.setCentralWidget(tabs)
        _tabs_add_frame(area, tabs, widget)
        _tabs_add_frame(area, tabs, frame)
    else:
        splitter = widget.parent()
        sizes = splitter.sizes()
        index = splitter.indexOf(widget)
        splitter.insertWidget(index, tabs)
        _tabs_add_frame(area, tabs, widget)
        _tabs_add_frame(area, tabs, frame)
        splitter.setSizes(sizes)
    return True


def _plug_compass_center(area, widget, frame, guide):
    """ Create a tab widget from the widget and frame.

    """
    default = widget if isinstance(widget, QDockTabWidget) else area
    position = default.tabPosition()
    return _tabify_helper(area, widget, frame, position)


def _plug_compass_ex_north(area, widget, frame, guide):
    """ Create a north tab widget from the widget and frame.

    """
    return _tabify_helper(area, widget, frame, QDockTabWidget.North)


def _plug_compass_ex_east(area, widget, frame, guide):
    """ Create a east tab widget from the widget and frame.

    """
    return _tabify_helper(area, widget, frame, QDockTabWidget.East)


def _plug_compass_ex_south(area, widget, frame, guide):
    """ Create a south tab widget from the widget and frame.

    """
    return _tabify_helper(area, widget, frame, QDockTabWidget.South)


def _plug_compass_ex_west(area, widget, frame, guide):
    """ Create a west tab widget from the widget and frame.

    """
    return _tabify_helper(area, widget, frame, QDockTabWidget.West)


def _split_handle_helper(area, handle, frame):
    """ Split the splitter handle with the given frame.

    """
    splitter = handle.parent()
    for index in range(1, splitter.count()):
        if splitter.handle(index) is handle:
            _splitter_insert_frame(area, splitter, index, frame)
            return True
    return False


def _plug_split_vertical(area, widget, frame, guide):
    """ Plug a frame onto a vertical split handle.

    """
    if not isinstance(widget, QDockSplitterHandle):
        return False
    if widget.orientation() != Qt.Vertical:
        return False
    return _split_handle_helper(area, widget, frame)


def _plug_split_horizontal(area, widget, frame, guide):
    """ Plug a frame onto a horizontal split handle.

    """
    if not isinstance(widget, QDockSplitterHandle):
        return False
    if widget.orientation() != Qt.Horizontal:
        return False
    return _split_handle_helper(area, widget, frame)


def _plug_area_center(area, widget, frame, guide):
    """ Plug the frame as the area center.

    """
    if widget is not None:
        return False
    if isinstance(frame, QDockWindow):
        temp_area = frame.dockArea()
        frame.setDockArea(None)
        _merge_dock_bars(area, temp_area)
        area.setCentralWidget(temp_area.centralWidget())
    else:
        if frame.isWindow():
            frame.unfloat()
        area.setCentralWidget(frame)
    return True


def _plug_border_ex(area, frame, dock_bar_pos):
    """ Plug the frame into the specified dock bar.

    """
    containers = []
    if isinstance(frame, QDockWindow):
        temp_area = frame.dockArea()
        frame.setDockArea(None)
        _merge_dock_bars(area, temp_area)
        containers.extend(iter_containers(temp_area))
    else:
        containers.append(frame)
    for container in containers:
        if container.isWindow():
            container.unfloat()
        container.showTitleBar()
        area.addToDockBar(container, dock_bar_pos)
    return True


def _plug_border_ex_north(area, widget, frame, guide):
    """ Plug the frame into the north dock bar.

    """
    return _plug_border_ex(area, frame, QDockBar.North)


def _plug_border_ex_east(area, widget, frame, guide):
    """ Plug the frame into the east dock bar.

    """
    return _plug_border_ex(area, frame, QDockBar.East)


def _plug_border_ex_south(area, widget, frame, guide):
    """ Plug the frame into the south dock bar.

    """
    return _plug_border_ex(area, frame, QDockBar.South)


def _plug_border_ex_west(area, widget, frame, guide):
    """ Plug the frame into the west dock bar.

    """
    return _plug_border_ex(area, frame, QDockBar.West)


_PLUG_HANDLERS = [
    lambda a, w, f, g: False,   # Guide.NoGuide
    _plug_border_north,         # Guide.BorderNorth
    _plug_border_east,          # Guide.BorderEast
    _plug_border_south,         # Guide.BorderSouth
    _plug_border_west,          # Guide.BorderWest
    _plug_compass_north,        # Guide.CompassNorth
    _plug_compass_east,         # Guide.CompassEast
    _plug_compass_south,        # Guide.CompassSouth
    _plug_compass_west,         # Guide.CompassWest
    _plug_compass_center,       # Guide.CompassCenter
    _plug_compass_ex_north,     # Guide.CompassExNorth
    _plug_compass_ex_east,      # Guide.CompassExEast
    _plug_compass_ex_south,     # Guide.CompassExSouth
    _plug_compass_ex_west,      # Guide.CompassExWest
    _plug_split_vertical,       # Guide.SplitVertical
    _plug_split_horizontal,     # Guide.SplitHorizontal
    _plug_area_center,          # Guide.AreaCenter
    _plug_border_ex_north,      # Guide.BorderExNorth
    _plug_border_ex_east,       # Guide.BorderExEast
    _plug_border_ex_south,      # Guide.BorderExSouth
    _plug_border_ex_west,       # Guide.BorderExWest
]
