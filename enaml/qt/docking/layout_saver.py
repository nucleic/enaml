#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import defaultdict

from enaml.layout.dock_layout import (
    ItemLayout, SplitLayout, TabLayout, DockBarLayout, AreaLayout
)
from enaml.nodevisitor import NodeVisitor

from enaml.qt.QtCore import Qt

from .q_dock_bar import QDockBar
from .q_dock_tab_widget import QDockTabWidget


class LayoutSaver(NodeVisitor):
    """ A node visitor which saves the layout for a dock widget.

    Instances of this class can be reused to build multiple layouts.

    """
    BAR_POSITIONS = {
        QDockBar.North: 'top',
        QDockBar.East: 'right',
        QDockBar.South: 'bottom',
        QDockBar.West: 'left',
    }

    TAB_POSITION = {
        QDockTabWidget.North: 'top',
        QDockTabWidget.South: 'bottom',
        QDockTabWidget.West: 'left',
        QDockTabWidget.East: 'right',
    }

    ORIENTATION = {
        Qt.Horizontal: 'horizontal',
        Qt.Vertical: 'vertical',
    }

    def setup(self, node):
        """ Setup the the layout saver.

        """
        self.stack = []

    def result(self, node):
        """ Get the results of the visitor.

        This returns the last item pushed onto the stack.

        """
        return self.stack[-1]

    def teardown(self, node):
        """ Teardown the layout builder.

        """
        del self.stack

    def init_floating_node(self, node, frame):
        """ Initialize a floating node for the given frame.

        Parameters
        ----------
        node : ItemLayout or AreaLayout
            The layout node for the given floating frame.

        frame : QDockFrame
            The floating dock frame.

        """
        node.floating = True
        node.linked = frame.isLinked()
        node.maximized = frame.isMaximized()
        if frame.isMaximized():
            geo = frame.normalGeometry()
        else:
            geo = frame.geometry()
        node.geometry = (geo.x(), geo.y(), geo.width(), geo.height())

    def visit_QDockContainer(self, container):
        """ Visit a QDockContainer node.

        This visitor generates an ItemLayout for the container and
        pushes it onto the stack.

        """
        layout = ItemLayout(container.objectName())
        if container.isWindow():
            self.init_floating_node(layout, container)
        self.stack.append(layout)

    def visit_QDockTabWidget(self, tabs):
        """ Visit a QDockTabWidget node.

        This visitor generates a TabLayout for the tab widget and
        pushes it onto the stack.

        """
        children = []
        for index in range(tabs.count()):
            self.visit(tabs.widget(index))
            children.append(self.stack.pop())
        layout = TabLayout(*children)
        layout.index = tabs.currentIndex()
        layout.tab_position = self.TAB_POSITION[tabs.tabPosition()]
        self.stack.append(layout)

    def visit_QDockSplitter(self, splitter):
        """ Visit a QDockSplitter node.

        This visitor generates a SplitLayout for the splitter and
        pushes it onto the stack.

        """
        children = []
        for index in range(splitter.count()):
            self.visit(splitter.widget(index))
            children.append(self.stack.pop())
        layout = SplitLayout(*children)
        layout.orientation = self.ORIENTATION[splitter.orientation()]
        layout.sizes = splitter.sizes()
        self.stack.append(layout)

    def visit_QDockArea(self, area):
        """ Visit a QDockArea node.

        This visitor generates an AreaLayout for the area and pushes
        it onto the stack.

        """
        central = area.centralWidget()
        if central is None:
            layout = AreaLayout()
        else:
            self.visit(central)
            layout = AreaLayout(self.stack.pop())
        bar_data = defaultdict(list)
        for container, position in area.dockBarContainers():
            bar_data[position].append(container.objectName())
        for bar_pos, names in bar_data.items():
            bar = DockBarLayout(*names, position=self.BAR_POSITIONS[bar_pos])
            layout.dock_bars.append(bar)
        maxed = area.maximizedWidget()
        if maxed is not None:
            name = maxed.objectName()
            for item in layout.find_all(ItemLayout):
                if item.name == name:
                    item.maximized = True
                    break
        self.stack.append(layout)

    def visit_QDockWindow(self, window):
        """ Visit a QDockWindow node.

        This visitor generates an AreaLayout for the window and pushes
        it onto the stack.

        """
        self.visit(window.dockArea())
        layout = self.stack.pop()
        self.init_floating_node(layout, window)
        self.stack.append(layout)
