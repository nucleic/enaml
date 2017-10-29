#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from ..compat import IS_PY3
from . import block_compiler as block
from . import compiler_common as cmn
from .enaml_ast import EnamlDef


class FirstPassEnamlDefCompiler(block.FirstPassBlockCompiler):
    """ The first pass enamldef compiler.

    This compiler generates the code which builds the compiler nodes
    for the enamldef definition. The main entry point is the 'compile'
    class method.

    """
    @classmethod
    def compile(cls, node, args, filename):
        """ Invoke the compiler for the given node.

        The generated code object expects the SCOPE_KEY to be passed as
        one of the arguments. The code object will return the compiler
        node list.

        Parameters
        ----------
        node : EnamlDef
            The enaml ast node of interest.

        args : list
            The list of argument names which will be passed to the
            code object when it is invoked.

        filename : str
            The filename of the node being compiled.

        Returns
        -------
        result : tuple
            A 2-tuple of (code, index_map) which is the generated code
            object for the first compiler pass, and a mapping of ast
            node to relevant compiler node index.

        """
        compiler = cls(filename=filename)
        cg = compiler.code_generator

        # Setup the block for execution.
        cmn.fetch_helpers(cg)
        cmn.make_node_list(cg, cmn.count_nodes(node))

        # Dispatch the visitors.
        compiler.visit(node)

        # Setup the parameters and generate the code object.
        cg.name = node.typename
        cg.firstlineno = node.lineno
        cg.newlocals = True
        cg.args = args
        code = cg.to_code()

        # Union the two index maps for use by the second compiler pass.
        final_index_map = dict(compiler.index_map)
        final_index_map.update(compiler.aux_index_map)

        return (code, final_index_map)

    def visit_EnamlDef(self, node):
        # No pragmas are supported yet for template nodes.
        cmn.warn_pragmas(node, self.filename)

        # Claim the index for the compiler node
        index = len(self.index_map)
        self.index_map[node] = index

        cg = self.code_generator
        cg.set_lineno(node.lineno)

        # Preload the helper to generate the enamldef
        cmn.load_helper(cg, 'make_enamldef')

        # Load the base class for the enamldef
        cg.load_const(node.typename)
        cg.load_global(node.base)                   # helper -> name -> base

        # Validate the type of the base class
        with cg.try_squash_raise():
            cg.dup_top()
            cmn.load_helper(cg, 'validate_declarative')
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
        should_store = cmn.should_store_locals(node)
        cmn.load_helper(cg, 'enamldef_node')
        cg.rot_two()
        cg.load_const(node.identifier)
        cg.load_fast(cmn.SCOPE_KEY)
        cg.load_const(should_store)                 # helper -> class -> identifier -> bool
        cg.call_function(4)                         # node

        # Store the node into the node list
        cmn.store_node(cg, index)

        # Visit the body of the enamldef
        for item in node.body:
            self.visit(item)

        # Update the internal node ids for the hierarchy.
        cmn.load_node(cg, 0)
        cg.load_attr('update_id_nodes')
        cg.call_function()
        cg.pop_top()

        # Load and return the compiler node list..
        cg.load_fast(cmn.NODE_LIST)
        cg.return_value()


class SecondPassEnamlDefCompiler(block.SecondPassBlockCompiler):
    """ The second pass enamldef compiler.

    This compiler generates code which binds the data to the compiler
    nodes for the enamldef definition. The main entry point is the
    'compile' class method.

    """
    @classmethod
    def compile(cls, node, args, index_map, filename):
        """ Invoke the compiler for the given node.

        The generated code object expects NODE_LIST to be passed as part
        of the arguments.

        Parameters
        ----------
        node : Template
            The enaml ast Template node of interest.

        args : list
            The list of argument names which will be passed to the
            code object when it is invoked.

        index_map : dict
            A mapping of ast node to compiler node index in the node list.

        filename : str
            The filename of the node being compiled.

        Returns
        -------
        result : CodeType
            The code object which will bind the data for the block.

        """
        compiler = cls()
        compiler.filename = filename
        compiler.index_map = index_map

        cg = compiler.code_generator

        # Setup the block for execution.
        cmn.fetch_helpers(cg)
        cmn.fetch_globals(cg)

        # Dispatch the visitors.
        compiler.visit(node)

        # Setup the parameters and generate the code object.
        cg.name = node.typename
        cg.firstlineno = node.lineno
        cg.newlocals = True
        cg.args = args
        return cg.to_code()

    def visit_EnamlDef(self, node):
        # Visit the body of the enamldef.
        for item in node.body:
            self.visit(item)

        # Add the return value for the code.
        cg = self.code_generator
        cg.load_const(None)
        cg.return_value()


class EnamlDefCompiler(cmn.CompilerBase):
    """ A compiler which will compile an enamldef definition.

    The entry point is the `compile` classmethod which will compile
    the ast into a python code object which will generate the enamldef
    when invoked.

    """
    @classmethod
    def compile(cls, node, filename):
        """ The main entry point to the compiler.

        Parameters
        ----------
        node : Template
            The enaml ast node to compile.

        filename : str
            The filename of the node being compiled.

        Returns
        -------
        result : CodeType
            The compiled code object for the node.

        """
        assert isinstance(node, EnamlDef), 'invalid node'
        compiler = cls(filename=filename)
        return compiler.visit(node)

    def visit_EnamlDef(self, node):
        cg = self.code_generator
        filename = self.filename

        # Generate the code for the first pass.
        first_args = [cmn.SCOPE_KEY]
        first_code, index_map = FirstPassEnamlDefCompiler.compile(
            node, first_args, filename
        )

        # Generate the code for the second pass.
        second_args = [cmn.NODE_LIST]
        second_code = SecondPassEnamlDefCompiler.compile(
            node, second_args, index_map, filename
        )

        # Prepare the code block for execution.
        cmn.fetch_helpers(cg)
        cmn.load_helper(cg, 'make_object')
        cg.call_function()
        cg.store_fast(cmn.SCOPE_KEY)

        # Load and invoke the first pass code object.
        cg.load_const(first_code)
        if IS_PY3:
            cg.load_const(None)  # XXX better qualified name
        cg.make_function()
        for arg in first_args:
            cg.load_fast(arg)
        cg.call_function(len(first_args))
        cg.store_fast(cmn.NODE_LIST)

        # Load and invoke the second pass code object.
        cg.load_const(second_code)
        if IS_PY3:
            cg.load_const(None)  # XXX better qualified name
        cg.make_function()
        for arg in second_args:
            cg.load_fast(arg)
        cg.call_function(len(second_args))
        cg.pop_top()

        # Load the root template compiler node and return the class.
        cmn.load_node(cg, 0)
        cg.load_attr('klass')
        cg.return_value()

        # Setup the parameters and generate the code object.
        cg.name = node.typename
        cg.firstlineno = node.lineno
        cg.newlocals = True
        cg.docstring = node.docstring
        return cg.to_code()
