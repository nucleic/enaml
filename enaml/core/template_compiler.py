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
    def collect_local_vars(self, node):
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
        for item in node.body:
            if isinstance(item, enaml_ast.StorageExpr):
                local_vars.append(item.name)
        return local_vars

    #--------------------------------------------------------------------------
    # Visitors
    #--------------------------------------------------------------------------
    def visit_Template(self, node):
        """ The compiler visitor for a Template node.

        """
        # Extract the local variables and check for other local scope.
        self.local_vars.update(self.collect_local_vars(node))
        self.has_locals = bool(self.local_vars)
        if not self.has_locals:
            self.has_locals = self.has_identifiers(node)

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

        # Create a tuple of the scope variables. The variables are
        # sorted since the pairs will be converted into a sortedmap,
        # which can be populated faster from a sorted sequence.
        for name in sorted(self.local_vars):
            self.code_ops.extend([
                (bp.LOAD_CONST, name),  # name
                (bp.LOAD_FAST, name),   # name -> var
            ])
        self.code_ops.append(                           # name -> var -> ...
            (bp.BUILD_TUPLE, 2 * len(self.local_vars))  # scope_tuple
        )

        # Load and return a tuple of the template scope and node.
        self.code_ops.extend([          # scope_tuple
            (bp.LOAD_FAST, node_var),   # scope_tuple -> node
            (bp.BUILD_TUPLE, 2),        # retval
            (bp.RETURN_VALUE, None),
        ])

        # Release the held variables
        self.var_pool.release(node_var)

    def visit_StorageExpr(self, node):
        """ The compiler visitor for a StorageExpr node.

        This reimplements the base class visitor to handle template
        'const' expressions.

        """
        if node.kind != 'const':
            super(TemplateCompiler, self).visit_StorageExpr(node)
            return

        # Compile the expression for the assigment
        self.visit(node.expr.value)
        code = self.code_stack.pop()
        bp_code = bp.Code.from_code(code).code

        # Translate the code to work from function scope. This isolates
        # any effects the expression may have on the local scope, such
        # as list comprehensions which leak the loop variable.
        arg_names = self.translate_locals(bp_code)
        code = bp.Code(
            bp_code, [], arg_names, False, False, True, node.name,
            self.filename, node.lineno, None
        )

        # Inovke the function and store the result as a fast local.
        self.set_lineno(node.lineno)
        self.code_ops.extend([
            (bp.LOAD_CONST, code),  # code
            (bp.MAKE_FUNCTION, 0),  # function
        ])
        for name in arg_names:
            self.code_ops.append((bp.LOAD_FAST, name))
        self.code_ops.append(                       # function -> args
            (bp.CALL_FUNCTION, len(arg_names)),     # value
        )

        # Validate the type of the value if necessary.
        if node.typename:
            with self.try_squash_raise():
                self.load_name(node.typename)
                self.load_helper('type_check_expr')
                self.code_ops.extend([              # value -> kind -> helper
                    (bp.ROT_THREE, None),           # helper -> value -> kind
                    (bp.CALL_FUNCTION, 0x0002),     # value
                ])

        # Store the value in the fast locals
        self.code_ops.append(               # value
            (bp.STORE_FAST, node.name)      # <empty>
        )
