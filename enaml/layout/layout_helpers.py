#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .constraint_helper import ConstraintHelper
from .factory_helper import FactoryHelper
from .grid_helper import GridHelper
from .linear_box_helper import LinearBoxHelper
from .sequence_helper import SequenceHelper
from .spacers import LayoutSpacer


spacer = LayoutSpacer(10)


def horizontal(*items, **config):
    """ Create a left-to-right SequenceHelper object.

    Parameters
    ----------
    *items
        The constraint items to pass to the helper.

    **config
        Additional keyword arguments to pass to the helper.

    """
    return SequenceHelper('right', 'left', items, **config)


def vertical(*items, **config):
    """ Create a top-to-bottom SequenceHelper object.

    Parameters
    ----------
    *items
        The constraint items to pass to the helper.

    **config
        Additional keyword arguments to pass to the helper.

    """
    return SequenceHelper('bottom', 'top', items, **config)


def hbox(*items, **config):
    """ Create a horizontal LinearBoxHelper object.

    Parameters
    ----------
    *items
        The constraint items to pass to the helper.

    **config
        Additional keyword arguments to pass to the helper.

    """
    return LinearBoxHelper('horizontal', items, **config)


def vbox(*items, **config):
    """ Create a vertical LinearBoxHelper object.

    Parameters
    ----------
    *items
        The constraint items to pass to the helper.

    **config
        Additional keyword arguments to pass to the helper.

    """
    return LinearBoxHelper('vertical', items, **config)


def align(anchor, *items, **config):
    """ Create a SequenceHelper with the given anchor object.

    Parameters
    ----------
    anchor : str
        The name of the target anchor on the constrainable object.

    *items
        The constraint items to pass to the helper.

    **config
        Additional keyword arguments to pass to the helper.

    """
    config.setdefault('spacing', 0)
    return SequenceHelper(anchor, anchor, items, **config)


def factory(func, *args, **kwargs):
    """ Create a FactoryHelper with the given factory function.

    Parameters
    ----------
    func : callable
        The callable which will generate the list of constraints.
        The owner widget will be passed as the first argument.

    *args
        Additional positional arguments to pass to the factory.

    **kwargs
        Additional keyword arguments to pass to the factory.

    """
    return FactoryHelper(func, *args, **kwargs)


def grid(*rows, **config):
    """ Create a GridHelper object with the given rows.

    Parameters
    ----------
    *rows


    **config
        Additional keyword arguments to pass to the helper.

    """
    return GridHelper(rows, **config)


def expand_constraints(component, constraints):
    """ A function which expands any ConstraintHelper in the list.

    Parameters
    ----------
    component : Constrainable
        The constrainable component with which the constraints are
        associated. This will be passed to the .create_constraints()
        method of any ConstraintHelper instance.

    constraints : list
        The list of constraints to expand.

    Returns
    -------
    result : list
        The list of expanded constraints.

    """
    cns = []
    for cn in constraints:
        if isinstance(cn, ConstraintHelper):
            cns.extend(cn.create_constraints(component))
        elif cn is not None:
            cns.append(cn)
    return cns
