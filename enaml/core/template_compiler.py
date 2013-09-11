#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from .block_compiler import BlockCompiler
from .enaml_ast import ConstExpr


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
    for item in node.body:
        if isinstance(item, ConstExpr):
            local_vars.append(item.name)
    return local_vars


class TemplateCompiler(BlockCompiler):
    """ A compiler class for compiling 'template' blocks.

    This compiler is invoked by the main EnamlCompiler class when it
    reaches a Template ast node. The main entry point is the 'compile'
    classmethod.

    """
    #: The user-accessible local names for the block.
    _local_names = Typed(set, ())

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
        compiler = cls()
        cg = compiler.code_generator
        cg.filename = filename
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
        code = cg.to_code(
            args=args, varargs=varargs, newlocals=True, name=node.name,
            firstlineno=node.lineno
        )
        return code

    def load_name(self, name):
        """ Load the given name on the TOS.

        This implements a required BlockCompiler method.

        """
        cg = self.code_generator
        if name in self._local_names:
            cg.load_fast(name)
        else:
            cg.load_global(name)

    def local_names(self):
        """ Get the set of user-accessible local names for the block.

        This implements a required BlockCompiler method.

        """
        return self._local_names

    def visit_Template(self, node):
        """ The compiler visitor for a Template node.

        """
        cg = self.code_generator

        # Extract the local variables and check for other local scope.
        self._local_names.update(collect_local_names(node))

        # Claim the variable for the template node
        node_var = self.var_pool.new()

        # Prepare the block for execution
        cg.set_lineno(node.lineno)
        self.prepare_block()

        # Create and store the template node
        cg.load_helper_from_fast('template_node')
        cg.call_function()
        cg.store_fast(node_var)

        # Populate the body of the template
        self.node_stack.append(node_var)
        for item in node.body:
            self.visit(item)
        self.node_stack.pop()

        # Load the helper and the template node.
        cg.load_helper_from_fast('make_template_scope')
        cg.load_fast(node_var)

        # Create a tuple of the scope variables. The variables are
        # sorted since the pairs will be converted into a sortedmap,
        # which can be populated faster from a sorted sequence.
        for name in sorted(self._local_names):
            cg.load_const(name)
            cg.load_fast(name)
        cg.build_tuple(2 * len(self._local_names))

        # Call the helper and return the resulting node
        cg.call_function(2)
        cg.return_value()

        # Release the held variables
        self.var_pool.release(node_var)

    def visit_ConstExpr(self, node):
        """ The compiler visitor for a ConstExpr node.

        """
        cg = self.code_generator
        cg.set_lineno(node.lineno)
        with cg.try_squash_raise():

            # Load the value of the expression
            self.safe_eval_ast(node.expr.ast, node.name, node.lineno)

            # Validate the type of the value if necessary
            if node.typename:
                cg.load_helper_from_fast('type_check_expr')
                cg.rot_two()
                self.load_name(node.typename)
                cg.call_function(2)                 # TOS -> value

            # Store the value as a fast local
            cg.store_fast(node.name)
