#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys

from atom.api import Typed

from . import byteplay as bp
from .compiler_base import CompilerBase
from .enamldef_compiler import EnamlDefCompiler
from .template_compiler import TemplateCompiler


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
#     does not rely on the LIST_APPEND instruction. It also means
#     that widget names must appear before they are used, just like in
#     normal Python class bodies.
# 13 : Move the post processing of enamldefs to before running the
#     decorators. This means a decorator gets a complete class.
# 14 : Updates to the parser and ast to be more structured - 22 March 2013
#     This updates ast generated by the parser and updates the process
#     for class creation when a module is imported. The serialized data
#     which lives in the code object is unpacked into a construction
#     tree which is then used for various transformations.
# 15 : Complete reimplementation of the expression engine - 22 August 2013
#     This updates the compiler to generate the building logic so that
#     all of the type resolution and type hierarchy building is performed
#     at import time using native code instead of serialized dict and a
#     runtime resolver object (I have no idea what I was thinking with
#     with compiler versions 9 - 14).
COMPILER_VERSION = 15


# Code that will be executed at the top of every enaml module
STARTUP = ['from enaml.core.compiler_helpers import __compiler_helpers']


# Cleanup code that will be included at the end of every enaml module
CLEANUP = []


class EnamlCompiler(CompilerBase):
    """ A compiler which will compile an Enaml module.

    The entry point is the `compile` classmethod which will compile
    the ast into an appropriate python code object for a module.

    """
    #: The set of templates created by the compiler.
    template_vars = Typed(set, ())

    @classmethod
    def compile(cls, module_ast, filename):
        """ The main entry point of the compiler.

        Parameters
        ----------
        module_ast : enaml_ast.Module
            The enaml module ast node that should be compiled.

        filename : str
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
        module_ops = [(bp.SetLineno, 1)]
        for start in STARTUP:
            start_code = compile(start, filename, mode='exec')
            bp_code = bp.Code.from_code(start_code)
            # Skip the SetLineo and ReturnValue codes
            module_ops.extend(bp_code.code[1:-2])

        # Add in the code ops for the module
        compiler = cls(filename=filename)
        compiler.visit(module_ast)
        module_ops.extend(compiler.code_ops)

        # Generate the cleanup code for the module
        for end in CLEANUP:
            end_code = compile(end, filename, mode='exec')
            bp_code = bp.Code.from_code(end_code)
            # Skip the SetLineo and ReturnValue codes
            module_ops.extend(bp_code.code[1:-2])

        # Add in the final return value ops
        module_ops.extend([
            (bp.LOAD_CONST, None),
            (bp.RETURN_VALUE, None),
        ])

        # Generate and return the module code object.
        mod_code = bp.Code(
            module_ops, [], [], False, False, False, '',  filename, 0, None,
        )
        return mod_code.to_code()

    #--------------------------------------------------------------------------
    # Visitors
    #--------------------------------------------------------------------------
    def visit_Module(self, node):
        """ The compiler visitor for a Module node.

        """
        for item in node.body:
            self.visit(item)

    def visit_PythonModule(self, node):
        """ The compiler visitor for a PythonModule node.

        """
        code = compile(node.ast, self.filename, mode='exec')
        bp_code = bp.Code.from_code(code)
        self.set_lineno(node.lineno)
        # Skip the SetLineo and ReturnValue codes
        self.code_ops.extend(bp_code.code[1:-2])

    def visit_EnamlDef(self, node):
        """ The compiler visitor for an EnamlDef node.

        """
        # Load the decorators
        for decorator in node.decorators:
            code = compile(decorator.ast, self.filename, mode='eval')
            bp_code = bp.Code.from_code(code).code
            self.code_ops.extend(bp_code[:-1])  # skip the return value op

        # Generate the enamldef class
        code = EnamlDefCompiler.compile(node, self.filename)
        self.code_ops.extend([              # decorators
            (bp.LOAD_CONST, code),          # decorators -> code
            (bp.MAKE_FUNCTION, 0),          # decorators -> function
            (bp.CALL_FUNCTION, 0x0000),     # decorators -> class
        ])

        # Invoke the decorators
        for decorator in node.decorators:
            self.code_ops.append((bp.CALL_FUNCTION, 0x0001))

        # Store the result into the namespace
        self.code_ops.append((bp.STORE_NAME, node.typename))

    def visit_Template(self, node):
        """ The compiler visitor for a Template node.

        """
        self.set_lineno(node.lineno)

        # Evaluate the specializations
        load_none = (bp.LOAD_CONST, None)
        for param in node.parameters.positional:
            spec = param.specialization
            if spec is not None:
                code = compile(spec.ast, self.filename, 'eval')
                bp_code = bp.Code.from_code(code).code
                self.code_ops.extend(bp_code[:-1])  # skip the return value op
                with self.try_squash_raise():
                    self.code_ops.append(               # value
                        (bp.DUP_TOP, None)              # value -> value
                    )
                    self.load_helper('validate_spec')
                    self.code_ops.extend([              # value -> value -> helper
                        (bp.ROT_TWO, None),             # value -> helper -> value
                        (bp.CALL_FUNCTION, 0x0001),     # value -> retval
                        (bp.POP_TOP, None),             # value
                    ])
            else:
                self.code_ops.append(load_none)

        n_positional = len(node.parameters.positional)
        n_keywords = len(node.parameters.keywords)
        self.code_ops.extend([load_none] * n_keywords)

        # Store the specializations in a tuple
        n_specs = n_positional + n_keywords
        if n_specs > 0:
            self.code_ops.append(               # p_1 -> p_2 -> p_n
                (bp.BUILD_TUPLE, n_specs)       # paramspec
            )
        else:
            self.code_ops.append(               # p_1 -> p_2 -> p_n
                (bp.LOAD_CONST, ())             # paramspec
            )

        # Evaluate the template defaults
        for param in node.parameters.keywords:
            code = compile(param.default.ast, self.filename, 'eval')
            bp_code = bp.Code.from_code(code).code
            self.code_ops.extend(bp_code[:-1])  # skip the return value op

        # Generate the template code and function
        code = TemplateCompiler.compile(node, self.filename)
        self.code_ops.extend([                  # paramspec -> defaults
            (bp.LOAD_CONST, code),              # paramspec -> defaults -> code
            (bp.MAKE_FUNCTION, n_keywords),     # paramspec -> function
        ])

        # Load or create the template object
        t_map = self.template_map
        if node.name in t_map:
            self.code_ops.append(                   # paramspec -> function
                (bp.LOAD_GLOBAL, t_map[node.name])  # paramspec -> function -> template
            )
        else:
            t_name = self.template_vars.next()
            t_map[node.name] = t_name
            self.load_helper('make_template')
            self.code_ops.extend([              # paramspec -> function -> helper
                (bp.LOAD_GLOBAL, '__name__'),   # paramspec -> function -> helper -> module
                (bp.LOAD_CONST,  node.name),    # paramspec -> function -> helper -> module -> name
                (bp.CALL_FUNCTION, 0x0002),     # paramspec -> function -> template
                (bp.DUP_TOP, None),             # paramspec -> function -> template -> template
                (bp.DUP_TOP, None),             # paramspec -> function -> template -> template -> template
                (bp.STORE_GLOBAL, node.name),   # paramspec -> function -> template -> template
                (bp.STORE_GLOBAL, t_name),      # paramspec -> function -> template
            ])

        # Add the specialization to the template
        attr = 'add_specialization'
        #with self.try_squash_raise():
        self.code_ops.extend([              # paramspec -> function -> template
            (bp.LOAD_ATTR, attr),           # paramspec -> function -> handler
            (bp.ROT_THREE, None),           # handler -> paramspec -> function
            (bp.CALL_FUNCTION, 0x0002),     # retval
            (bp.POP_TOP, None),             # <empty>
        ])
