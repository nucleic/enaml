#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from PyQt4.QtCore import Qt, QRect
from PyQt4.QtGui import QApplication

from atom.api import Atom, Typed, List

from enaml.layout.dock_layout import docklayout, dockarea, dockitem

from .dock_handler import DockHandler
from .dock_overlay import DockOverlay
from .layout_handling import (
    build_layout, save_layout, layout_hit_test, plug_container
)
from .q_dock_area import QDockArea
from .q_dock_container import QDockContainer
from .q_dock_window import QDockWindow
from .q_guide_rose import QGuideRose


def ensure_on_screen(rect):
    """ Ensure that the given rect is contained on screen.

    If the origin of the rect is not contained within the closest
    desktop screen, the rect will be moved so that it is fully on the
    closest screen. If the rect is larger than the closest screen, the
    origin will never be less than the screen origin.

    Parameters
    ----------
    rect : QRect
        The geometry rect of interest.

    """
    d = QApplication.desktop()
    pos = rect.topLeft()
    drect = d.screenGeometry(pos)
    if not drect.contains(pos):
        x = pos.x()
        if x < drect.x() or x > drect.right():
            dw = drect.width() - rect.width()
            x = max(drect.x(), drect.x() + dw)
        y = pos.y()
        if x < drect.top() or y > drect.bottom():
            dh = drect.height() - rect.height()
            y = max(drect.y(), drect.y() + dh)
        rect = QRect(x, y, rect.width(), rect.height())
    return rect


class DockManager(Atom):
    """ A class which manages the docking behavior of a dock area.

    """
    #: The handler which holds the primary dock area.
    dock_area = Typed(QDockArea)

    #: The overlay used when hovering over a dock area.
    overlay = Typed(DockOverlay, ())

    #: The list of DockHandler instances maintained by the manager.
    handlers = List()

    #: The list of toplevel floating handlers.
    toplevel = List()

    #: The set of QDockItem instances added to the manager.
    dock_items = Typed(set, ())

    def __init__(self, dock_area):
        """ Initialize a DockingManager.

        Parameters
        ----------
        dock_area : QDockArea
            The primary dock area to be managed. Docking will be
            restricted to this area and to windows spawned by the
            area.

        """
        assert dock_area is not None
        self.dock_area = dock_area

    #--------------------------------------------------------------------------
    # Private API
    #--------------------------------------------------------------------------
    def _find_handler(self, name):
        """ Find the handler for the given dock item name:

        Parameters
        ----------
        name : basestring
            The name of the dock item for which to locate a handler.

        Returns
        -------
        result : DockHandler or None
            The handler for the named item or None.

        """
        for handler in self.handlers:
            if handler.name() == name:
                return handler

    #--------------------------------------------------------------------------
    # Public API
    #--------------------------------------------------------------------------
    def add_item(self, item):
        """ Add a dock item to the dock manager.

        If the item has already been added, this is a no-op.

        Parameters
        ----------
        items : QDockItem
            The item to be managed by this dock manager. It will be
            reparented to a dock container and made available to the
            the layout system.

        """
        if item in self.dock_items:
            return
        self.dock_items.add(item)
        container = QDockContainer()
        container.setObjectName(item.objectName())
        container.setDockItem(item)
        container.setParent(self.dock_area)
        handler = DockHandler(manager=self, dock_container=container)
        item.handler = handler
        container.handler = handler
        self.handlers.append(handler)

    def remove_item(self, item):
        """ Remove a dock item from the dock manager.

        If the item has not been added to the manager, this is a no-op.

        Parameters
        ----------
        items : QDockItem
            The item to remove from the dock manager. It will be hidden
            and unparented, but not destroyed.

        """
        if item not in self.dock_items:
            return
        self.dock_items.remove(item)
        handler = item.handler
        if not handler.floating:
            handler.unplug()
        container = handler.dock_container
        container.hide()
        container.setParent(None)
        container.setDockItem(None)
        item.handler = None
        container.handler = None
        handler.manager = None
        self.handlers.remove(handler)

    def clear_items(self):
        """ Clear the dock items from the dock manager.

        This method will hide and unparent all of the dock items that
        were previously added to the dock manager. This is equivalent
        to calling the 'remove_item()' method for every item managed
        by the dock manager.

        """
        for item in list(self.dock_items):
            self.remove_item(item)

    def apply_layout(self, layout):
        """ Apply a layout to the dock area.

        Parameters
        ----------
        layout : docklayout
            The docklayout to apply to the managed area.

        """
        # Remove the layout widget before resetting the handlers. This
        # prevents a re-used container from being hidden by the call to
        # setLayoutWidget after it has already been reset. The reference
        # held so that the containers do not get prematurely destroyed.
        widget = self.dock_area.layoutWidget()
        self.dock_area.setLayoutWidget(None)
        for handler in self.handlers:
            handler.reset()

        main_area = None
        floating_areas = []
        for layoutarea in layout.children:
            if layoutarea.floating:
                floating_areas.append(layoutarea)
            else:
                main_area = layoutarea

        if main_area is not None:
            containers = (h.dock_container for h in self.handlers)
            widget = build_layout(main_area.child, containers)
            self.dock_area.setLayoutWidget(widget)

        for f_area in floating_areas:
            child = f_area.child
            if isinstance(child, dockitem):
                handler = self._find_handler(child.name)
                if handler is not None:
                    rect = QRect(*f_area.geometry)
                    handler.float(ensure_on_screen(rect))

    def save_layout(self):
        """ Get the dictionary representation of the dock layout.

        """
        areas = []
        widget = self.dock_area.layoutWidget()
        if widget is not None:
            areas.append(dockarea(save_layout(widget)))
        for handler in self.handlers:
            if handler.floating:
                container = handler.dock_container
                area = dockarea(save_layout(container), floating=True)
                geo = container.geometry()
                area.geometry = (geo.x(), geo.y(), geo.width(), geo.height())
                areas.append(area)
        return docklayout(*areas)

    #--------------------------------------------------------------------------
    # Framework API
    #--------------------------------------------------------------------------
    def dock_drag(self, handler, pos):
        """ Handle the dock drag event from a dock handler.

        This method is called by a floating dock handler as it is being
        dragged by the user. It will make the dock overlay visible at
        the proper location.

        Parameters
        ----------
        handler : DockHandler
            The dock handler which owns the container being dragged by
            the user.

        pos : QPoint
            The global coordinates of the mouse position.

        """
        # Check siblings floating containers first in top-down Z-order
        for sibling in reversed(self.handlers):
            if sibling.floating and sibling is not handler:
                container = sibling.dock_container
                local = container.mapFromGlobal(pos)
                if container.rect().contains(local):
                    # FIXME floating docking not yet fully supported
                    self.overlay.mouse_over_widget(container, local)
                    #self.overlay.hide()
                    return

        # Check the primary area second since it's guaranteed to be
        # below the floating handlers in the application Z-order.
        area = self.dock_area
        local = area.mapFromGlobal(pos)
        if area.rect().contains(local):
            overlay = self.overlay
            if area.layoutWidget() is None:
                overlay.mouse_over_widget(area, local, empty=True)
                return
            widget = layout_hit_test(area, local)
            if widget is not None:
                overlay.mouse_over_area(area, widget, local)
                return
            overlay.mouse_over_widget(area, local)
            return

        # Hide the overlay when there are no mouseover hits.
        self.overlay.hide()

    def end_dock_drag(self, handler, pos):
        """ Handle the dock drag end event from a dock handler.

        This method is called by a floating dock handler when the user
        has completed the drag operation. It will hide the overlay and
        redock the handler if the drag ended over a valid dock guide.

        Parameters
        ----------
        handler : DockHandler
            The dock handler which owns the container being dragged by
            the user.

        pos : QPoint
            The global coordinates of the mouse position.

        """
        # FIXME docking on floating handlers not yet fully supported.
        overlay = self.overlay
        overlay.hide()
        guide = overlay.guide_at(pos)
        if guide != QGuideRose.Guide.NoGuide:
            for sibling in reversed(self.handlers):
                if sibling.floating and sibling is not handler:
                    container = sibling.dock_container
                    local = container.mapFromGlobal(pos)
                    if container.rect().contains(local):
                        w = QDockWindow(self.dock_area)
                        w.move(pos)
                        w.show()
                        return
            area = self.dock_area
            local = area.mapFromGlobal(pos)
            if area.rect().contains(local):
                container = handler.dock_container
                widget = layout_hit_test(area, local)
                if plug_container(area, widget, container, guide):
                    handler.floating = False
