#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Typed

from . import enaml_ast


class VarPool(Atom):
    """ A class for generating private variable names.

    """
    #: The pool of currently used variable names.
    pool = Typed(set, ())

    def new(self):
        """ Get a new private variable name.

        Returns
        -------
        result : str
            An unused variable name.

        """
        var = '_[var_%d]' % len(self.pool)
        self.pool.add(var)
        return var

    def release(self, name):
        """ Return a variable name to the pool.

        Parameters
        ----------
        name : str
            The variable name which is free to be reused.

        """
        self.pool.discard(name)


def collect_local_names(node):
    """ Collect the compile-time local variable names for the node.

    Parameters
    ----------
    node : Template
        The enaml ast template node of interest.

    Returns
    -------
    result : list
        The list of local variable names found in the block.

    """
    local_vars = []
    params = node.parameters
    for param in params.positional:
        local_vars.append(param.name)
    for param in params.keywords:
        local_vars.append(param.name)
    if params.starparam:
        local_vars.append(params.starparam)
    StorageExpr = enaml_ast.StorageExpr
    for item in node.body:
        if isinstance(item, StorageExpr):
            local_vars.append(item.name)
    return local_vars
