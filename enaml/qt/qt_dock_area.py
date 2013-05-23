#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from textwrap import dedent

from PyQt4.QtCore import QObject, QEvent, QSize, QTimer
from PyQt4.QtGui import QTabWidget

from atom.api import Typed

from enaml.widgets.dock_area import ProxyDockArea

from .docking.dock_manager import DockManager
from .docking.q_dock_area import QDockArea
from .qt_constraints_widget import QtConstraintsWidget
from .qt_dock_item import QtDockItem


TAB_POSITIONS = {
    'top': QTabWidget.North,
    'bottom': QTabWidget.South,
    'left': QTabWidget.West,
    'right': QTabWidget.East,
}


def make_style_sheet(style):
    """ A function to generate the stylesheet for the give style.

    """

    if style is None:
        return ''
    bg = '    background: rgba({0.red}, {0.green}, {0.blue}, {0.alpha});'
    fg = '    color: rgba({0.red}, {0.green}, {0.blue}, {0.alpha});'
    bd = '    border: 1px solid rgba({0.red}, {0.green}, {0.blue}, {0.alpha});'
    items = {}
    parts = []
    push = parts.append
    def get(attr, which):
        if getattr(style, attr) is not None:
            items[attr] = which.format(getattr(style, attr))
    def push_item(attr):
        push(items[attr])
    def push_item_if(attr):
        if attr in items:
            push(items[attr])
    get('dock_area_background', bg)
    get('splitter_handle_background', bg)
    get('dock_window_background', bg)
    get('dock_window_border', bd)
    get('dock_container_background', bg)
    get('dock_container_border', bd)
    get('dock_item_background', bg)
    get('title_bar_background', bg)
    get('title_bar_foreground', fg)
    get('tab_background', bg)
    get('tab_hover_background', bg)
    get('tab_selected_background', bg)
    get('tab_foreground', fg)
    get('tab_selected_foreground', fg)
    push('QDockArea {')
    push('    padding: 5px;')
    push_item_if('dock_area_background')
    push('}')
    if 'splitter_handle_background' in items:
        push('QDockSplitterHandle {')
        push_item('splitter_handle_background')
        push('}')
    if 'dock_window_background' in items or 'dock_window_border' in items:
        push('QDockWindow {')
        push_item_if('dock_window_background')
        push_item_if('dock_window_border')
        push('}')
    if 'dock_container_background' in items:
        push('QDockContainer {')
        push_item('dock_container_background')
        push('}')
    if 'dock_container_border' in items:
        push('QDockContainer[floating="true"] {')
        push_item('dock_container_border')
        push('}')
    if 'dock_item_background' in items:
        push('QDockItem {')
        push_item('dock_item_background')
        push('}')
    if 'title_bar_background' in items:
        push('QDockTitleBar {')
        push_item('title_bar_background')
        push('}')
    if 'title_bar_foreground' in items or 'title_bar_font' in items:
        push('QDockTitleBar > QTextLabel {')
        push_item_if('title_bar_foreground')
        # push_item_if('title_bar_font')
        push('}')
    push(dedent("""\
        /* Correct a bug in the pane size when using system styling */
        QDockTabWidget::pane {
        }
        QDockTabBar::close-button {
            margin-bottom: 2px;
            image: url(:dock_images/closebtn_s.png);
        }
        QDockTabBar::close-button:selected {
            image: url(:dock_images/closebtn_b.png);
        }
        QDockTabBar::close-button:hover,
        QDockTabBar::close-button:selected:hover {
            image: url(:dock_images/closebtn_h.png);
        }
        QDockTabBar::close-button:pressed,
        QDockTabBar::close-button:selected:pressed {
            image: url(:dock_images/closebtn_p.png);
        }"""))
    if 'tab_background' in items or 'tab_foreground' in items:
        push('QDockTabBar::tab {')
        push_item_if('tab_background')
        push_item_if('tab_foreground')
        push('}')
    push(dedent("""\
        QDockTabBar::tab:top, QDockTabBar::tab:bottom {
            margin-right: 1px;
            padding-left: 5px;
            padding-right: 5px;
            padding-bottom: 2px;
            height: 17px;
        }

        QDockTabBar::tab:left, QDockTabBar::tab:right {
            margin-bottom: 1px;
            padding-top: 5px;
            padding-bottom: 5px;
            width: 20px;
        }"""))
    if 'tab_hover_background' in items or 'tab_hover_foreground' in items:
        push('QDockTabBar::tab:hover {')
        push_item_if('tab_hover_background')
        push_item_if('tab_hover_foreground')
        push('}')
    if 'tab_selected_background' in items or 'tab_selected_foreground' in items:
        push('QDockTabBar::tab:selected {')
        push_item_if('tab_selected_background')
        push_item_if('tab_selected_foreground')
        push('}')
    print '\n'.join(parts)
    return '\n'.join(parts)

class DockFilter(QObject):
    """ A simple event filter used by the QtDockArea.

    This event filter listens for LayoutRequest events on the dock
    area widget, and will send a size_hint_updated notification to
    the constraints system when the dock area size hint changes.

    The notifications are collapsed on a single shot timer so that
    the dock area geometry can fully settle before being snapped
    by the constraint layout engine.

    """
    def __init__(self, owner):
        super(DockFilter, self).__init__()
        self._owner = owner
        self._size_hint = QSize()
        self._pending = False
        self._timer = timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(self.onNotify)

    def onNotify(self):
        self._owner.size_hint_updated()
        self._pending = False

    def eventFilter(self, obj, event):
        if not self._pending and event.type() == QEvent.LayoutRequest:
            hint = obj.sizeHint()
            if hint != self._size_hint:
                self._size_hint = hint
                self._timer.start(0)
                self._pending = True
        return False


class QtDockArea(QtConstraintsWidget, ProxyDockArea):
    """ A Qt implementation of an Enaml DockArea.

    """
    #: A reference to the widget created by the proxy.
    widget = Typed(QDockArea)

    #: The docking manager which will drive the dock area.
    manager = Typed(DockManager)

    #: The event filter which listens for layout requests.
    dock_filter = Typed(DockFilter)

    #--------------------------------------------------------------------------
    # Initialization API
    #--------------------------------------------------------------------------
    def create_widget(self):
        """ Create the underlying QDockArea widget.

        """
        self.widget = QDockArea(self.parent_widget())
        self.manager = DockManager(self.widget)

    def init_widget(self):
        """ Initialize the underlying widget.

        """
        super(QtDockArea, self).init_widget()
        d = self.declaration
        self.set_tab_position(d.tab_position)
        self.set_style(d.style)

    def init_layout(self):
        """ Initialize the layout of the underlying control.

        """
        super(QtDockArea, self).init_layout()
        manager = self.manager
        for item in self.dock_items():
            manager.add_item(item)
        manager.apply_layout(self.declaration.layout)
        self.dock_filter = dock_filter = DockFilter(self)
        self.widget.installEventFilter(dock_filter)

    def destroy(self):
        """ A reimplemented destructor.

        This removes the event filter from the dock area and releases
        the items from the dock manager.

        """
        self.widget.removeEventFilter(self.dock_filter)
        del self.dock_filter
        self.manager.clear_items()
        super(QtDockArea, self).destroy()

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    def dock_items(self):
        """ Get an iterable of QDockItem children for this area.

        """
        for d in self.declaration.dock_items():
            w = d.proxy.widget
            if w is not None:
                yield w

    #--------------------------------------------------------------------------
    # Child Events
    #--------------------------------------------------------------------------
    def child_added(self, child):
        """ Handle the child added event for a QtDockArea.

        """
        super(QtDockArea, self).child_added(child)
        if isinstance(child, QtDockItem):
            w = child.widget
            if w is not None:
                self.manager.add_item(w)

    def child_removed(self, child):
        """ Handle the child removed event for a QtDockArea.

        """
        super(QtDockArea, self).child_removed(child)
        if isinstance(child, QtDockItem):
            w = child.widget
            if w is not None:
                self.manager.remove_item(w)

    #--------------------------------------------------------------------------
    # ProxyDockArea API
    #--------------------------------------------------------------------------
    def set_tab_position(self, position):
        """ Set the default tab position on the underyling widget.

        """
        self.widget.setTabPosition(TAB_POSITIONS[position])

    def set_style(self, style):
        """ Set the style for the underlying widget.

        """
        self.widget.setStyleSheet(make_style_sheet(style))

    def save_layout(self):
        """ Save the current layout on the underlying widget.

        """
        return self.manager.save_layout()

    def apply_layout(self, layout):
        """ Apply a new layout to the underlying widget.

        """
        self.manager.apply_layout(layout)

    def apply_layout_op(self, op, direction, *item_names):
        """ Apply the layout operation to the underlying widget

        """
        self.manager.apply_layout_op(op, direction, *item_names)
