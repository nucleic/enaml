#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import ast
import types

from .byteplay import (
    Code, LOAD_FAST, CALL_FUNCTION, LOAD_GLOBAL, STORE_FAST, LOAD_CONST,
    RETURN_VALUE, POP_TOP, STORE_NAME, LOAD_NAME, DUP_TOP, DELETE_NAME,
    DELETE_FAST, LIST_APPEND, BUILD_TUPLE, SetLineno
)
from .code_tracing import inject_tracing, inject_inversion


# Increment this number whenever the compiler changes the code which it
# generates. This number is used by the import hooks to know which version
# of a .enamlc file is valid for the Enaml compiler version in use. If
# this number is not incremented on change, it may result in .enamlc
# files which fail on import.
#
# Version History
# ---------------
# 1 : Initial compiler version - 2 February 2012
# 2 : Update line number handling - 26 March 2012
#     When compiling code objects with mode='eval', Python ignores the
#     line number specified by the ast. The workaround is to compile the
#     code object, then make a new copy of it with the proper firstlineno
#     set via the types.CodeType constructor.
# 3 : Update the generated code to remove the toolkit - 21 June 2012
#     This updates the compiler for the coming switch to async UI's
#     which will see the removal of the Toolkit concept. The only
#     magic scope maintained is for that of operators.
# 4 : Update component building - 27 July 2012
#     This updates the compiler to handle the new Enaml creation semantics
#     that don't rely on __enaml_call__. Instead the parent is passed
#     directly to the component cls which is a subclass of Declarative.
#     That class handles calling the builder functions upon instance
#     creation. This allows us to get rid of the EnamlDef class and
#     make enamldef constructs proper subclasses of Declarative.
# 5 : Change the import names - 28 July 2012
#     This changes the imported helper name from _make_decl_subclass_
#     to _make_enamldef_helper_ which is more descriptive, but equally
#     mangled. It also updates the method name used on the Declarative
#     component for adding attribute from _add_decl_attr to the more
#     descriptive _add_user_attribute. Finally, it adds the eval_compile
#     function for compiling Python code in 'eval' mode with proper line
#     number handling.
# 6 : Compile with code tracing - 24 November 2012
#     This updates the compiler to generate code using the idea of code
#     tracing instead of monitors and inverters. The compiler compiles
#     the expressions into functions which are augmented to accept
#     additional arguments. These arguments are tracer objects which will
#     have methods called in response to bytecode ops executing. These
#     methods can then attach listeners as necessary. This is an easier
#     paradigm to develop with than the previous incarnation. This new
#     way also allows the compiler to generate the final code objects
#     upfront, instead of needed to specialize at runtime for a given
#     operator context. This results in a much smaller footprint since
#     then number of code objects created is n instead of n x m.
# 7 : Fix bug with local deletes - 10 December 2012
#     This fixes a bug in the locals optimization where the DELETE_NAME
#     opcode was not being replaced with DELETE_FAST.
# 8 : Generate description dicts instead of builders - 27 January 2013
#     This updates the compiler to generate marshalable description
#     dicts instead of builder functions. The responsibility of building
#     out the object tree has been shifted to the Declarative class. This
#     is a touch slower, but provides a ton more flexibility and enables
#     templated components like `Looper` and `Conditional`.
# 9 : Generate description dicts for attrs and events - 11 March 2013
#     This augments the description dictionary for an enamldef with
#     a list of dicts describing the 'attr' and 'event' keywords for
#     the given enamldef block. These dicts are used by the compiler
#     helper to generate atom members for the new class.
# 10 : Class time post processing and decorators - 17 March 2013
#     This moves a large amount of processing from instantiation time
#     to class definition time. In particular, operators are now bound
#     at the class level. This also adds support for decorators on an
#     enamldef block.
COMPILER_VERSION = 10


# The Enaml compiler translates an Enaml AST into a decription dict
# which contains information about the tree, including code objects
# which were compiled with support for runtime introspection. The
# reason dictionaries are used instead of the AST nodes is because
# the dictionaries can be marshaled into a .enamlc file, which is
# faster on subsequent loading than reparsing the entire file.
#
#
# Given this sample declaration in Enaml::
#
# FooWindow(Window): foo:
#     attr a = '12'
#     PushButton: btn:
#         text = 'clickme'
#
# The compiler generates a new class called FooWindow which uses Window
# as the base class. The new class is given the following description
# dictionary to use when populating new instances. The block and filename
# information is repeated for each logical production because it makes
# easier for runtime code to generate useful exceptions without needed
# to pass the entire parse tree around at every step. The code objects
# in the binding dictionaries have had their bytecode rewritten to
# support Enaml's runtime introspection facilities.
#
# description = {
#     'enamldef': True,
#     'type': 'FooWindow',
#     'base': 'Window',
#     'doc': '',
#     'lineno': 1,
#     'identifier': 'foo',
#     'filename': 'sample.enaml',
#     'block': 'FooWindow',
#     'children': [
#         { 'enamldef': False,
#           'type': 'PushButton',
#           'lineno': 3,
#           'identifier': 'btn',
#           'filename': 'sample.enaml',
#           'block': 'FooWindow',
#           'children': [],
#           'bindings': [
#               { 'operator': '=',
#                 'code': <codeobject>,
#                 'name': 'text',
#                 'lineno': 4,
#                 'filename': 'sample.enaml',
#                 'block': 'FooWindow',
#               },
#           ],
#         },
#     ],
#     'bindings': [
#         { 'operator': '=',
#           'code': <codeobject>,
#           'name': 'a',
#           'lineno': 2,
#           'filename': 'sample.enaml',
#           'block': 'FooWindow',
#         },
#     ],
# }


#------------------------------------------------------------------------------
# Compiler Helpers
#------------------------------------------------------------------------------
# Code that will be executed at the top of every enaml module
STARTUP = [
    'from enaml.core.compiler_helpers import _make_enamldef_helper_',
    'from enaml.core.compiler_helpers import _post_process_enamldefs_',
    '_enamldef_descriptions_ = []',
]


# Cleanup code that will be included in every compiled enaml module
CLEANUP = [
    'del _make_enamldef_helper_',
    'del _post_process_enamldefs_',
    'del _enamldef_descriptions_',
]


def update_firstlineno(code, firstlineno):
    """ Returns a new code object with an updated first line number.

    """
    return types.CodeType(
        code.co_argcount, code.co_nlocals, code.co_stacksize, code.co_flags,
        code.co_code, code.co_consts, code.co_names, code.co_varnames,
        code.co_filename, code.co_name, firstlineno, code.co_lnotab,
        code.co_freevars, code.co_cellvars,
    )


#------------------------------------------------------------------------------
# Expression Compilers
#------------------------------------------------------------------------------
def replace_global_loads(codelist, explicit=None):
    """ A code transformer which rewrites LOAD_GLOBAL opcodes.

    This transform will replace the LOAD_GLOBAL opcodes with LOAD_NAME
    opcodes. The operation is performed in-place.

    Parameters
    ----------
    codelist : list
        The list of byteplay code ops to modify.

    explicit : set or None
        The set of global names declared explicitly and which should
        remain untransformed.

    """
    # Replacing LOAD_GLOBAL with LOAD_NAME enables dynamic scoping by
    # way of a custom locals mapping. The `call_func` function in the
    # `funchelper` module enables passing a locals map to a function.
    explicit = explicit or set()
    for idx, (op, op_arg) in enumerate(codelist):
        if op == LOAD_GLOBAL and op_arg not in explicit:
            codelist[idx] = (LOAD_NAME, op_arg)


def optimize_locals(codelist):
    """ Optimize the given code object for fast locals access.

    All STORE_NAME opcodes will be replaced with STORE_FAST. Names which
    are stored and then loaded via LOAD_NAME are rewritten to LOAD_FAST
    and DELETE_NAME is rewritten to DELETE_FAST. This transformation is
    applied in-place.

    Parameters
    ----------
    codelist : list
        The list of byteplay code ops to modify.

    """
    fast_locals = set()
    for idx, (op, op_arg) in enumerate(codelist):
        if op == STORE_NAME:
            fast_locals.add(op_arg)
            codelist[idx] = (STORE_FAST, op_arg)
    for idx, (op, op_arg) in enumerate(codelist):
        if op == LOAD_NAME and op_arg in fast_locals:
            codelist[idx] = (LOAD_FAST, op_arg)
        elif op == DELETE_NAME and op_arg in fast_locals:
            codelist[idx] = (DELETE_FAST, op_arg)


def compile_simple(py_ast, filename):
    """ Compile an ast into a code object implementing operator `=`.

    Parameters
    ----------
    py_ast : ast.Expression
        A Python ast Expression node.

    filename : str
        The filename which generated the expression.

    Returns
    -------
    result : types.CodeType
        A Python code object which implements the desired behavior.

    """
    code = compile(py_ast, filename, mode='eval')
    code = update_firstlineno(code, py_ast.lineno)
    bp_code = Code.from_code(code)
    replace_global_loads(bp_code.code)
    optimize_locals(bp_code.code)
    bp_code.newlocals = False
    return bp_code.to_code()


def compile_notify(py_ast, filename):
    """ Compile an ast into a code object implementing operator `::`.

    Parameters
    ----------
    py_ast : ast.Module
        A Python ast Module node.

    filename : str
        The filename which generated the expression.

    Returns
    -------
    result : types.CodeType
        A Python code object which implements the desired behavior.

    """
    explicit_globals = set()
    for node in ast.walk(py_ast):
        if isinstance(node, ast.Global):
            explicit_globals.update(node.names)
    code = compile(py_ast, filename, mode='exec')
    bp_code = Code.from_code(code)
    replace_global_loads(bp_code.code, explicit_globals)
    optimize_locals(bp_code.code)
    bp_code.newlocals = False
    return bp_code.to_code()


def compile_subscribe(py_ast, filename):
    """ Compile an ast into a code object implementing operator `<<`.

    Parameters
    ----------
    py_ast : ast.Expression
        A Python ast Expression node.

    filename : str
        The filename which generated the expression.

    Returns
    -------
    result : types.CodeType
        A Python code object which implements the desired behavior.

    """
    code = compile(py_ast, filename, mode='eval')
    code = update_firstlineno(code, py_ast.lineno)
    bp_code = Code.from_code(code)
    replace_global_loads(bp_code.code)
    optimize_locals(bp_code.code)
    bp_code.code = inject_tracing(bp_code.code)
    bp_code.newlocals = False
    bp_code.args = ('_[tracer]',) + bp_code.args
    return bp_code.to_code()


def compile_update(py_ast, filename):
    """ Compile an ast into a code object implementing operator `>>`.

    Parameters
    ----------
    py_ast : ast.Expression
        A Python ast Expression node.

    filename : str
        The filename which generated the expression.

    Returns
    -------
    result : types.CodeType
        A Python code object which implements the desired behavior.

    """
    code = compile(py_ast, filename, mode='eval')
    code = update_firstlineno(code, py_ast.lineno)
    bp_code = Code.from_code(code)
    replace_global_loads(bp_code.code)
    optimize_locals(bp_code.code)
    bp_code.code = inject_inversion(bp_code.code)
    bp_code.newlocals = False
    bp_code.args = ('_[inverter]', '_[value]') + bp_code.args
    return bp_code.to_code()


def compile_delegate(py_ast, filename):
    """ Compile an ast into a code object implementing operator `:=`.

    This will generate two code objects: one which is equivalent to
    operator `<<` and another which is equivalent to `>>`.

    Parameters
    ----------
    py_ast : ast.Expression
        A Python ast Expression node.

    filename : str
        The filename which generated the expression.

    Returns
    -------
    result : tuple
        A 2-tuple of types.CodeType equivalent to operators `<<` and
        `>>` respectively.

    """
    code = compile(py_ast, filename, mode='eval')
    code = update_firstlineno(code, py_ast.lineno)
    bp_code = Code.from_code(code)
    bp_code.newlocals = False
    codelist = bp_code.code[:]
    bp_args = tuple(bp_code.args)
    replace_global_loads(codelist)
    optimize_locals(codelist)
    sub_list = inject_tracing(codelist)
    bp_code.code = sub_list
    bp_code.args = ('_[tracer]',) + bp_args
    sub_code = bp_code.to_code()
    upd_list = inject_inversion(codelist)
    bp_code.code = upd_list
    bp_code.args = ('_[inverter]', '_[value]') + bp_args
    upd_code = bp_code.to_code()
    return (sub_code, upd_code)


COMPILE_OP_MAP = {
    '=': compile_simple,
    '::': compile_notify,
    '<<': compile_subscribe,
    '>>': compile_update,
    ':=': compile_delegate,
}


def scope_name_generator():
    stem = '__locals_%d__'
    i = 0
    while True:
        yield stem % i
        i += 1
scope_name_generator = scope_name_generator()


#------------------------------------------------------------------------------
# Node Visitor
#------------------------------------------------------------------------------
class _NodeVisitor(object):
    """ A node visitor class that is used as base class for the various
    Enaml compilers.

    """
    def visit(self, node):
        """ The main visitor dispatch method.

        Unhandled nodes will raise an error.

        """
        name = 'visit_%s' % node.__class__.__name__
        try:
            method = getattr(self, name)
        except AttributeError:
            method = self.default_visit
        method(node)

    def visit_nonstrict(self, node):
        """ A nonstrict visitor dispatch method.

        Unhandled nodes will be ignored.

        """
        name = 'visit_%s' % node.__class__.__name__
        try:
            method = getattr(self, name)
        except AttributeError:
            pass
        else:
            method(node)

    def default_visit(self, node):
        """ The default visitor method. Raises an error since there
        should not be any unhandled nodes.

        """
        raise ValueError('Unhandled Node %s.' % node)


#------------------------------------------------------------------------------
# Declaration Compiler
#------------------------------------------------------------------------------
class DeclarationCompiler(_NodeVisitor):
    """ A visitor which compiles a Declaration node into a code object.

    """
    @classmethod
    def compile(cls, node, filename):
        """ The main entry point of the DeclarationCompiler.

        This compiler compiles the given Declaration node into a
        description dictionary which can be used to build out the
        component tree at run time.

        Top assist with debugging, every production generated by the
        compiler has the filename, lineno, and block from where it was
        generated.

        Parameters
        ----------
        node : Declaration
            The Declaration node to compiler.

        filename : str
            The string filename to use for the description.

        """
        compiler = cls(filename)
        compiler.visit(node)
        return compiler.stack.pop()

    def __init__(self, filename):
        """ Initialize a DeclarationCompiler.

        Parameters
        ----------
        filename : str
            The filename string to use for the descriptions.

        """
        self.filename = filename
        self.block = '<undefined>'
        self.stack = []

    def visit_Declaration(self, node):
        """ Creates the description dict for a declaration.

        This method will create the root description dict, push it onto
        the stack, then dispatch to the node's body nodes.

        """
        self.block = node.name
        obj = {
            'enamldef': True,
            'scopename': '',
            'type': node.name,
            'base': node.base,
            'doc': node.doc,
            'lineno': node.lineno,
            'identifier': node.identifier,
            'filename': self.filename,
            'block': self.block,
            'children': [],
            'bindings': [],
            'attrs': [],
        }
        self.stack.append(obj)
        for item in node.body:
            self.visit(item)

        # Pass over the block and check for identifiers.
        has_idents = False
        s = [obj]
        while s:
            d = s.pop()
            if d['identifier']:
                has_idents = True
                break
            s.extend(d['children'])

        # If the block has identifiers, create new scope name.
        if has_idents:
            scopename = scope_name_generator.next()
            s = [obj]
            while s:
                d = s.pop()
                d['scopename'] = scopename
                for b in d['bindings']:
                    b['scopename'] = scopename
                s.extend(d['children'])

    def visit_AttributeDeclaration(self, node):
        """ Add an attribute declaration to the description.

        """
        decl = {
            'lineno': node.lineno,
            'block': self.block,
            'filename': self.filename,
            'name': node.name,
            'type': node.type,
            'is_event': node.is_event,
        }
        self.stack[-1]['attrs'].append(decl)
        default = node.default
        if default is not None:
            self.visit(node.default)

    def visit_AttributeBinding(self, node):
        """ Add an attribute binding to the description.

        This visitor creates the binding dict for the given node and
        adds it to the bindings list for the object at the top of the
        stack. It compiles the python ast for the bound expression into
        a code object that has been hooked for the given operator.

        """
        obj = self.stack[-1]
        py_ast = node.binding.expr.py_ast
        op = node.binding.op
        op_compiler = COMPILE_OP_MAP[op]
        code = op_compiler(py_ast, self.filename)
        binding = {
            'operator': op,
            'code': code,
            'name': node.name,
            'lineno': node.binding.lineno,
            'filename': self.filename,
            'block': self.block,
            'scopename': '',
        }
        obj['bindings'].append(binding)

    def visit_Instantiation(self, node):
        """ Create the description for an instantiation.

        This visitor creates a new dictionary for the object, pushes
        it onto the stack, dispatches to the body nodes, then pops
        the item and adds it to the children of the object at the top
        of the stack.

        """
        obj = {
            'enamldef': False,
            'scopename': '',
            'type': node.name,
            'lineno': node.lineno,
            'identifier': node.identifier,
            'filename': self.filename,
            'block': self.block,
            'children': [],
            'bindings': [],
            'attrs': [],
        }
        self.stack.append(obj)
        for item in node.body:
            self.visit(item)
        self.stack.pop()
        self.stack[-1]['children'].append(obj)


#------------------------------------------------------------------------------
# Enaml Compiler
#------------------------------------------------------------------------------
class EnamlCompiler(_NodeVisitor):
    """ A visitor that will compile an enaml module ast node.

    The entry point is the `compile` classmethod which will compile
    the ast into an appropriate python code object for a module.

    """
    @classmethod
    def compile(cls, module_ast, filename):
        """ The main entry point of the compiler.

        Parameters
        ----------
        module_ast : Instance(enaml_ast.Module)
            The enaml module ast node that should be compiled.

        filename : str
            The string filename of the module ast being compiled.

        """
        # Generate the startup code for the module
        module_ops = [(SetLineno, 1)]
        for start in STARTUP:
            start_code = compile(start, filename, mode='exec')
            bp_code = Code.from_code(start_code)
            # Skip the SetLineo and ReturnValue codes
            module_ops.extend(bp_code.code[1:-2])

        # Add in the code ops for the module
        compiler = cls(filename)
        compiler.visit(module_ast)
        module_ops.extend(compiler.code_ops)

        module_ops.extend([
           (LOAD_GLOBAL, '_post_process_enamldefs_'),
           (LOAD_GLOBAL, '_enamldef_descriptions_'),
           (LOAD_NAME, 'globals'),
           (CALL_FUNCTION, 0x0000),
           (CALL_FUNCTION, 0x0002),
           (POP_TOP, None),
        ])

        # Generate the cleanup code for the module
        for end in CLEANUP:
            end_code = compile(end, filename, mode='exec')
            bp_code = Code.from_code(end_code)
            # Skip the SetLineo and ReturnValue codes
            module_ops.extend(bp_code.code[1:-2])

        # Add in the final return value ops
        module_ops.extend([
            (LOAD_CONST, None),
            (RETURN_VALUE, None),
        ])

        # Generate and return the module code object.
        mod_code = Code(
            module_ops, [], [], False, False, False, '',  filename, 0, '',
        )
        return mod_code.to_code()

    def __init__(self, filename):
        """ Initialize an EnamlCompiler.

        Parameters
        ----------
        filename : str
            The string filename of the module ast being compiled.

        """
        self.filename = filename
        self.code_ops = []

    def visit_Module(self, node):
        """ The Module node visitor method.

        This visitor dispatches to all of the body nodes of the module.

        """
        for item in node.body:
            self.visit(item)

    def visit_Python(self, node):
        """ The Python node visitor method.

        This visitor adds a chunk of raw Python into the module.

        """
        py_code = compile(node.py_ast, self.filename, mode='exec')
        bp_code = Code.from_code(py_code)
        # Skip the SetLineo and ReturnValue codes
        self.code_ops.extend(bp_code.code[1:-2])

    def visit_Declaration(self, node):
        """ The Declaration node visitor.

        This generates the bytecode ops whic create a new type for the
        enamldef and then adds the user defined attributes and events.
        It also dispatches to the DeclarationCompiler which will create
        the builder function for the new type.

        """
        code_ops = self.code_ops
        name = node.name
        description = DeclarationCompiler.compile(node, self.filename)
        code_ops.append((LOAD_NAME, '_enamldef_descriptions_'))
        for dec in node.decorators:
            code = compile(dec, self.filename, mode='eval')
            bpcode = Code.from_code(code).code
            code_ops.extend(bpcode[:-1])  # skip the return value op
        code_ops.extend([
            (SetLineno, node.lineno),
            (LOAD_NAME, '_make_enamldef_helper_'),  # Foo = _make_enamldef_helper_(name, base, description, globals)
            (LOAD_CONST, name),
            (LOAD_NAME, node.base),
            (LOAD_CONST, description),  # description is a marshalable dict
            (LOAD_NAME, 'globals'),
            (CALL_FUNCTION, 0x0000),
            (CALL_FUNCTION, 0x0004),
        ])
        for dec in node.decorators:
            code_ops.append((CALL_FUNCTION, 0x0001))
        code_ops.extend([
            (DUP_TOP, None),
            (STORE_NAME, name),
            (LOAD_CONST, description),
            (BUILD_TUPLE, 2),
            (LIST_APPEND, 1),
            (POP_TOP, None),
        ])
