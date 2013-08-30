#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from . import byteplay as bp
from . import enaml_ast
from .block_compiler import BlockCompiler


class TemplateCompiler(BlockCompiler):
    """ A compiler class for compiling 'template' blocks.

    This compiler is invoked by the main EnamlCompiler class when it
    reaches a Template ast node. The main entry point is the 'compile'
    classmethod.

    """
    @classmethod
    def compile(cls, node, filename):
        """ Compile a Template node into a code object.

        Parameters
        ----------
        node : Template
            The enaml ast node representing the template block.

        filename : str
            The full name of the file which contains the node.

        Returns
        -------
        result : CodeType
            A Python code object which implements the template block.

        """
        compiler = cls(filename=filename)
        compiler.visit(node)
        args = []
        params = node.parameters
        for p in params.positional:
            args.append(p.name)
        for p in params.keywords:
            args.append(p.name)
        varargs = False
        if params.starparam:
            args.append(params.starparam)
            varargs = True
        code = bp.Code(
            compiler.code_ops, [], args, varargs, False, True,
            node.name, filename, node.lineno, None
        )
        return code.to_code()

    #--------------------------------------------------------------------------
    # Utilities
    #--------------------------------------------------------------------------
    def extract_template_locals(self, node):
        """ Get whether or not a Template has local scope variables.

        A template will have local scope variables if it has parameters,
        const expressions, or child identifiers.

        Parameters
        ----------
        node : Template
            The template node of interest.

        Returns
        -------
        result : bool
            True if the node has locals, False otherwise.

        """
        params = node.parameters
        for param in params.positional:
            self.local_names.add(param.name)
        for param in params.keywords:
            self.local_names.add(param.name)
        if params.starparam:
            self.local_names.add(params.starparam)
        # The parser enforces that the StorageExpr is 'static'
        for b in node.body:
            if isinstance(b, enaml_ast.StorageExpr):
                self.local_names.add(b.name)

    #--------------------------------------------------------------------------
    # Visitors
    #--------------------------------------------------------------------------
    def visit_Template(self, node):
        """ The compiler visitor for a Template node.

        """
        #self.extract_template_locals(node)
        #if len(self.local_names) > 0:
        #    self.has_locals = True
        #elif self.has_identifiers(node):
        #    self.has_locals = True

        # Claim the variable for the template node
        node_var = self.var_pool.new()

        # Prepare the block for execution
        self.set_lineno(node.lineno)
        self.fetch_globals()
        self.fetch_helpers()
        self.make_scope_key()

        # Create and store the template node
        self.load_helper('template_node')
        self.load_scope_key()
        self.code_ops.extend([                  # helper -> scope_key
            (bp.LOAD_CONST, self.has_locals),   # helper -> scope_key -> bool
            (bp.CALL_FUNCTION, 0x0002),         # node
            (bp.STORE_FAST, node_var),          # <empty>
        ])

        # Populate the body of the template
        self.node_stack.append(node_var)
        for item in node.body:
            self.visit(item)
        self.node_stack.pop()

        # Return the template node
        self.code_ops.extend([
            (bp.LOAD_FAST, node_var),
            (bp.RETURN_VALUE, None),
        ])

        # Release the held variables
        self.var_pool.release(node_var)
