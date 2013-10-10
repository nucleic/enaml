#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from atom.api import List, Typed

from . import compiler_common as cmn
from .enaml_ast import ConstExpr, Template


def collect_local_names(node):
    """ Collect the compile-time local variable names for the node.

    Parameters
    ----------
    node : Template
        The enaml ast template node of interest.

    Returns
    -------
    result : tuple
        A 2-tuple of (const_names, param_names) lists for the template.

    """
    const_names = []
    param_names = []
    params = node.parameters
    for param in (params.positional + params.keywords):
        param_names.append(param.name)
    if params.starparam:
        param_names.append(params.starparam)
    for item in node.body:
        if isinstance(item, ConstExpr):
            const_names.append(item.name)
    return const_names, param_names


class FirstPassTemplateCompiler(cmn.CompilerBase):
    """ The first pass template compiler.

    This compiler generates the code which builds the compiler nodes
    for the template definition. The main entry point is the 'compile'
    class method.

    """
    #: The set of local names for the compiler.
    _local_names = Typed(set, ())

    #: A mapping of ast node -> compiler node index for the block. This
    #: mapping is updated as the compiler progresses.
    _index_map = Typed(dict, ())

    #: A mapping of auxiliary ast node -> compiler node index.
    _aux_index_map = Typed(dict, ())

    #: The const names collected during traversal.
    _const_names = List()

    @classmethod
    def compile(cls, node, args, local_names, filename):
        """ Invoke the compiler for the given node.

        The generated code object expects the SCOPE_KEY to be passed as
        one of the arguments. The code object will return a 2-tuple of
        compiler node list and const expression value tuple.

        Parameters
        ----------
        node : Template
            The enaml ast Template node of interest.

        args : list
            The list of argument names which will be passed to the
            code object when it is invoked.

        local_names : set
            The set of local names which are available to the code
            object. This should be the combination of const expression
            names and template parameter names.

        filename : str
            The filename of the node being compiled.

        Returns
        -------
        result : tuple
            A 2-tuple of (code, index_map) which is the generated code
            object for the first compiler pass, and a mapping of ast
            node to relevant compiler node index.

        """
        compiler = cls()
        compiler.filename = filename
        compiler._local_names = local_names
        cg = compiler.code_generator

        # Setup the block for execution.
        cmn.fetch_helpers(cg)
        cmn.make_node_list(cg, cmn.count_nodes(node))

        # Dispatch the visitors.
        compiler.visit(node)

        # Setup the parameters and generate the code object.
        cg.name = node.name
        cg.firstlineno = node.lineno
        cg.newlocals = True
        cg.args = args
        code = cg.to_code()

        # Union the two index maps for use by the second compiler pass.
        final_index_map = dict(compiler._index_map)
        final_index_map.update(compiler._aux_index_map)

        return (code, final_index_map)

    #--------------------------------------------------------------------------
    # Utilities
    #--------------------------------------------------------------------------
    def parent_index(self):
        """ Get the node index for the parent node.

        Returns
        -------
        result : int
            The compiler node index for the node represented by the
            current parent ast node.

        """
        return self._index_map[self.ancestor()]

    #--------------------------------------------------------------------------
    # Visitors
    #--------------------------------------------------------------------------
    def visit_Template(self, node):
        # No pragmas are supported yet for template nodes.
        cmn.warn_pragmas(node, self.filename)

        # Claim the index for the compiler node
        index = len(self._index_map)
        self._index_map[node] = index

        # Setup the line number for the template.
        cg = self.code_generator
        cg.set_lineno(node.lineno)

        # Create the template compiler node and store in the node list.
        cmn.load_helper(cg, 'template_node')
        cg.load_fast(cmn.SCOPE_KEY)
        cg.call_function(1)
        cmn.store_node(cg, index)

        # Visit the body of the template.
        for item in node.body:
            self.visit(item)

        # Update the internal node ids for the hierarchy.
        cmn.load_node(cg, 0)
        cg.load_attr('update_id_nodes')
        cg.call_function()
        cg.pop_top()

        # Load the compiler node list for returning.
        cg.load_fast(cmn.NODE_LIST)

        # Load the const names for returning.
        for name in self._const_names:
            cg.load_fast(name)
        cg.build_tuple(len(self._const_names))

        # Create and return the return value tuple.
        cg.build_tuple(2)
        cg.return_value()

    def visit_ChildDef(self, node):
        # Claim the index for the compiler node.
        index = len(self._index_map)
        self._index_map[node] = index

        # Setup the line number for the child def.
        cg = self.code_generator
        cg.set_lineno(node.lineno)

        # Generate the child def compiler node.
        cmn.gen_child_def_node(cg, node, self._local_names)

        # Store the compiler node in the node list.
        cmn.store_node(cg, index)

        # Append the compiler node to the parent node.
        cmn.append_node(cg, self.parent_index(), index)

        # Visit the body of the child def.
        for item in node.body:
            self.visit(item)

    def visit_TemplateInst(self, node):
        # No pragmas are supported yet for template inst nodes.
        cmn.warn_pragmas(node, self.filename)

        # Claim the index for the compiler node.
        index = len(self._index_map)
        self._index_map[node] = index

        # Setup the line number for the template inst.
        cg = self.code_generator
        cg.set_lineno(node.lineno)

        # Generate the template inst compiler node.
        cmn.gen_template_inst_node(cg, node, self._local_names)

        # Store the compiler node in the node list.
        cmn.store_node(cg, index)

        # Append the compiler node to the parent node.
        cmn.append_node(cg, self.parent_index(), index)

        # Visit the body of the template inst.
        for item in node.body:
            self.visit(item)

    def visit_ConstExpr(self, node):
        # Keep track of the const name for loading for return.
        self._const_names.append(node.name)

        # Setup the line number for the const expr.
        cg = self.code_generator
        cg.set_lineno(node.lineno)

        # Generate the code for the expression.
        names = self._local_names
        cmn.safe_eval_ast(cg, node.expr.ast, node.name, node.lineno, names)

        # Validate the type of the expression value.
        if node.typename:
            with cg.try_squash_raise():
                cg.dup_top()
                cmn.load_helper(cg, 'type_check_expr')
                cg.rot_two()
                cmn.load_name(cg, node.typename, names)
                cg.call_function(2)
                cg.pop_top()

        # Store the result in the fast locals.
        cg.store_fast(node.name)

    def visit_TemplateInstBinding(self, node):
        # Grab the index of the parent node for later use.
        self._aux_index_map[node] = self.parent_index()

    def visit_Binding(self, node):
        # Grab the index of the parent node for later use.
        self._aux_index_map[node] = self.parent_index()

    def visit_ExBinding(self, node):
        # Grab the index of the parent node for later use.
        self._aux_index_map[node] = self.parent_index()

    def visit_AliasExpr(self, node):
        # Grab the index of the parent node for later use.
        self._aux_index_map[node] = self.parent_index()

    def visit_StorageExpr(self, node):
        # Grab the index of the parent node for later use.
        self._aux_index_map[node] = self.parent_index()


class SecondPassTemplateCompiler(cmn.CompilerBase):
    """ The second pass template compiler.

    This compiler generates code which binds the data to the compiler
    nodes for the template definition. The main entry point is the
    'compile' class method.

    """
    #: The set of local names for the compiler.
    _local_names = Typed(set, ())

    #: A mapping of ast node -> compiler node index for the block.
    _index_map = Typed(dict, ())

    #: A mapping of const names to their value index.
    _const_indices = Typed(dict, ())

    @classmethod
    def compile(cls, node, args, local_names, index_map, consts, filename):
        """ Invoke the compiler for the given node.

        The generated code object expects NODE_LIST and T_CONSTS to be
        passed as part of the arguments.

        Parameters
        ----------
        node : Template
            The enaml ast Template node of interest.

        args : list
            The list of argument names which will be passed to the
            code object when it is invoked.

        local_names : set
            The set of local names which are available to the code
            object. This should be the combination of const expression
            names and template parameter names.

        index_map : dict
            A mapping of ast node to compiler node index in the node list.

        consts : list
            The list of const expression names for the block.

        filename : str
            The filename of the node being compiled.

        Returns
        -------
        result : CodeType
            The code object which will bind the data for the block.

        """
        compiler = cls()
        compiler.filename = filename
        compiler._local_names = local_names
        compiler._index_map = index_map
        for index, name in enumerate(consts):
            compiler._const_indices[name] = index

        cg = compiler.code_generator

        # Setup the block for execution.
        cmn.fetch_helpers(cg)
        cmn.fetch_globals(cg)

        # Dispatch the visitors.
        compiler.visit(node)

        # Setup the parameters and generate the code object.
        cg.name = node.name
        cg.firstlineno = node.lineno
        cg.newlocals = True
        cg.args = args
        return cg.to_code()

    #--------------------------------------------------------------------------
    # Utilities
    #--------------------------------------------------------------------------
    def parent_index(self):
        """ Get the node index for the parent node.

        Returns
        -------
        result : int
            The compiler node index for the node represented by the
            current parent ast node.

        """
        return self._index_map[self.ancestor()]

    #--------------------------------------------------------------------------
    # Visitors
    #--------------------------------------------------------------------------
    def visit_Template(self, node):
        # Visit the body of the template.
        for item in node.body:
            self.visit(item)

        # Add the return value for the code.
        cg = self.code_generator
        cg.load_const(None)
        cg.return_value()

    def visit_ChildDef(self, node):
        # Visit the body of the child def.
        for item in node.body:
            self.visit(item)

    def visit_TemplateInst(self, node):
        if node.body:
            # Create the unpack map.
            cg = self.code_generator
            index = self._index_map[node]
            cmn.load_helper(cg, 'make_unpack_map')
            cmn.load_node(cg, index)
            cg.call_function(1)
            cg.store_fast(cmn.UNPACK_MAP)

            # Visit the body of the template inst.
            for item in node.body:
                self.visit(item)

    def visit_ConstExpr(self, node):
        # Store the value of the const expr into fast locals.
        cg = self.code_generator
        cg.set_lineno(node.lineno)
        cg.load_fast(cmn.T_CONSTS)
        cg.load_const(self._const_indices[node.name])
        cg.binary_subscr()
        cg.store_fast(node.name)

    def visit_TemplateInstBinding(self, node):
        # Generate the code for the template inst binding.
        cg = self.code_generator
        cmn.gen_template_inst_binding(cg, node)

    def visit_Binding(self, node):
        # Generate the code for the operator binding.
        cg = self.code_generator
        index = self.parent_index()
        cmn.gen_operator_binding(cg, node.expr, index, node.name)

    def visit_ExBinding(self, node):
        # Generate the code for the operator binding.
        cg = self.code_generator
        index = self.parent_index()
        cmn.gen_operator_binding(cg, node.expr, index, node.name)

    def visit_AliasExpr(self, node):
        # Generate the code for the alias expression.
        cg = self.code_generator
        index = self.parent_index()
        cmn.gen_alias_expr(cg, node, index)

    def visit_StorageExpr(self, node):
        # Generate the code for the storage expression.
        cg = self.code_generator
        index = self.parent_index()
        cmn.gen_storage_expr(cg, node, index, self._local_names)
        if node.expr is not None:
            cmn.gen_operator_binding(cg, node.expr, index, node.name)


class TemplateCompiler(cmn.CompilerBase):
    """ A compiler which will compile an Enaml template definition.

    The entry point is the `compile` classmethod which will compile
    the ast into a python code object which will generate a template
    instance compiler node when invoked.

    """
    @classmethod
    def compile(cls, node, filename):
        """ The main entry point to the compiler.

        Parameters
        ----------
        node : Template
            The enaml ast Template node to compile.

        filename : str
            The filename of the node being compiled.

        Returns
        -------
        result : CodeType
            The compiled code object for the node.

        """
        assert isinstance(node, Template), "invalid node"
        compiler = cls(filename=filename)
        return compiler.visit(node)

    #--------------------------------------------------------------------------
    # Visitors
    #--------------------------------------------------------------------------
    def visit_Template(self, node):
        cg = self.code_generator
        filename = self.filename

        # Collect the data needed for the compiler passes.
        const_names, param_names = collect_local_names(node)
        local_names = set(const_names + param_names)

        # Generate the code for the first pass.
        first_args = [cmn.SCOPE_KEY] + param_names
        first_code, index_map = FirstPassTemplateCompiler.compile(
            node, first_args, local_names, filename
        )

        # Generate the code for the second pass.
        second_args = [cmn.NODE_LIST, cmn.T_CONSTS] + param_names
        second_code = SecondPassTemplateCompiler.compile(
            node, second_args, local_names, index_map, const_names, filename
        )

        # Prepare the code block for execution.
        cmn.fetch_helpers(cg)
        cmn.load_helper(cg, 'make_object')
        cg.call_function()
        cg.store_fast(cmn.SCOPE_KEY)

        # Load and invoke the first pass code object.
        cg.load_const(first_code)
        cg.make_function()
        for arg in first_args:
            cg.load_fast(arg)
        cg.call_function(len(first_args))
        cg.unpack_sequence(2)
        cg.store_fast(cmn.NODE_LIST)
        cg.store_fast(cmn.T_CONSTS)

        # Load and invoke the second pass code object.
        cg.load_const(second_code)
        cg.make_function()
        for arg in second_args:
            cg.load_fast(arg)
        cg.call_function(len(second_args))
        cg.pop_top()

        # Load the root template compiler node.
        cmn.load_node(cg, 0)

        # Add the template scope to the node.
        cg.dup_top()
        cmn.load_helper(cg, 'add_template_scope')
        cg.rot_two()
        cg.load_const(tuple(param_names + const_names))
        for name in param_names:
            cg.load_fast(name)
        cg.build_tuple(len(param_names))
        cg.load_fast(cmn.T_CONSTS)
        cg.binary_add()
        cg.call_function(3)
        cg.pop_top()

        # Return the template node to the caller.
        cg.return_value()

        # Setup the parameters and generate the code object.
        cg.name = node.name
        cg.firstlineno = node.lineno
        cg.newlocals = True
        cg.args = param_names
        cg.docstring = node.docstring
        cg.varargs = bool(node.parameters.starparam)
        return cg.to_code()
