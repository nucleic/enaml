#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom


class CompilerBase(Atom):
    """ A base class for creating compilers.

    This class provides the primary visitor dispatching mechanism.

    """
    def visit(self, node, *args, **kwargs):
        """ The main visitor dispatch method.

        Parameters
        ----------
        node : object
            The ast node of interest.

        *args
            Additional arguments to pass to the visitor.

        **kwargs
            Additional keywords to pass to the visitor.

        Returns
        -------
        result : object
            The object returned by the visitor, if any.

        """
        visitor_name = 'visit_' + type(node).__name__
        visitor = getattr(self, visitor_name, None)
        if visitor is None:
            visitor = self.default_visit
        return visitor(node, *args, **kwargs)

    def default_visit(self, node, *args, **kwargs):
        """ The default node visitor method.

        This method is invoked when no named visitor method is found
        for a given node. This default behavior raises an exception for
        the missing handler. Subclasses may reimplement this method for
        custom default behavior.

        """
        msg = "no visitor found for node of type `%s`"
        raise TypeError(msg % type(node).__name__)
