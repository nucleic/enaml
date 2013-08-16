#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import ast
import sys
import types

from .byteplay import (
    Code, LOAD_FAST, CALL_FUNCTION, LOAD_GLOBAL, STORE_FAST, LOAD_CONST,
    RETURN_VALUE, STORE_NAME, LOAD_NAME, DELETE_NAME, DELETE_FAST, DUP_TOP,
    ROT_TWO, SetLineno
)


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
# 11 : Fix a bug in code generation for Python 2.6 - 18 March 2013
#     On Python 2.6 the LIST_APPEND instruction consumes the TOS. This
#     update adds a check for running on < 2.7 and dups the TOS.
# 12 : Post process an enamldef immediately. - 18 March 2013
#     This removes the need for the 2.6 check from version 11 since it
#     does not rely on the LIST_APPEND instruction. It almost means
#     that widget names must appear before they are used, just like in
#     normal Python class bodies.
# 13 : Move the post processing of enamldefs to before running the
#     decorators. This means a decorator gets a complete class.
# 14 : Updates to the parser and ast to be more structured - 22 March 2013
#     This updates ast generated by the parser and updates the process
#     for class creation when a module is imported. The serialized data
#     which lives in the code object is unpacked into a construction
#     tree which is then used for various transformations.
COMPILER_VERSION = 14


#------------------------------------------------------------------------------
# Compiler Helpers
#------------------------------------------------------------------------------
# Code that will be executed at the top of every enaml module
STARTUP = [
    'from enaml.core.compiler_helpers import __make_enamldef_helper, __add_user_storage',
    'from enaml.operators import __get_operators',
]


# Cleanup code that will be included in every compiled enaml module
CLEANUP = [
    'del __make_enamldef_helper',
    'del __add_use_storage',
    'del __get_operators',
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
# EnamlDef Compiler
#------------------------------------------------------------------------------
class EnamlDefCompiler(_NodeVisitor):
    """ A visitor which compiles an EnamlDef into a marshallable dict.

    """
    @classmethod
    def compile(cls, node, filename):
        """ The main entry point of the EnamlDefCompiler.

        This compiler compiles the given EnamlDef node into a dictionary
        which can be used to build out the component tree at run time.

        Parameters
        ----------
        node : EnamlDef
            The EnamlDef node to compile.

        filename : string
            The string filename to use for the enamldef.

        """
        compiler = cls(filename)
        compiler.visit(node)
        return compiler.stack.pop()

    def __init__(self, filename):
        self.filename = filename
        self.ops = []

    def visit_EnamlDef(self, node):
        for item in node.body:
            self.visit(item)

    def visit_StorageDef(self, node):
        self.ops.extend([                       # TOS == new class
            (LOAD_GLOBAL, '__add_use_storage'), # class -> helper
            (ROT_TWO, None),                    # helper -> class
            (LOAD_CONST, node.name),            # helper -> class -> name
        ])
        if node.typename:
            self.ops.append(
                (LOAD_GLOBAL, node.typename)    # helper -> class -> name -> type
            )
        else:
            self.ops.append(
                (LOAD_CONST, None)              # helper -> class -> name -> None
            )
        self.ops.extend([
            (LOAD_CONST, node.kind),            # helper -> class -> name -> type | None -> 'event' | 'attr'
            (CALL_FUNCTION, 0x0004),
        ])

        self.stack[-1]['storage_defs'].append(storage_def)
        if node.expr is not None:
            self.visit_Binding(node)

    def visit_Binding(self, node):
        opexpr = node.expr
        pyast = opexpr.value.ast
        opcompiler = COMPILE_OP_MAP[opexpr.operator]
        code = opcompiler(pyast, self.filename)
        binding = {
            'lineno': node.lineno,
            'name': node.name,
            'operator': opexpr.operator,
        }
        if isinstance(code, tuple):
            code, auxcode = code
            binding['code'] = code
            binding['auxcode'] = auxcode
        else:
            binding['code'] = code
            binding['auxcode'] = None
        self.stack[-1]['bindings'].append(binding)

    def visit_ChildDef(self, node):
        obj = {
            'lineno': node.lineno,
            'typename': node.typename,
            'identifier': node.identifier,
            'filename': self.filename,
            'storage_defs': [],
            'bindings': [],
            'child_defs': [],
        }
        self.stack.append(obj)
        for item in node.body:
            self.visit(item)
        self.stack.pop()
        self.stack[-1]['child_defs'].append(obj)


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

        filename : string
            The string filename of the module ast being compiled.

        Returns
        -------
        result : types.CodeType
            The code object for the compiled module.

        """
        # Protect against unicode filenames, which are incompatible
        # with code objects created via types.CodeType
        if isinstance(filename, unicode):
            filename = filename.encode(sys.getfilesystemencoding())

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
        self.filename = filename
        self.code_ops = []

    def visit_Module(self, node):
        for item in node.body:
            self.visit(item)

    def visit_Python(self, node):
        py_code = compile(node.ast, self.filename, mode='exec')
        bp_code = Code.from_code(py_code)
        # Skip the SetLineo and ReturnValue codes
        self.code_ops.extend(bp_code.code[1:-2])

    def visit_EnamlDef(self, node):
        code_ops = self.code_ops
        dct = EnamlDefCompiler.compile(node, self.filename)
        for decorator in node.decorators:
            code = compile(decorator.ast, self.filename, mode='eval')
            bpcode = Code.from_code(code).code
            code_ops.extend(bpcode[:-1])  # skip the return value op
        code_ops.extend([
            (SetLineno, node.lineno),
            (LOAD_NAME, '__make_enamldef_helper'),  # Foo = __make_enamldef_helper(dct, globals)
            (LOAD_CONST, dct),                      # dct is a marshalable description dict
            (LOAD_NAME, 'globals'),
            (CALL_FUNCTION, 0x0000),
            (CALL_FUNCTION, 0x0002),
        ])
        for dec in node.decorators:
            code_ops.append((CALL_FUNCTION, 0x0001))
        code_ops.append((STORE_NAME, node.typename))
