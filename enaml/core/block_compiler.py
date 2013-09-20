#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from itertools import count

from atom.api import Atom, Constant, Int, Str, Typed

from .code_generator import CodeGenerator
from .enaml_ast import (
    Binding, StorageExpr, AliasExpr, EnamlDef, Template, ChildDef,
    PythonExpression, PythonModule, TemplateInst, ExBinding, ConstExpr,
    TemplateInstBinding
)


COMPILE_MODE = {
    PythonExpression: 'eval',
    PythonModule: 'exec',
}


def count_nodes(node):
    """ Count the number of nodes needed for a block.

    Parameters
    ----------
    node : Template or EnamlDef
        The root node of interest.

    Returns
    -------
    result : int
        The number of nodes needed for the block.

    """
    node_count = 0
    stack = [node]
    types = (Template, ChildDef, EnamlDef, TemplateInst)
    while stack:
        node = stack.pop()
        if isinstance(node, types):
            node_count += 1
            stack.extend(node.body)
    return node_count


def should_store_locals(node):
    """ Get whether or not a node should store its locals.

    A node must store its local scope if it has alias exprs,
    attribute bindings, or storage exprs with default bindings.

    Parameters
    ----------
    node : EnamlDef or ChildDef
        The ast node of interest.

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


def collect_local_names(node):
    """ Collect the compile-time local variable names for the node.

    Parameters
    ----------
    node : Template
        The enaml ast template node of interest.

    Returns
    -------
    result : tuple
        A 2-tuple of (const_names, param_names) lists for the block.

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


class BlockCompiler(Atom):
    """ A base class for creating block compilers.

    This class implements common logic for the enamldef and template
    compilers.

    """
    #: The filename for the node being compiled.
    filename = Str()

    #: The set of local names for the compiler.
    local_names = Typed(set, ())

    #: A mapping of const name to index in the const tuple.
    const_indices = Typed(dict, ())

    #: The code generator for the compiler.
    code_generator = Typed(CodeGenerator, ())

    #: The name of the scope key in local storage.
    scope_key = Constant('_[scope_key]')

    #: The name of the node list in the fast locals.
    node_list = Constant('_[node_list]')

    #: The name of the globals in the fast locals.
    f_globals = Constant('_[f_globals]')

    #: The name of the compiler helpers in the fast locals.
    c_helpers = Constant('_[helpers]')

    #: The name of the template parameter tuple.
    t_params = Constant('_[t_params]')

    #: The name of the stored template const values.
    t_consts = Constant('_[t_consts]')

    #: The name of the unpack mapping for the current template inst.
    unpack_map = Constant('_[unpack_map]')

    #: The index of the node for the current unpack mapping.
    unpack_index = Int(-1)

    @classmethod
    def compile(cls, node, filename):
        """ The main entry point to the compiler.

        This method will invoke the compiler for the given root node.

        Parameters
        ----------
        node : EnamlDef or Template
            The enaml ast root node to compile.

        filename : str
            The filename of the node being compiled.

        Returns
        -------
        result : CodeType
            The compiled code object for the node.

        """
        compiler = cls(filename=filename)
        if isinstance(node, EnamlDef):
            code = compiler.compile_EnamlDef(node)
        elif isinstance(node, Template):
            code = compiler.compile_Template(node)
        else:
            raise TypeError("Invalid node '%s'" % type(node).__name__)
        return code

    #--------------------------------------------------------------------------
    # Root Compilers
    #--------------------------------------------------------------------------
    def compile_EnamlDef(self, node):
        """ Compile an EnamlDef node into a code object.

        Parameters
        ----------
        node : EnamlDef
            The enamldef ast node of interest.

        Returns
        -------
        result : CodeType
            The compiled code object for the node.

        """
        def new_code_generator():
            gen = CodeGenerator()
            gen.filename = self.filename
            gen.name = node.typename
            gen.firstlineno = node.lineno
            gen.newlocals = True
            return gen

        # Generate the code for building the compiler nodes.
        node_cg = new_code_generator()
        self.code_generator = node_cg
        self.dispatch_build_compiler_nodes(node)
        node_cg.load_const(None)
        node_cg.return_value()

        # Generate the code for binding the data expressions.
        data_cg = new_code_generator()
        self.code_generator = data_cg
        self.dispatch_bind_data(node)
        data_cg.load_const(None)
        data_cg.return_value()

        # Create and prepare the outer code block.
        primary_cg = new_code_generator()
        self.code_generator = primary_cg
        self.prepare_block(count_nodes(node))

        # Setup the args for invoking the secondary codes.
        args = [self.scope_key, self.node_list, self.f_globals, self.c_helpers]

        # Invoke the node builder code
        node_cg.args = args
        primary_cg.load_const(node_cg.to_code())
        primary_cg.make_function()
        for arg in args:
            primary_cg.load_fast(arg)
        primary_cg.call_function(len(args))
        primary_cg.pop_top()

        # Update the internal node ids for the hierarchy.
        primary_cg.load_fast(self.node_list)
        primary_cg.load_const(0)
        primary_cg.binary_subscr()
        primary_cg.load_attr('update_id_nodes')
        primary_cg.call_function()
        primary_cg.pop_top()

        # Invoke the data binding code
        data_cg.args = args
        primary_cg.load_const(data_cg.to_code())
        primary_cg.make_function()
        for arg in args:
            primary_cg.load_fast(arg)
        primary_cg.call_function(len(args))
        primary_cg.pop_top()

        # Load the root compiler node and return the class.
        primary_cg.load_fast(self.node_list)
        primary_cg.load_const(0)
        primary_cg.binary_subscr()
        primary_cg.load_attr('klass')
        primary_cg.return_value()

        # Generate and return the code object for the block.
        return primary_cg.to_code()

    def compile_Template(self, node):
        """ Compile a Template node into a code object.

        Parameters
        ----------
        node : Template
            The template ast node of interest.

        Returns
        -------
        result : CodeType
            The compiled code object for the node.

        """
        def new_code_generator():
            gen = CodeGenerator()
            gen.filename = self.filename
            gen.name = node.name
            gen.firstlineno = node.lineno
            gen.newlocals = True
            return gen

        # Collect the local names used in the block.
        const_names, param_names = collect_local_names(node)
        self.local_names.update(param_names)
        self.local_names.update(const_names)

        # TODO optimize the parameter packing and unpacking based
        # on whether or not the block will actually use the values.

        # Setup the const index mapping.
        for idx, name in enumerate(const_names):
            self.const_indices[name] = idx

        # Generate the code for building the compiler nodes.
        node_cg = new_code_generator()
        node_cg.load_fast(self.t_params)
        node_cg.unpack_sequence(len(param_names))
        for p_name in param_names:
            node_cg.store_fast(p_name)
        self.code_generator = node_cg
        self.dispatch_build_compiler_nodes(node)
        for c_name in const_names:
            node_cg.load_fast(c_name)
        node_cg.build_tuple(len(const_names))
        node_cg.return_value()

        # Generate the code for binding the data expressions.
        data_cg = new_code_generator()
        data_cg.load_fast(self.t_params)
        data_cg.unpack_sequence(len(param_names))
        for p_name in param_names:
            data_cg.store_fast(p_name)
        self.code_generator = data_cg
        self.dispatch_bind_data(node)
        data_cg.load_const(None)
        data_cg.return_value()

        # Create and prepare the outer code block.
        primary_cg = new_code_generator()
        self.code_generator = primary_cg
        self.prepare_block(count_nodes(node))

        # Setup the template params tuple.
        for p_name in param_names:
            primary_cg.load_fast(p_name)
        primary_cg.build_tuple(len(param_names))
        primary_cg.store_fast(self.t_params)

        # Setup the args for invoking the node building codes
        args = [
            self.scope_key, self.node_list, self.f_globals,
            self.c_helpers, self.t_params
        ]

        # Invoke the node generating code and store the consts tuple.
        node_cg.args = args
        primary_cg.load_const(node_cg.to_code())
        primary_cg.make_function()
        for arg in args:
            primary_cg.load_fast(arg)
        primary_cg.call_function(len(args))
        primary_cg.store_fast(self.t_consts)

        # Update the internal node ids for the node hierarchy.
        primary_cg.load_fast(self.node_list)
        primary_cg.load_const(0)
        primary_cg.binary_subscr()
        primary_cg.load_attr('update_id_nodes')
        primary_cg.call_function()
        primary_cg.pop_top()

        # Setup the args for invoking the data binding code.
        args.append(self.t_consts)

        # Invoke the data binding code.
        data_cg.args = args
        primary_cg.load_const(data_cg.to_code())
        primary_cg.make_function()
        for arg in args:
            primary_cg.load_fast(arg)
        primary_cg.call_function(len(args))
        primary_cg.pop_top()

        # Load the template compiler node.
        primary_cg.load_fast(self.node_list)
        primary_cg.load_const(0)
        primary_cg.binary_subscr()

        # Add the template scope to the node.
        primary_cg.dup_top()
        self.load_helper('add_template_scope')
        primary_cg.rot_two()
        primary_cg.load_const(tuple(param_names + const_names))
        primary_cg.load_fast(self.t_params)
        primary_cg.load_fast(self.t_consts)
        primary_cg.binary_add()
        primary_cg.call_function(3)
        primary_cg.pop_top()

        # Return the template node to the caller.
        primary_cg.return_value()

        # Generate and return the code object for the block.
        primary_cg.args = param_names
        primary_cg.docstring = node.docstring
        primary_cg.varargs = bool(node.parameters.starparam)
        return primary_cg.to_code()

    #--------------------------------------------------------------------------
    # Dispatchers
    #--------------------------------------------------------------------------
    def dispatch_build_compiler_nodes(self, root):
        """ Build the compiler node hierarchy for a root node.

        Parameters
        ----------
        node : EnamlDef or Template
            The root node for the block.

        """
        counter = count()
        stack = [(-1, root)]
        while stack:
            parent, node = stack.pop()
            if isinstance(node, EnamlDef):
                index = counter.next()
                self.gen_EnamlDef(node, index)
                for item in reversed(node.body):
                    stack.append((index, item))
            elif isinstance(node, Template):
                index = counter.next()
                self.gen_Template(node, index)
                for item in reversed(node.body):
                    stack.append((index, item))
            elif isinstance(node, ChildDef):
                index = counter.next()
                self.gen_ChildDef(node, index, parent)
                for item in reversed(node.body):
                    stack.append((index, item))
            elif isinstance(node, TemplateInst):
                index = counter.next()
                self.gen_TemplateInst(node, index, parent)
            elif isinstance(node, ConstExpr):
                self.gen_ConstExpr(node)

    def dispatch_bind_data(self, root):
        """ Bind the data for the hierarchy of a root node.

        Parameters
        ----------
        node : EnamlDef or Template
            The root node for the block.

        """
        counter = count()
        types = (EnamlDef, ChildDef, Template, TemplateInst)
        stack = [(-1, root)]
        while stack:
            parent, node = stack.pop()
            if isinstance(node, types):
                index = counter.next()
                for item in reversed(node.body):
                    stack.append((index, item))
            elif isinstance(node, Binding):
                self.gen_OperatorExpr(node.expr, parent, node.name)
            elif isinstance(node, ExBinding):
                self.gen_OperatorExpr(node.expr, parent, node.chain)
            elif isinstance(node, TemplateInstBinding):
                self.gen_TemplateInstBinding(node, parent)
            elif isinstance(node, AliasExpr):
                self.gen_AliasExpr(node, parent)
            elif isinstance(node, StorageExpr):
                self.gen_StorageExpr(node, parent)
                if node.expr is not None:
                    self.gen_OperatorExpr(node.expr, parent, node.name)
            elif isinstance(node, ConstExpr):
                self.unpack_ConstExpr(node)

    #--------------------------------------------------------------------------
    # Node Generators
    #--------------------------------------------------------------------------
    def gen_EnamlDef(self, node, index):
        """ Build the compiler node for an EnamlDef.

        Parameters
        ----------
        node : EnamlDef
            The root EnamlDef ast node.

        index : int
            The index to use for storing the node.

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
        store_locals = should_store_locals(node)
        self.load_helper('enamldef_node')
        cg.rot_two()
        cg.load_const(node.identifier)
        cg.load_fast(self.scope_key)
        cg.load_const(store_locals)                 # helper -> class -> identifier -> bool
        cg.call_function(4)                         # node

        # Store the node into the node list
        self.store_node(index)

    def gen_ChildDef(self, node, index, parent):
        """ Build the compiler node for a ChildDef.

        Parameters
        ----------
        node : ChildDef
            The ChildDef ast node of interest.

        index : int
            The index to use for storing the node.

        parent : int
            The index to use for the parent of the node.

        """
        cg = self.code_generator

        # Set the line number and load the child class
        cg.set_lineno(node.lineno)
        self.load_name(node.typename)

        # Validate the type of the child
        with cg.try_squash_raise():
            cg.dup_top()
            self.load_helper('validate_declarative')
            cg.rot_two()                            # base -> helper -> base
            cg.call_function(1)                     # base -> retval
            cg.pop_top()                            # base

        # Subclass the child class if needed
        store_types = (StorageExpr, AliasExpr)
        if any(isinstance(item, store_types) for item in node.body):
            cg.load_const(node.typename)
            cg.rot_two()
            cg.build_tuple(1)
            cg.build_map()
            cg.load_global('__name__')
            cg.load_const('__module__')
            cg.store_map()                          # name -> bases -> dict
            cg.build_class()                        # class

        # Build the declarative compiler node
        store_locals = should_store_locals(node)
        self.load_helper('declarative_node')
        cg.rot_two()
        cg.load_const(node.identifier)
        cg.load_fast(self.scope_key)
        cg.load_const(store_locals)                 # helper -> class -> identifier -> key -> bool
        cg.call_function(4)                         # node

        # Store this node in the node list.
        self.store_node(index)

        # Append this node to the parent node
        self.append_node(parent, index)

    def gen_TemplateInst(self, node, index, parent):
        """ Build the compiler node for a TemplateInst.

        Parameters
        ----------
        node : TemplateInst
            The TemplateInst ast node of interest.

        index : int
            The index to use for storing the node.

        parent : int
            The index to use for the parent of the node.

        """
        cg = self.code_generator

        # Set the line number and load the template.
        cg.set_lineno(node.lineno)
        self.load_name(node.name)

        # Validate the type of the template.
        with cg.try_squash_raise():
            cg.dup_top()
            self.load_helper('validate_template')
            cg.rot_two()
            cg.call_function(1)
            cg.pop_top()

        # Load the arguments for the instantiation call.
        arguments = node.arguments
        for arg in arguments.args:
            self.safe_eval_ast(arg.ast, node.name, arg.lineno)
        if arguments.stararg:
            arg = arguments.stararg
            self.safe_eval_ast(arg.ast, node.name, arg.lineno)

        # Instantiate the template.
        argcount = len(arguments.args)
        varargs = bool(arguments.stararg)
        if varargs:
            cg.call_function_var(argcount)
        else:
            cg.call_function(argcount)

        # Validate the instantiation size, if needed.
        names = ()
        starname = ''
        identifiers = node.identifiers
        if identifiers is not None:
            names = tuple(identifiers.names)
            starname = identifiers.starname
            with cg.try_squash_raise():
                cg.dup_top()
                self.load_helper('validate_unpack_size')
                cg.rot_two()
                cg.load_const(len(names))
                cg.load_const(bool(starname))
                cg.call_function(3)
                cg.pop_top()

        # Load and call the helper to create the compiler node
        self.load_helper('template_inst_node')
        cg.rot_two()
        cg.load_const(names)
        cg.load_const(starname)
        cg.load_fast(self.scope_key)
        cg.call_function(4)

        # Store the node to the node list.
        self.store_node(index)

        # Append the node to the parent node
        self.append_node(parent, index)

    def gen_Template(self, node, index):
        """ Build the compiler node for a Template.

        Parameters
        ----------
        node : TemplateInst
            The TemplateInst ast node of interest.

        index : int
            The index to use for storing the node.

        """
        cg = self.code_generator
        cg.set_lineno(node.lineno)
        self.load_helper('template_node')
        cg.load_fast(self.scope_key)
        cg.call_function(1)
        self.store_node(index)

    def gen_ConstExpr(self, node):
        """ Generate the code for a const expr.

        """
        cg = self.code_generator
        cg.set_lineno(node.lineno)
        self.safe_eval_ast(node.expr.ast, node.name, node.lineno)
        if node.typename:
            with cg.try_squash_raise():
                cg.dup_top()
                self.load_helper('type_check_expr')
                cg.rot_two()
                self.load_name(node.typename)
                cg.call_function(2)                 # TOS -> retval
                cg.pop_top()
        cg.store_fast(node.name)

    #--------------------------------------------------------------------------
    # Data Binders
    #--------------------------------------------------------------------------
    def gen_StorageExpr(self, node, index):
        """ Bind the data expressions for a StorageExpr.

        Parameters
        ----------
        node : StorageExpr
            The StorageExpr ast node of interest.

        index : int
            The index of the compiler node for the storage.

        """
        cg = self.code_generator
        with cg.try_squash_raise():
            cg.set_lineno(node.lineno)
            self.load_helper('add_storage')
            self.load_node(index)
            cg.load_const(node.name)
            if node.typename:
                self.load_name(node.typename)
            else:
                cg.load_const(None)
            cg.load_const(node.kind)                # helper -> class -> name -> type -> kind
            cg.call_function(4)                     # retval
            cg.pop_top()

    def gen_AliasExpr(self, node, index):
        """ Bind the data expressions for an AliasExpr.

        Parameters
        ----------
        node : AliasExpr
            The AliasExpr ast node of interest.

        index : int
            The index of the compiler node for the storage.

        """
        cg = self.code_generator
        with cg.try_squash_raise():
            cg.set_lineno(node.lineno)
            self.load_helper('add_alias')
            self.load_node(index)
            cg.load_const(node.name)
            cg.load_const(node.target)
            cg.load_const(node.chain)
            cg.call_function(4)
            cg.pop_top()

    def gen_OperatorExpr(self, node, index, name):
        """ Bind the data expressions for an OperatorExpr.

        Parameters
        ----------
        node : OperatorExpr
            The OperatorExpr ast node of interest.

        index : int
            The index of the compiler node for the storage.

        name : str or tuple
            The string name or tuple of extended names to which the
            operator is being bound.

        """
        cg = self.code_generator
        mode = COMPILE_MODE[type(node.value)]
        code = compile(node.value.ast, cg.filename, mode=mode)
        with cg.try_squash_raise():
            cg.set_lineno(node.lineno)
            self.load_helper('run_operator')
            self.load_node(index)
            cg.load_const(name)
            cg.load_const(node.operator)
            cg.load_const(code)
            cg.load_fast(self.f_globals)            # helper -> node -> name -> op -> code -> globals
            cg.call_function(5)
            cg.pop_top()

    def gen_TemplateInstBinding(self, node, index):
        """ Bind the data expressions for a template instance.

        Parameters
        ----------
        node : TemplateInst
            The ast node of interest.

        index : int
            The index of the compiler node for the storage.

        """
        cg = self.code_generator

        # Create the unpack map for this node, if needed.
        if index != self.unpack_index:
            self.load_helper('make_unpack_map')
            self.load_node(index)
            cg.call_function(1)
            cg.store_fast(self.unpack_map)
            self.unpack_index = index

        op_node = node.expr
        mode = COMPILE_MODE[type(op_node.value)]
        code = compile(op_node.value.ast, cg.filename, mode=mode)
        with cg.try_squash_raise():
            cg.set_lineno(node.lineno)
            self.load_helper('run_operator')
            cg.load_fast(self.unpack_map)
            cg.load_const(node.name)
            cg.binary_subscr()
            cg.load_const(node.chain)
            cg.load_const(op_node.operator)
            cg.load_const(code)
            cg.load_fast(self.f_globals)
            cg.call_function(5)
            cg.pop_top()

    def unpack_ConstExpr(self, node):
        """ Unpack a const value from the local consts tuple.

        Parameters
        ----------
        node : ConstExpr
            The ConstExpr ast node of interest.

        """
        cg = self.code_generator
        cg.set_lineno(node.lineno)
        cg.load_fast(self.t_consts)
        cg.load_const(self.const_indices[node.name])
        cg.binary_subscr()
        cg.store_fast(node.name)

    #--------------------------------------------------------------------------
    # Utilities
    #--------------------------------------------------------------------------
    def load_name(self, name):
        """ Load a name onto the TOS.

        This indirection allows the call to be redirected by a subclass
        to load the name from the local scope.

        """
        cg = self.code_generator
        if name in self.local_names:
            cg.load_fast(name)
        else:
            cg.load_global(name)

    def load_helper(self, name):
        """ Load the compiler helper with the given name.

        """
        cg = self.code_generator
        cg.load_fast(self.c_helpers)
        cg.load_const(name)
        cg.binary_subscr()

    def load_node(self, index):
        """ Load a node onto the TOS.

        """
        cg = self.code_generator
        cg.load_fast(self.node_list)
        cg.load_const(index)
        cg.binary_subscr()

    def store_node(self, index):
        """ Store the node on TOS into the node list.

        """
        cg = self.code_generator
        cg.load_fast(self.node_list)
        cg.load_const(index)
        cg.store_subscr()

    def append_node(self, parent, index):
        """ Append a child node to a parent node.

        """
        cg = self.code_generator
        self.load_node(parent)
        cg.load_attr('children')
        cg.load_attr('append')
        self.load_node(index)
        cg.call_function(1)
        cg.pop_top()

    def prepare_block(self, node_count):
        """ Prepare the code block for code generation.

        This method will setup the state variables needed by the
        rest of the code generators for the block.

        Parameters
        ----------
        node_count : int
            The number of nodes needed by the block.

        """
        cg = self.code_generator

        # Store the globals as fast locals.
        cg.load_global('globals')
        cg.call_function()
        cg.store_fast(self.f_globals)

        # Store the helpers as fast locals.
        cg.load_global('__compiler_helpers')
        cg.store_fast(self.c_helpers)

        # Create a local scope key for the block.
        self.load_helper('make_object')
        cg.call_function()
        cg.store_fast(self.scope_key)

        # Create the node list for the block.
        cg.load_const(None)
        cg.build_list(1)
        cg.load_const(node_count)
        cg.binary_multiply()
        cg.store_fast(self.node_list)

    def safe_eval_ast(self, node, name, lineno):
        """ Safe eval a Python ast node.

        """
        cg = self.code_generator

        # Generate the code object for the expression
        expr_cg = CodeGenerator()
        expr_cg.filename = cg.filename
        expr_cg.name = name
        expr_cg.firstlineno = lineno
        expr_cg.set_lineno(lineno)
        expr_cg.insert_python_expr(node, trim=False)
        call_args = expr_cg.rewrite_to_fast_locals(self.local_names)
        expr_code = expr_cg.to_code()

        # Create and invoke the function
        cg.load_const(expr_code)
        cg.make_function()
        for arg in call_args:
            self.load_name(arg)
        cg.call_function(len(call_args))
