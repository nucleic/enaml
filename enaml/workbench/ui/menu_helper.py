#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from collections import defaultdict

from atom.api import Atom, Instance, List, Typed

import kiwisolver as kiwi

from enaml.widgets.action import Action
from enaml.workbench.workbench import Workbench

from .action_item import ActionItem
from .item_group import ItemGroup
from .menu_item import MenuItem

import enaml
with enaml.imports():
    from .workbench_menus import (
        WorkbenchAction, WorkbenchActionGroup, WorkbenchMenu
    )


def solve_ordering(nodes):
    """ Solve for the desired order of the list of nodes.

    This function is an implementation detail and should not be
    consumed by code outside of this module.

    Parameters
    ----------
    nodes : list
        The list of PathNode objects which should be ordered. It
        is assumed that all nodes reside in the same group.

    Returns
    -------
    result : list
        The PathNode objects ordered according to the constraints
        specified by the 'before' and 'after' items attributes.

    """
    variables = {}
    for node in nodes:
        variables[node.id] = kiwi.Variable(str(node.id))

    prev_var = None
    constraints = []
    for node in nodes:
        this_var = variables[node.id]
        constraints.append(this_var >= 0)
        if prev_var is not None:  # weakly preserve relative order
            constraints.append((prev_var + 0.1 <= this_var) | 'weak')
        before = node.item.before
        if before:
            if before not in variables:
                msg = "item '%s' has invalid `before` reference '%s'"
                raise ValueError(msg % (node.path, before))
            target_var = variables[before]
            constraints.append((this_var + 0.1 <= target_var) | 'strong')
        after = node.item.after
        if after:
            if after not in variables:
                msg = "item '%s' has invalid `after` reference '%s'"
                raise ValueError(msg % (node.path, after))
            target_var = variables[after]
            constraints.append((target_var + 0.1 <= this_var) | 'strong')
        prev_var = this_var

    solver = kiwi.Solver()
    for cn in constraints:
        solver.addConstraint(cn)
    solver.updateVariables()

    return sorted(nodes, key=lambda node: (variables[node.id].value(), id(node)))


class PathNode(Atom):
    """ The base class for the menu building nodes.

    This class is an implementation detail and should not be consumed
    by code outside of this module.

    """
    #: The declarative item for the node.
    item = Instance((MenuItem, ActionItem))

    @property
    def path(self):
        """ Get the sanitized path for the node.

        """
        path = self.item.path.rstrip(u'/')
        if not path:
            return u'/'
        if path[0] != u'/':
            return u'/' + path
        return path

    @property
    def parent_path(self):
        """ Get the sanitized path of the parent node.

        """
        path = self.path.rsplit(u'/', 1)[0]
        return path or u'/'

    @property
    def id(self):
        """ Get the id portion of the path.

        """
        return self.path.rsplit(u'/', 1)[1]

    def assemble(self):
        """ Assemble the menu or action object for the node.

        """
        raise NotImplementedError


class ActionNode(PathNode):
    """ A path node representing an action item.

    This class is an implementation detail and should not be consumed
    by code outside of this module.

    """
    #: The workbench instance to associate with action.
    workbench = Typed(Workbench)

    def assemble(self):
        """ Assemble and return a WorkbenchAction for the node.

        """
        return WorkbenchAction(workbench=self.workbench, item=self.item)


class MenuNode(PathNode):
    """ A path node representing a menu item.

    This class is an implementation detail and should not be consumed
    by code outside of this module.

    """
    #: The child objects defined for this menu node.
    children = List(PathNode)

    def group_data(self):
        """ The group map and list of group items for the node.

        Returns
        -------
        result : tuple
            A tuple of (dict, list) which holds the mapping of group
            id to ItemGroup object, and the flat list of ordered groups.

        """
        group_map = {}
        item_groups = self.item.item_groups

        for group in item_groups:
            if group.id in group_map:
                msg = "menu item '%s' has duplicate group '%s'"
                raise ValueError(msg % (self.path, group.id))
            group_map[group.id] = group

        if u'' not in group_map:
            group = ItemGroup()
            group_map[u''] = group
            item_groups.append(group)

        return group_map, item_groups

    def collect_child_groups(self):
        """ Yield the ordered and grouped children.

        """
        group_map, item_groups = self.group_data()

        grouped = defaultdict(list)
        for child in self.children:
            target_group = child.item.group
            if target_group not in group_map:
                msg = "item '%s' has invalid group '%s'"
                raise ValueError(msg % (child.path, target_group))
            grouped[target_group].append(child)

        for group in item_groups:
            if group.id in grouped:
                nodes = grouped.pop(group.id)
                yield group, solve_ordering(nodes)

    def create_children(self, group, nodes):
        """ Create the child widgets for the given group of nodes.

        This will assemble the nodes and setup the action groups.

        """
        result = []
        actions = []
        children = [node.assemble() for node in nodes]

        def process_actions():
            if actions:
                wag = WorkbenchActionGroup(group=group)
                wag.insert_children(None, actions)
                result.append(wag)
                del actions[:]

        for child in children:
            if isinstance(child, WorkbenchAction):
                actions.append(child)
            else:
                process_actions()
                child.group = group
                result.append(child)

        process_actions()

        return result

    def assemble_children(self):
        """ Assemble the list of child objects for the menu.

        """
        children = []
        for group, nodes in self.collect_child_groups():
            children.extend(self.create_children(group, nodes))
            children.append(Action(separator=True))
        if children:
            children.pop()
        return children

    def assemble(self):
        """ Assemble and return a WorkbenchMenu for the node.

        """
        menu = WorkbenchMenu(item=self.item)
        menu.insert_children(None, self.assemble_children())
        return menu


class RootMenuNode(MenuNode):
    """ A path node representing a root menu item.

    This class is an implementation detail and should not be consumed
    by code outside of this module.

    """
    def group_data(self):
        """ Get the group data for the root menu node.

        """
        group = ItemGroup()
        return {u'': group}, [group]

    def assemble(self):
        """ Assemble and return the list of root menu bar menus.

        """
        return self.assemble_children()


def create_menus(workbench, menu_items, action_items):
    """ Create the WorkbenchMenu objects for the menu bar.

    This is the only external public API of this module.

    Parameters
    ----------
    workbench : Workbench
        The workbench object which is creating the menus.

    menu_items : list
        The list of all MenuItem objects to include in the menus. The
        order of the items in this list is irrelevant.

    action_items : list
        The list of all ActionItem objects to include in the menus.
        The order of the items in this list is irrelevant.

    Returns
    -------
    result : list
        An ordered list of Menu objects which can be directly included
        into the main window's MenuBar.

    """
    # create the nodes for the menu items
    menu_nodes = []
    for item in menu_items:
        node = MenuNode(item=item)
        menu_nodes.append(node)

    # assemble the menu nodes into a tree structure in two passes
    # in order to maintain the relative item definition order
    root = RootMenuNode()
    node_map = {u'/': root}
    for node in menu_nodes:
        path = node.path
        if path in node_map:
            msg = "a menu item already exist for path '%s'"
            raise ValueError(msg % path)
        node_map[path] = node
    for node in menu_nodes:
        parent_path = node.parent_path
        if parent_path not in node_map:
            msg = "the path '%s' does not point to a menu item"
            raise ValueError(msg % parent_path)
        parent = node_map[parent_path]
        parent.children.append(node)

    # create the nodes for the action items
    action_nodes = []
    for item in action_items:
        node = ActionNode(item=item, workbench=workbench)
        action_nodes.append(node)

    # add the action nodes to the tree structure
    for node in action_nodes:
        parent_path = node.parent_path
        if parent_path not in node_map:
            msg = "the path '%s' does not point to a menu item"
            raise ValueError(msg % parent_path)
        path = node.path
        if path in node_map:
            msg = "an item already exist for path '%s'"
            raise ValueError(msg % path)
        parent = node_map[parent_path]
        parent.children.append(node)
        node_map[path] = node

    # generate the menus for the root nodes
    return root.assemble()
