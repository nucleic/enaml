#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import Bool, Typed

from .block_compiler import BlockCompiler
from .compiler_util import has_identifiers, needs_engine


class EnamlDefCompiler(BlockCompiler):
    """ A compiler class for compiling 'enamldef' blocks.

    This compiler is invoked by the main EnamlCompiler class when it
    reaches an EnamlDef ast node. The main entry point is the 'compile'
    classmethod.

    """
    #: Whether instances of the block need local storage.
    _has_locals = Bool(False)

    #: The user-accessible local names for the block.
    _local_names = Typed(set, ())

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

    def has_locals(self):
        """ Get whether or not the block has locals.

        This implements a required BlockCompiler method.

        """
        return self._has_locals

    def local_names(self):
        """ Get the set of user-accessible local names for the block.

        This implements a required BlockCompiler method.

        """
        return self._local_names

    def visit_EnamlDef(self, node):
        """ The compiler visitor for an EnamlDef node.

        """
        cg = self.code_generator

        # Determine whether declaration instances need local storage.
        self._has_locals = has_identifiers(node)

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

        # Build the construct node
        cg.load_helper_from_fast('construct_node')
        cg.rot_two()
        cg.load_const(node.identifier)
        cg.load_fast(self.scope_key)
        cg.load_const(self._has_locals)             # helper -> class -> identifier -> key -> bool
        cg.call_function(4)                         # node
        cg.store_fast(node_var)

        # Build an engine for the new class if needed.
        if needs_engine(node):
            cg.load_helper_from_fast('make_engine')
            cg.load_fast(class_var)                 # helper -> class
            cg.call_function(1)                     # engine
            cg.load_fast(class_var)                 # engine -> class
            cg.store_attr('__engine__')

        # Popuplate the body of the class
        self.class_stack.append(class_var)
        self.node_stack.append(node_var)
        for item in node.body:
            self.visit(item)
        self.class_stack.pop()
        self.node_stack.pop()

        # Store the node on the enamldef and return the class
        cg.load_fast(class_var)
        cg.dup_top()
        cg.load_fast(node_var)
        cg.rot_two()
        cg.store_attr('__node__')
        cg.return_value()

        # Release the held variables
        self.var_pool.release(class_var)
        self.var_pool.release(node_var)
