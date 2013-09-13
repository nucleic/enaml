#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import List, Typed

from .block_compiler import BlockCompiler
from .code_generator import CodeGenerator
from .enaml_ast import AliasExpr, Binding, StorageExpr, ChildDef, TemplateInst


def should_store_locals(node):
    """ Get whether or not an enamldef should store its locals.

    An enamldef must store its local scope if it has alias expressions,
    attribute bindings, or storage expressions with default bindings.

    Parameters
    ----------
    node : EnamlDef
        The enamldef ast node of interest.

    Returns
    -------
    result : bool
        True if instances of the enamldef should store their local
        scopes, False otherwise.

    """
    types = (AliasExpr, Binding)
    for item in node.body:
        if isinstance(item, types):
            return True
        if isinstance(item, StorageExpr) and item.expr is not None:
            return True
    return False


class EnamlDefCompiler(BlockCompiler):
    """ A compiler class for compiling 'enamldef' blocks.

    This compiler is invoked by the main EnamlCompiler class when it
    reaches an EnamlDef ast node. The main entry point is the 'compile'
    classmethod.

    """
    #: Temporary storage for deferred process nodes.
    deferred_nodes = List()

    #: The user-accessible local names for the block. These are always
    #: empty for an enamldef block.
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

    def local_names(self):
        """ Get the set of user-accessible local names for the block.

        This implements a required BlockCompiler method.

        """
        return self._local_names

    def process_deferred_nodes(self, name):
        """ The handler for processing the deferred body nodes.

        Parameters
        ----------
        name : str
            The typename for the enamldef block.

        """
        # In order to properly report line numbers in tracebacks, the
        # deferred nodes must be executed in their own function. This
        # is due to the fact that the lineno table in a code object
        # does not support negative offsets.
        if not self.deferred_nodes:
            return

        # Setup a new code generator for the deferred nodes.
        cg = self.code_generator
        cg_ex = CodeGenerator(filename=cg.filename)
        cg_ex.store_helpers_to_fast()
        cg_ex.store_globals_to_fast()

        # Invoke the vistors for the nodes under the new generator.
        self.code_generator = cg_ex
        for node in self.deferred_nodes:
            self.visit(node)
        self.code_generator = cg

        # Setup the return value for the function.
        cg_ex.load_const(None)
        cg_ex.return_value()

        # Compile the code object for the nodes.
        node_var = self.node_stack[-1]
        args = [self.node_map, node_var]
        firstlineno = self.deferred_nodes[0].lineno
        code = cg_ex.to_code(
            args=args, newlocals=True, name=name, firstlineno=firstlineno
        )

        # Load the code and arguments and invoke the function.
        cg.load_const(code)
        cg.make_function()
        cg.load_fast(self.node_map)
        cg.load_fast(node_var)
        cg.call_function(2)
        cg.pop_top()

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
        store_locals = should_store_locals(node)
        cg.load_helper_from_fast('enamldef_node')
        cg.rot_two()
        cg.load_const(node.identifier)
        cg.load_fast(self.scope_key)
        cg.load_const(store_locals)                 # helper -> class -> identifier -> bool
        cg.call_function(4)                         # node
        cg.store_fast(node_var)

        # Popuplate the body of the class. The expression bindings are
        # processed after all of the children are created so that any
        # forward reference by an alias can be processed.
        self.node_stack.append(node_var)
        child_types = (ChildDef, TemplateInst)
        for item in node.body:
            if isinstance(item, child_types):
                self.visit(item)
            else:
                self.deferred_nodes.append(item)
        self.process_deferred_nodes(node.typename)
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
        """ The compiler visitor for an AliasExpr node.

        """
        cg = self.code_generator
        cg.set_lineno(node.lineno)
        cg.load_helper_from_fast('add_alias')
        cg.load_fast(self.node_map)
        cg.load_fast(self.node_stack[-1])
        cg.load_const(node.name)
        cg.load_const(node.target)
        cg.load_const(node.attr)
        cg.call_function(5)
        cg.pop_top()
