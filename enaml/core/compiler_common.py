#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
""" A collection of common compiler functionality.

"""
import ast

from atom.api import Str, Typed

from ..compat import IS_PY3, USE_WORDCODE
from . import byteplay as bp
from .code_generator import CodeGenerator
from .enaml_ast import (
    AliasExpr, ASTVisitor, Binding, ChildDef, EnamlDef, StorageExpr, Template,
    TemplateInst, PythonExpression, PythonModule, FuncDef
)


#: The name of the compiler helpers in the global scope.
COMPILER_HELPERS = '__compiler_helpers'

#: The name of the compiler helpers in the fast locals.
C_HELPERS = '_[helpers]'

#: The name of the scope key in the fast locals.
SCOPE_KEY = '_[scope_key]'

#: The name of the node list in the fast locals.
NODE_LIST = '_[node_list]'

#: The name of the globals map in the fast locals.
F_GLOBALS = '_[f_globals]'

#: The name of the template parameter tuple.
T_PARAMS = '_[t_params]'

#: The name of the stored template const values.
T_CONSTS = '_[t_consts]'

#: The global name of the template map in a module.
TEMPLATE_MAP = '_[template_map]'

#: The name of the unpack mapping for the template instance.
UNPACK_MAP = '_[unpack_map]'

#: A mapping of enaml ast node to compile(...) mode string.
COMPILE_MODE = {
    PythonExpression: 'eval',
    PythonModule: 'exec',
}

#: Ast nodes associated with comprehensions which uses a function call that we
#: will have to call in proper scope
_FUNC_DEF_NODES = [ast.Lambda]
if IS_PY3:
    _FUNC_DEF_NODES.append(ast.ListComp)
if hasattr(ast, 'DictComp'):
    _FUNC_DEF_NODES.append(ast.DictComp)
if hasattr(ast, 'SetComp'):
    _FUNC_DEF_NODES.append(ast.SetComp)

_FUNC_DEF_NODES = tuple(_FUNC_DEF_NODES)

#: Opcode used to create a function
_MAKE_FUNC = ((bp.MAKE_FUNCTION,) +
              ((bp.MAKE_CLOSURE,) if not USE_WORDCODE else ()))


def unhandled_pragma(name, filename, lineno):
    """ Emit a warning for an unhandled pragma.

    Parameters
    ----------
    name : str
        The name of the unhandled pragma.

    filename : str
        The name of the file with the unhandled pragma.

    lineno : int
        The line number of the unhandled pragma.

    """
    import warnings
    msg = "unhandled pragma '%s'" % name
    warnings.warn_explicit(msg, SyntaxWarning, filename, lineno)


def warn_pragmas(node, filename):
    """ Emit a warning if there are any pragmas defined on the node.

    Parameters
    ----------
    node : ASTNode
        An enaml ast node which supports pragmas

    filename : str
        The filename for the node.

    """
    for pragma in node.pragmas:
        unhandled_pragma(pragma.command, filename, pragma.lineno)


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
    types = (AliasExpr, Binding, FuncDef)
    for item in node.body:
        if isinstance(item, types):
            return True
        if isinstance(item, StorageExpr) and item.expr is not None:
            return True
    return False


def count_nodes(node):
    """ Count the number of compiler nodes needed for the template.

    Parameters
    ----------
    node : Template
        The template node of interest.

    Returns
    -------
    result : int
        The number of compiler nodes needed for the template.

    """
    node_count = 0
    stack = [node]
    types = (EnamlDef, Template, ChildDef, TemplateInst)
    while stack:
        node = stack.pop()
        if isinstance(node, types):
            node_count += 1
            stack.extend(node.body)
    return node_count


def has_list_comp(pyast):
    """ Determine whether a Python expression has a list comprehension.

    This function is only used under Python 2.

    Parameters
    ----------
    pyast : Expression
        The Python Expression ast of interest.

    Returns
    -------
    result : bool
        True if the ast includes a list comprehension, False otherwise.

    """
    for item in ast.walk(pyast):
        if isinstance(item, ast.ListComp):
            return True
    return False


def fetch_helpers(cg):
    """ Fetch the compiler helpers and store in fast locals.

    This function should be called once on a code generator before
    using the 'load_helper' function.

    Parameters
    ----------
    cg : CodeGenerator
        The code generator with which to write the code.

    """
    cg.load_global(COMPILER_HELPERS)
    cg.store_fast(C_HELPERS)


def fetch_globals(cg):
    """ Fetch the globals and store in fast locals.

    Parameters
    ----------
    cg : CodeGenerator
        The code generator with which to write the code.

    """
    cg.load_global('globals')
    cg.call_function()
    cg.store_fast(F_GLOBALS)


def load_helper(cg, name, from_globals=False):
    """ Load a compiler helper onto the TOS.

    The caller should have already invoked the 'fetch_locals' function
    for the code generator before using this function, unless the
    'from_globals' keyword is set to True.

    Parameters
    ----------
    cg : CodeGenerator
        The code generator with which to write the code.

    name : str
        The name of the compiler helper to load onto the TOS.

    from_globals : bool, optional
        If True, the helpers will be loaded from the globals instead of
        the fast locals. The default is False.

    """
    if from_globals:
        cg.load_global(COMPILER_HELPERS)
    else:
        cg.load_fast(C_HELPERS)
    cg.load_const(name)
    cg.binary_subscr()


def load_name(cg, name, local_names):
    """ Load a name onto the TOS.

    If the name exists in the local names set, it is loaded from
    the fast locals. Otherwise, it is loaded from the globals.

    Parameters
    ----------
    cg : CodeGenerator
        The code generator with which to write the code.

    name : str
        The name of the value to load onto the TOS.

    local_names : set
        The set of fast local names available to the code object.

    """
    if name in local_names:
        cg.load_fast(name)
    else:
        cg.load_global(name)


def make_node_list(cg, count):
    """ Create the node list and store in fast locals.

    Parameters
    ----------
    cg : CodeGenerator
        The code generator with which to write the code.

    count : int
        The required size of the node list.

    """
    cg.load_const(None)
    cg.build_list(1)
    cg.load_const(count)
    cg.binary_multiply()
    cg.store_fast(NODE_LIST)


def store_node(cg, index):
    """ Store the node on TOS into the node list.

    The caller should ensure that NODE_LIST exists in fast locals.

    Parameters
    ----------
    cg : CodeGenerator
        The code generator with which to write the code.

    index : int
        The index at which to store the node in the node list.

    """
    cg.load_fast(NODE_LIST)
    cg.load_const(index)
    cg.store_subscr()


def load_node(cg, index):
    """ Load the node at the given index in the node list.

    The caller should ensure that NODE_LIST exists in fast locals.

    Parameters
    ----------
    cg : CodeGenerator
        The code generator with which to write the code.

    index : int
        The index of the parent node in the node list.

    """
    cg.load_fast(NODE_LIST)
    cg.load_const(index)
    cg.binary_subscr()


def append_node(cg, parent, index):
    """ Append the node on the TOS as a child of the specified node.

    The caller should ensure that NODE_LIST exists in fast locals.

    Parameters
    ----------
    cg : CodeGenerator
        The code generator with which to write the code.

    parent : int
        The index of the parent node in the node list.

    index : int
        The index of the target node in the node list.

    """
    load_node(cg, parent)
    cg.load_attr('children')
    cg.load_attr('append')
    load_node(cg, index)
    cg.call_function(1)
    cg.pop_top()


def safe_eval_ast(cg, node, name, lineno, local_names):
    """ Safe eval a Python ast node.

    This method will eval the python code represented by the ast
    in the local namespace. If the code would have the side effect
    of storing a value in the namespace, such as a list comp under
    Python 2, then the expression will be evaluated in it's own
    namespace.

    Parameters
    ----------
    cg : CodeGenerator
        The code generator with which to write the code.

    node : ast.Expression
        The Python expression ast node of interest.

    name : str
        The name to use any internal code object.

    lineno : int
        The line number to use for any internal code object.

    local_names : set
        The set of fast local names available to the code object.

    """
    if not IS_PY3 and has_list_comp(node):
        expr_cg = CodeGenerator()
        expr_cg.filename = cg.filename
        expr_cg.name = name
        expr_cg.firstlineno = lineno
        expr_cg.set_lineno(lineno)
        expr_cg.insert_python_expr(node, trim=False)
        call_args = expr_cg.rewrite_to_fast_locals(local_names)
        expr_code = expr_cg.to_code()
        cg.load_const(expr_code)
        cg.make_function()
        for arg in call_args:
            if arg in local_names:
                cg.load_fast(arg)
            else:
                cg.load_global(arg)
        cg.call_function(len(call_args))
    else:
        expr_cg = CodeGenerator()
        expr_cg.insert_python_expr(node)
        expr_cg.rewrite_to_fast_locals(local_names)
        cg.code_ops.extend(expr_cg.code_ops)


def analyse_globals_and_func_defs(pyast):
    """Collect the explicit 'global' variable names and check for function
    definitions

    Functions definition can exist if a comprehension (list, dict, set) is
    present or if a lambda function exists.

    """
    global_vars = set()
    has_def = False
    for node in ast.walk(pyast):
        if isinstance(node, ast.Global):
            global_vars.update(node.names)
        elif isinstance(node, _FUNC_DEF_NODES):
            has_def = True

    return global_vars, has_def


def rewrite_globals_access(code, global_vars):
    """Update the function code global loads

    This will rewrite the function to convert each LOAD_GLOBAL opcode
    into a LOAD_NAME opcode, unless the associated name is known to have been
    made global via the 'global' keyword.

    """
    inner_ops = code.code
    for idx, (op, op_arg) in enumerate(inner_ops):
        if op == bp.LOAD_GLOBAL and op_arg not in global_vars:
            inner_ops[idx] = (bp.LOAD_NAME, op_arg)


def run_in_dynamic_scope(code, global_vars):
    """Wrap functions defined in operators/decl func to run them in the proper
    dynamic scope.

    This will also rewrite the function to convert each LOAD_GLOBAL opcode
    into a LOAD_NAME opcode, unless the associated name is known to have been
    made global via the 'global' keyword.

    Parameters
    ----------
    code :
        Code object in which functions are defined.

    """
    # Code generator used to modify the bytecode
    cg = CodeGenerator()
    fetch_helpers(cg)

    # Scan all ops to detect function call after GET_ITER
    ops = enumerate(code.code)
    for idx, (op, op_arg) in ops:
        if isinstance(op_arg, bp.Code):
            # Allow to pass the dynamic scope as locals. There is no need
            # to copy it as internal variables are stored in fast locals
            # and hence does not affect the scope content.
            op_arg.newlocals = False
            run_in_dynamic_scope(op_arg, global_vars)
        elif any(op == make_fun_op for make_fun_op in _MAKE_FUNC):
            cg.code_ops.append((op, op_arg))  # func
            load_helper(cg, 'wrap_func')      # func -> wrap
            cg.rot_two()                      # wrap -> func
            cg.load_global('__scope__')       # wrap -> func -> scope
            cg.call_function(2)               # wrapped
            continue

        cg.code_ops.append((op, op_arg))

    code.code = cg.code_ops
    rewrite_globals_access(code, global_vars)


def gen_child_def_node(cg, node, local_names):
    """ Generate the code to create the child def compiler node.

    The caller should ensure that SCOPE_KEY is present in the fast
    locals of the code object.

    Parameters
    ----------
    cg : CodeGenerator
        The code generator with which to write the code.

    node : ChildDef
        The enaml ast node of interest.

    local_names : set
        The set of local names available to the code object.

    """
    # Validate the type of the child
    load_name(cg, node.typename, local_names)
    with cg.try_squash_raise():
        cg.dup_top()
        load_helper(cg, 'validate_declarative')
        cg.rot_two()                            # base -> helper -> base
        cg.call_function(1)                     # base -> retval
        cg.pop_top()                            # base

    # Subclass the child class if needed
    store_types = (StorageExpr, AliasExpr, FuncDef)
    if any(isinstance(item, store_types) for item in node.body):
        if not IS_PY3:
            # On Python 2 directly build the class.
            cg.load_const(node.typename)
            cg.rot_two()
            cg.build_tuple(1)
            cg.build_map()
            cg.load_global('__name__')
            cg.load_const('__module__')
            cg.store_map()                          # name -> bases -> dict
            cg.build_class()                        # class

        else:
            # On Python 3 create the class code
            cg.load_build_class()
            cg.rot_two()                            # builtins.__build_class_ -> base

            class_cg = CodeGenerator()
            class_cg.filename = cg.filename
            class_cg.name = node.typename
            class_cg.firstlineno = node.lineno
            class_cg.set_lineno(node.lineno)

            class_cg.code_ops.append((bp.LOAD_NAME, '__name__'),)
            class_cg.code_ops.append((bp.STORE_NAME, '__module__'),)
            class_cg.load_const(node.typename)
            class_cg.code_ops.append((bp.STORE_NAME, '__qualname__'),)
            class_cg.load_const(None)  # XXX better qualified name
            class_cg.return_value()

            class_code = class_cg.to_code()
            cg.load_const(class_code)
            cg.load_const(None)  # XXX better qualified name
            cg.make_function()

            cg.rot_two()                            # builtins.__build_class_ -> class_func -> base
            cg.load_const(node.typename)
            cg.rot_two()                            # builtins.__build_class_ -> class_func -> class_name -> base
            cg.call_function(3)                     # class


    # Build the declarative compiler node
    store_locals = should_store_locals(node)
    load_helper(cg, 'declarative_node')
    cg.rot_two()
    cg.load_const(node.identifier)
    cg.load_fast(SCOPE_KEY)
    cg.load_const(store_locals)                 # helper -> class -> identifier -> key -> bool
    cg.call_function(4)                         # node


def gen_template_inst_node(cg, node, local_names):
    """ Generate the code to create a template inst compiler node.

    The caller should ensure that SCOPE_KEY is present in the fast
    locals of the code object.

    Parameters
    ----------
    cg : CodeGenerator
        The code generator with which to write the code.

    node : TemplateInst
        The enaml ast node of interest.

    local_names : set
        The set of local names available to the code object.

    """
    # Validate the type of the template.
    load_name(cg, node.name, local_names)
    with cg.try_squash_raise():
        cg.dup_top()
        load_helper(cg, 'validate_template')
        cg.rot_two()
        cg.call_function(1)
        cg.pop_top()

    # Load the arguments for the instantiation call.
    arguments = node.arguments
    for arg in arguments.args:
        safe_eval_ast(cg, arg.ast, node.name, arg.lineno, local_names)
    if arguments.stararg:
        arg = arguments.stararg
        safe_eval_ast(cg, arg.ast, node.name, arg.lineno, local_names)

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
            load_helper(cg, 'validate_unpack_size')
            cg.rot_two()
            cg.load_const(len(names))
            cg.load_const(bool(starname))
            cg.call_function(3)
            cg.pop_top()

    # Load and call the helper to create the compiler node
    load_helper(cg, 'template_inst_node')
    cg.rot_two()
    cg.load_const(names)
    cg.load_const(starname)
    cg.load_fast(SCOPE_KEY)
    cg.load_const(bool(node.body))
    cg.call_function(5)


def gen_template_inst_binding(cg, node, index):
    """ Generate the code for a template inst binding.

    The caller should ensure that UNPACK_MAP and F_GLOBALS are present
    in the fast locals of the code object.

    Parameters
    ----------
    cg : CodeGenerator
        The code generator with which to write the code.

    node : TemplateInstBinding
        The enaml ast node of interest.

    index : int
        The index of the template inst node in the node list.

    """
    op_node = node.expr
    mode = COMPILE_MODE[type(op_node.value)]
    code = compile(op_node.value.ast, cg.filename, mode=mode)
    with cg.try_squash_raise():
        cg.set_lineno(node.lineno)
        load_helper(cg, 'run_operator')
        load_node(cg, index)
        cg.load_fast(UNPACK_MAP)
        cg.load_const(node.name)
        cg.binary_subscr()
        cg.load_const(node.chain)
        cg.load_const(op_node.operator)
        cg.load_const(code)
        cg.load_fast(F_GLOBALS)
        cg.call_function(6)
        cg.pop_top()


def gen_operator_binding(cg, node, index, name):
    """ Generate the code for an operator binding.

    The caller should ensure that F_GLOBALS and NODE_LIST are present
    in the fast locals of the code object.

    Parameters
    ----------
    cg : CodeGenerator
        The code generator with which to write the code.

    node : OperatorExpr
        The enaml ast node of interest.

    index : int
        The index of the target node in the node list.

    name : str
        The attribute name to be bound.

    """
    mode = COMPILE_MODE[type(node.value)]
    global_vars, has_defs = analyse_globals_and_func_defs(node.value.ast)
    # In mode exec, the body of the operator has been wrapped in a function def
    # after the compilation we extract the function code
    if mode == 'exec':
        code = compile(node.value.ast, cg.filename, mode=mode)
        for op, op_arg in bp.Code.from_code(code).code:
            if isinstance(op_arg, bp.Code):
                code = op_arg.to_code()
                break
    else:
        code = compile(node.value.ast, cg.filename, mode=mode)

    b_code = bp.Code.from_code(code)
    if has_defs:
        run_in_dynamic_scope(b_code, global_vars)
    else:
        rewrite_globals_access(b_code, global_vars)
    code = b_code.to_code()

    with cg.try_squash_raise():
        cg.set_lineno(node.lineno)
        load_helper(cg, 'run_operator')
        load_node(cg, index)
        cg.dup_top()
        cg.load_const(name)
        cg.load_const(node.operator)
        cg.load_const(code)
        cg.load_fast(F_GLOBALS)
        cg.call_function(6)
        cg.pop_top()


def gen_alias_expr(cg, node, index):
    """ Generate the code for an alias expression.

    The caller should ensure that NODE_LIST is present in the fast
    locals of the code object.

    Parameters
    ----------
    cg : CodeGenerator
        The code generator with which to write the code.

    node : AliasExpr
        The enaml ast node of interest.

    index : int
        The index of the target node in the node list.

    """
    with cg.try_squash_raise():
        cg.set_lineno(node.lineno)
        load_helper(cg, 'add_alias')
        load_node(cg, index)
        cg.load_const(node.name)
        cg.load_const(node.target)
        cg.load_const(node.chain)
        cg.call_function(4)
        cg.pop_top()


def gen_storage_expr(cg, node, index, local_names):
    """ Generate the code for a storage expression.

    The caller should ensure that NODE_LIST is present in the fast
    locals of the code object.

    Parameters
    ----------
    cg : CodeGenerator
        The code generator with which to write the code.

    node : StorageExpr
        The enaml ast node of interest.

    index : int
        The index of the target node in the node list.

    local_names : set
        The set of fast local names available to the code object.

    """
    with cg.try_squash_raise():
        cg.set_lineno(node.lineno)
        load_helper(cg, 'add_storage')
        load_node(cg, index)
        cg.load_const(node.name)
        if node.typename:
            load_name(cg, node.typename, local_names)
        else:
            cg.load_const(None)
        cg.load_const(node.kind)
        cg.call_function(4)
        cg.pop_top()


def _insert_decl_function(cg, funcdef):
    """ Create and place a declarative function on the TOS.

    This will rewrite the function to convert each LOAD_GLOBAL opcode
    into a LOAD_NAME opcode, unless the associated name was explicitly
    made global via the 'global' keyword.

    Parameters
    ----------
    funcdef : ast node
        The python FunctionDef ast node.

    """
    # collect the explicit 'global' variable names and check for the presence
    # of comprehensions (list, dict, set).
    global_vars, has_defs = analyse_globals_and_func_defs(funcdef)

    # generate the code object which will create the function
    mod = ast.Module(body=[funcdef])
    code = compile(mod, cg.filename, mode='exec')

    # convert to a byteplay object and remove the leading and
    # trailing ops: SetLineno STORE_NAME LOAD_CONST RETURN_VALUE
    outer_ops = bp.Code.from_code(code).code[1:-3]

    # the stack now looks like the following:
    #   ...
    #   ...
    #   LOAD_CONST      (<code object>)
    #   MAKE_FUCTION    (num defaults)      // TOS

    # extract the inner code object which represents the actual
    # function code and update its flags
    if not IS_PY3:
        inner = outer_ops[-2][1]  # On Python 2 there is no qualified name
    else:
        inner = outer_ops[-3][1]  # On Python 3 a function has a qualified name
    inner.newlocals = False

    # On Python 3 all comprehensions use a function call (on Python 2 only dict
    # and set). To avoid scoping issues the function call is run in the dynamic
    # scope.
    if has_defs:
        run_in_dynamic_scope(inner, global_vars)
    else:
        rewrite_globals_access(inner, global_vars)

    # inline the modified code ops into the code generator
    cg.code_ops.extend(outer_ops)


def gen_decl_funcdef(cg, node, index):
    """ Generate the code for a declarative function definition.

    The caller should ensure that NODE_LIST is present in the fast
    locals of the code object.

    Parameters
    ----------
    cg : CodeGenerator
        The code generator with which to write the code.

    node : FuncDef
        The enaml ast node of interest.

    index : int
        The index of the target node in the node list.

    """
    with cg.try_squash_raise():
        cg.set_lineno(node.lineno)
        load_helper(cg, 'add_decl_function')
        load_node(cg, index)
        _insert_decl_function(cg, node.funcdef)
        cg.load_const(node.is_override)
        cg.call_function(3)
        cg.pop_top()


class CompilerBase(ASTVisitor):
    """ A base class for defining compilers.

    """
    #: The filename for the code being generated.
    filename = Str()

    #: The code generator to use for this compiler.
    code_generator = Typed(CodeGenerator)

    def _default_code_generator(self):
        """ Create the default code generator instance.

        """
        return CodeGenerator(filename=self.filename)
