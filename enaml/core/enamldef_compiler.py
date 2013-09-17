#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from itertools import count

from .block_compiler import BlockCompiler, CompilerPass
from .code_generator import CodeGenerator


class EnamlDefCompiler(BlockCompiler):
    """ A compiler class for compiling 'enamldef' blocks.

    This compiler is invoked by the main EnamlCompiler class when it
    reaches an EnamlDef ast node. The main entry point is the 'compile'
    classmethod.

    """
    @classmethod
    def compile(cls, node, filename):
        """ Compile an EnamlDef node into a code object.

        Parameters
        ----------
        node : EnamlDef
            The enaml ast node representing the enamldef block.

        filename : str
            The full name of the file which contains the node.

        Returns
        -------
        result : CodeType
            A Python code object which implements the enamldef block.

        """
        def new_code_generator():
            gen = CodeGenerator()
            gen.filename = filename
            gen.name = node.typename
            gen.firstlineno = node.lineno
            gen.newlocals = True
            return gen

        # Create the compiler instance for generating the block.
        compiler = cls()

        # Run the first pass to count the nodes.
        compiler.comp_pass = CompilerPass.CountNodes
        compiler.index_counter = count()
        compiler.visit(node)

        # Create the outer code generator and setup the block.
        cg = new_code_generator()
        compiler.code_generator = cg
        compiler.prepare_block()

        # Run the second pass to generate the nodes.
        compiler.comp_pass = CompilerPass.BuildNodes
        compiler.code_generator = new_code_generator()
        compiler.index_counter = count()
        compiler.visit(node)
        compiler.call_from(cg)

        # Run the third pass to generate data binding.
        compiler.comp_pass = CompilerPass.BindData
        compiler.code_generator = new_code_generator()
        compiler.index_counter = count()
        compiler.visit(node)
        compiler.call_from(cg)

        # Load the node for the class and return the class.
        cg.load_fast(compiler.node_list)
        cg.load_const(0)
        cg.binary_subscr()
        cg.load_attr('klass')
        cg.return_value()

        # Generate and return the code object for the block.
        return cg.to_code()

    #--------------------------------------------------------------------------
    # Utilities
    #--------------------------------------------------------------------------
    def handle_enaml_def(self, node, index):
        """ The handler for an enamldef node.

        """
        cg = self.code_generator

        # Preload the helper to generate the enamldef
        cg.set_lineno(node.lineno)
        self.load_helper('make_enamldef')

        # Load the base class for the enamldef
        cg.load_const(node.typename)
        cg.load_global(node.base)                   # helper -> name -> base

        # Validate the type of the base class
        with cg.try_squash_raise():
            cg.dup_top()
            self.load_helper('validate_declarative')
            cg.rot_two()                            # helper -> name -> base -> helper -> base
            cg.call_function(1)                     # helper -> name -> base -> retval
            cg.pop_top()                            # helper -> name -> base

        # Build the enamldef class
        cg.build_tuple(1)
        cg.build_map()
        cg.load_global('__name__')
        cg.load_const('__module__')
        cg.store_map()                              # helper -> name -> bases -> dict
        if node.docstring:
            cg.load_const(node.docstring)
            cg.load_const('__doc__')
            cg.store_map()
        cg.call_function(3)                         # class

        # Build the compiler node
        store_locals = self.should_store_locals(node)
        self.load_helper('enamldef_node')
        cg.rot_two()
        cg.load_const(node.identifier)
        cg.load_fast(self.scope_key)
        cg.load_const(store_locals)                 # helper -> class -> identifier -> bool
        cg.call_function(4)                         # node

        # Store the node into the node list
        self.store_node(index)

        #: Store the node in the node map if needed.
        if node.identifier:
            cg.load_fast(self.node_map)
            self.load_node(index)
            cg.load_const(node.identifier)
            cg.store_map()
            cg.pop_top()

    #--------------------------------------------------------------------------
    # Visitors
    #--------------------------------------------------------------------------
    def visit_EnamlDef(self, node):
        """ The compiler visitor for an EnamlDef node.

        """
        comp_pass = self.comp_pass
        index = self.index_counter.next()
        self.index_stack.append(index)

        if comp_pass == CompilerPass.CountNodes:
            self.node_count += 1
        elif comp_pass == CompilerPass.BuildNodes:
            self.handle_enaml_def(node, index)

        for item in node.body:
            self.visit(item)

        self.index_stack.pop()
