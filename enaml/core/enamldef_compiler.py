#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Typed

from .block_compiler import BlockCompiler
from .code_generator import CodeGenerator


class EnamlDefCompiler(BlockCompiler):
    """ A compiler class for compiling 'enamldef' blocks.

    This compiler is invoked by the main EnamlCompiler class when it
    reaches an EnamlDef ast node. The main entry point is the 'compile'
    classmethod.

    """
    #: The user-accessible local names for the block. These are always
    #: empty for an enamldef block.
    _local_names = Typed(set, ())

    #: Temporary storage for the visited aliases.
    _alias_nodes = Typed(list, ())

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
        compiler = cls()
        cg = compiler.code_generator
        cg.filename = filename
        compiler.visit(node)
        code = cg.to_code(
            newlocals=True, name=node.typename, firstlineno=node.lineno,
            docstring=node.docstring or None
        )
        return code

    def load_name(self, name):
        """ Load the given name on the TOS.

        This implements a required BlockCompiler method.

        """
        self.code_generator.load_global(name)

    def local_names(self):
        """ Get the set of user-accessible local names for the block.

        This implements a required BlockCompiler method.

        """
        return self._local_names

    def visit_EnamlDef(self, node):
        """ The compiler visitor for an EnamlDef node.

        """
        cg = self.code_generator

        # Claim the variables needed for the class and construct node
        class_var = self.var_pool.new()
        node_var = self.var_pool.new()

        # Prepare the block for execution
        cg.set_lineno(node.lineno)
        self.prepare_block()

        # Load the type name and the base class
        cg.load_helper_from_fast('make_enamldef')
        cg.load_const(node.typename)
        cg.load_global(node.base)                   # helper -> name -> base

        # Validate the type of the base class
        with cg.try_squash_raise():
            cg.dup_top()
            cg.load_helper_from_fast('validate_declarative')
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

        # Store the class as a local
        cg.dup_top()
        cg.store_fast(class_var)

        # Build the compiler node
        cg.load_helper_from_fast('enamldef_node')
        cg.rot_two()
        cg.load_const(node.identifier)
        cg.load_fast(self.scope_key)                # helper -> class -> identifier -> key
        cg.call_function(3)                         # node
        cg.store_fast(node_var)

        # Popuplate the body of the class
        self.class_stack.append(class_var)
        self.node_stack.append(node_var)
        for item in node.body:
            self.visit(item)
        self.process_aliases(node.typename)
        self.class_stack.pop()
        self.node_stack.pop()

        # Store the node on the enamldef and return the class
        cg.load_fast(node_var)
        cg.load_fast(class_var)
        cg.store_attr('__node__')
        cg.load_fast(class_var)
        cg.return_value()

        # Release the held variables
        self.var_pool.release(class_var)
        self.var_pool.release(node_var)

    def visit_AliasExpr(self, node):
        """  The compiler visitor for an AliasExpr node.

        """
        # Store away the node for later processing.
        self._alias_nodes.append(node)

    def process_aliases(self, name):
        """ The handler for processing the alias definitions.

        Parameters
        ----------
        name : str
            The name of the enamldef to which the aliases belong.

        """
        if not self._alias_nodes:
            return

        # The aliases must be processed as a separate function. The
        # line number table in a Python code object does not support
        # negative offsets, and so the only way to get line numbers
        # correct when processing the aliases out-of-order wrt to the
        # block is to given them their own independent code object.
        cg = self.code_generator
        cg_ex = CodeGenerator(filename=cg.filename)

        # Invoke the helper for each alias.
        with cg_ex.try_squash_raise():
            for node in self._alias_nodes:
                cg_ex.set_lineno(node.lineno)
                cg_ex.load_fast('helper')
                cg_ex.load_fast('node_map')
                cg_ex.load_fast('node')
                cg_ex.load_const(node.name)
                cg_ex.load_const(node.target)
                cg_ex.load_const(node.attr)
                cg_ex.call_function(5)
                cg_ex.pop_top()
        cg_ex.load_const(None)
        cg_ex.return_value()

        # Generate the code object for the aliases.
        args = ['helper', 'node_map', 'node']
        firstlineno = self._alias_nodes[0].lineno
        code = cg_ex.to_code(
            args=args, newlocals=True, name=name, firstlineno=firstlineno
        )

        # Invoke the code object inline.
        cg.load_const(code)
        cg.make_function()
        cg.load_helper_from_fast('add_alias')
        cg.load_fast(self.node_map)
        cg.load_fast(self.node_stack[-1])
        cg.call_function(3)
        cg.pop_top()
