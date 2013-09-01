#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from contextlib import contextmanager

from atom.api import Atom, List, Str

from . import byteplay as bp
from . import enaml_ast


class CompilerBase(Atom):
    """ A base class for creating compilers.

    This class provides functionality which is common to all compilers.
    It consists primarily of utility functions for writing common code
    snippets.

    """
    #: The full name of the file which is being compiled.
    filename = Str()

    #: The list of byteplay code operations.
    code_ops = List()

    #--------------------------------------------------------------------------
    # Utilities
    #--------------------------------------------------------------------------
    def set_lineno(self, lineno):
        """ Set the current line number in the code.

        """
        self.code_ops.append((bp.SetLineno, lineno))

    def load_name(self, name):
        """ Load a name onto the TOS.

        This method may be reimplemented by subclasses to control how
        the name is loaded. The default behavior loads the name from
        the global scope.

        """
        self.code_ops.append((bp.LOAD_GLOBAL, name))

    def load_globals(self):
        """ Load the globals onto the TOS.

        This may be reimplemented in a subclass to change how the
        globals are loaded.

        """
        self.code_ops.extend([
            (bp.LOAD_GLOBAL, 'globals'),
            (bp.CALL_FUNCTION, 0x0000),
        ])

    def load_helper(self, name):
        """ Load a compiler helper onto the TOS.

        This may be reimplemented in a subclass to change how the
        helpers are loaded.

        Parameters
        ----------
        name : str
            The name of the helper function to load onto the TOS.

        """
        self.code_ops.extend([
            (bp.LOAD_GLOBAL, '__compiler_helpers'), # helpers
            (bp.LOAD_CONST, name),                  # helpers -> name
            (bp.BINARY_SUBSCR, None),               # helper
        ])

    @contextmanager
    def try_squash_raise(self):
        """ A context manager for squashing tracebacks.

        The code written during this context will be wrapped so that
        any exception raised will appear to have been generated from
        this code, rather than any function called by the code.

        """
        exc_label = bp.Label()
        end_label = bp.Label()
        self.code_ops.append(
            (bp.SETUP_EXCEPT, exc_label)
        )
        yield
        self.code_ops.extend([                  # TOS
            (bp.POP_BLOCK, None),               # TOS
            (bp.JUMP_FORWARD, end_label),       # TOS
            (exc_label, None),                  # TOS -> tb -> val -> exc
            (bp.ROT_THREE, None),               # TOS -> exc -> tb -> val
            (bp.ROT_TWO, None),                 # TOS -> exc -> val -> tb
            (bp.POP_TOP, None),                 # TOS -> exc -> val
            (bp.RAISE_VARARGS, 2),              # TOS
            (bp.JUMP_FORWARD, end_label),       # TOS
            (bp.END_FINALLY, None),             # TOS
            (end_label, None),                  # TOS
        ])

    def validate_declarative(self):
        """ Validate that the TOS is a Declarative subclass.

        """
        with self.try_squash_raise():
            self.code_ops.append(                       # class
                (bp.DUP_TOP, None)                      # class -> class
            )
            self.load_helper('validate_declarative')    # class -> class -> helper
            self.code_ops.extend([
                (bp.ROT_TWO, None),                     # class -> helper -> class
                (bp.CALL_FUNCTION, 0x0001),             # class -> retval
                (bp.POP_TOP, None),                     # class
            ])

    def has_identifiers(self, node):
        """ Get whether or not a node block has identifiers.

        Parameters
        ----------
        node : EnamlDef, ChildDef, Template, or TemplateInst
            The enaml ast node of interest.

        Returns
        -------
        result : bool
            True if the node or any of it's decendents have identifiers,
            False otherwise.

        """
        EnamlDef = enaml_ast.EnamlDef
        ChildDef = enaml_ast.ChildDef
        Template = enaml_ast.Template
        TemplateInst = enaml_ast.TemplateInst
        stack = [node]
        while stack:
            node = stack.pop()
            if isinstance(node, (ChildDef, EnamlDef)):
                if node.identifier:
                    return True
                stack.extend(node.body)
            elif isinstance(node, TemplateInst):
                if node.identifiers:
                    return True
                stack.extend(node.body)
            elif isinstance(node, Template):
                stack.extend(node.body)
        return False

    #--------------------------------------------------------------------------
    # Visitors
    #--------------------------------------------------------------------------
    def visit(self, node):
        """ The main visitor dispatch method.

        Unhandled nodes will raise an error.

        """
        name = 'visit_%s' % type(node).__name__
        try:
            method = getattr(self, name)
        except AttributeError:
            method = self.default_visit
        method(node)

    def default_visit(self, node):
        """ The default visitor method.

        This method raises since there should be no unhandled nodes.

        """
        raise ValueError('Unhandled Node %s.' % node)