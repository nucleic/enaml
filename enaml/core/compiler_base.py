#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Atom, Typed

from .code_generator import CodeGenerator


class CompilerBase(Atom):
    """ A base class for creating compilers.

    """
    #: The current code generator for the compiler.
    code_generator = Typed(CodeGenerator, ())

    def visit(self, node, *args):
        """ The main visitor dispatch method.

        Unhandled nodes will raise an error.

        """
        name = 'visit_%s' % type(node).__name__
        try:
            method = getattr(self, name)
        except AttributeError:
            method = self.default_visit
        return method(node, *args)

    def default_visit(self, node, *args):
        """ The default visitor method.

        This method raises since there should be no unhandled nodes.

        """
        raise ValueError('Unhandled Node %s.' % node)
