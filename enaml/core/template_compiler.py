#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from .block_compiler import BlockCompiler
from .compiler_util import collect_local_names


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
        cg.load_fast(self.scope_key)
        cg.call_function(1)
        cg.store_fast(node_var)

        # Populate the body of the template
        self.node_stack.append(node_var)
        for item in node.body:
            self.visit(item)
        self.node_stack.pop()

        # Create a tuple of the scope variables. The variables are
        # sorted since the pairs will be converted into a sortedmap,
        # which can be populated faster from a sorted sequence.
        for name in sorted(self._local_names):
            cg.load_const(name)
            cg.load_fast(name)
        cg.build_tuple(2 * len(self._local_names))

        # Load and return a tuple of the template scope and node.
        cg.load_fast(node_var)
        cg.build_tuple(2)
        cg.return_value()

        # Release the held variables
        self.var_pool.release(node_var)
