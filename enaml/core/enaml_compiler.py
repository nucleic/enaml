#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys

from ..compat import IS_PY3, USE_WORDCODE
from . import compiler_common as cmn
from .enaml_ast import Module
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
# 16 : Support for templates - 9 September 2013
#     This overhauls the compiler with added support for templates to
#     the language grammar. The various compiler bits have been broken
#     out into their own classes and delegate to a CodeGenerator for
#     actually writing the bytecode operations. A large number of new
#     compiler helpers were needed for this, and they are now held in
#     a module level dictionary since the dict must persist for the
#     lifetime of the module in order to insantiate templates. The dict
#     helps remove namespace pollution.
# 17 : Support for aliases - 19 September 2013
#     The introduction of templates with version 16 introduced a strong
#     need for an alias construct. This version implements suppor for
#     such a thing. It was quite the overhaul and represents almost an
#     entirely new compiler.
# 18 : Allow const exprs to raise unsquashed - 20 September 2013
#     There was a bug in the code generated for evaluating template
#     const expressions, where an error raised by a function called
#     by the expression would have its traceback erroneously squashed.
#     This version fixes that bug.
# 19 : Fix a bug in variadic template args - 20 September 2013
#     The code generated for variadic template functions did not set
#     the varargs flag on the code object. This is now fixed.
# 20 : Fix a bug in template instantiation scoping - 13 January 2014
#     The generated code did not properly handle the scope key for
#     binding expressions on template instantiations.
#     https://github.com/nucleic/enaml/issues/78
# 21 : Add support for declarative functions - 2 May 2014
#     This update add support for the 'func' keyword and '->' style
#     declarative method overrides.
# 22 : Update the syntax of arrow functions - 5 May 2014
#     This updates the arrow functions to use "=>" instead of "->".
# 23 : Support for Python 3 and inlining of comprehensions.
# 24 : Call comprehension functions in the proper scope rather than inlining
# 25 : Support for Python 3.6
# 26 : Wrap functions defined inside operators or declarative function to call
#      them with their scope of definition. This allows to handle properly
#      comprehensions and lambdas. Also ensure that we compile the body of the
#      :: operator as a function to properly handle closure.
COMPILER_VERSION = 26


# Code that will be executed at the top of every enaml module
STARTUP = ['from enaml.core.compiler_helpers import __compiler_helpers']


# Cleanup code that will be included at the end of every enaml module
CLEANUP = []


class EnamlCompiler(cmn.CompilerBase):
    """ A compiler which will compile an Enaml module.

    The entry point is the `compile` classmethod which will compile
    the ast into an appropriate python code object for a module.

    """
    @classmethod
    def compile(cls, node, filename):
        """ The main entry point of the compiler.

        Parameters
        ----------
        node : Module
            The enaml ast Module node that should be compiled.

        filename : str
            The string filename of the module ast being compiled.

        Returns
        -------
        result : CodeType
            The code object for the compiled module.

        """
        assert isinstance(node, Module), 'invalid node'

        # On Python 2 protect against unicode filenames, which are incompatible
        # with code objects created via types.CodeType
        if not IS_PY3 and isinstance(filename, type(u'')):
            filename = filename.encode(sys.getfilesystemencoding())

        # Create the compiler and generate the code.
        compiler = cls(filename=filename)
        return compiler.visit(node)

    def visit_Module(self, node):
        cg = self.code_generator

        # Generate the startup code for the module.
        cg.set_lineno(1)
        for start in STARTUP:
            cg.insert_python_block(start)

        # Create the template map.
        cg.build_map()
        cg.store_global(cmn.TEMPLATE_MAP)

        # Populate the body of the module.
        for item in node.body:
            self.visit(item)

        # Delete the template map.
        cg.delete_global(cmn.TEMPLATE_MAP)

        # Generate the cleanup code for the module.
        for end in CLEANUP:
            cg.insert_python_block(end)

        # Finalize the ops and return the code object.
        cg.load_const(None)
        cg.return_value()
        return cg.to_code()

    def visit_PythonModule(self, node):
        # Inline the bytecode for the Python statement block.
        cg = self.code_generator
        cg.set_lineno(node.lineno)
        cg.insert_python_block(node.ast)

    def visit_EnamlDef(self, node):
        # Invoke the enamldef code and store result in the namespace.
        cg = self.code_generator
        code = EnamlDefCompiler.compile(node, cg.filename)
        cg.load_const(code)
        if IS_PY3:
            cg.load_const(None)  # XXX better qualified name
        cg.make_function()
        cg.call_function()
        cg.store_global(node.typename)

    def visit_Template(self, node):
        cg = self.code_generator
        cg.set_lineno(node.lineno)

        with cg.try_squash_raise():

            # Load and validate the parameter specializations
            for index, param in enumerate(node.parameters.positional):
                spec = param.specialization
                if spec is not None:
                    cmn.load_helper(cg, 'validate_spec', from_globals=True)
                    cg.load_const(index)
                    cmn.safe_eval_ast(
                        cg, spec.ast, node.name, param.lineno, set()
                    )
                    cg.call_function(2)
                else:
                    cg.load_const(None)

            # Store the specializations as a tuple
            cg.build_tuple(len(node.parameters.positional))

            # Evaluate the default parameters
            for param in node.parameters.keywords:
                cmn.safe_eval_ast(
                    cg, param.default.ast, node.name, param.lineno, set()
                )

            # Under Python 3.6+ default positional arguments are passed as a
            # single tuple and MAKE_FUNCTION is passed the flag 0x01 to
            # indicate that there is default positional arguments.
            if USE_WORDCODE:
                cg.build_tuple(len(node.parameters.keywords))

            # Generate the template code and function
            code = TemplateCompiler.compile(node, cg.filename)
            cg.load_const(code)

            # Under Python 3 function have a qualified name
            # XXX improve qualified name
            if IS_PY3:
                cg.load_const(None)
            cg.make_function(0x01 if USE_WORDCODE else
                             len(node.parameters.keywords))

            # Load and call the helper which will build the template
            cmn.load_helper(cg, 'make_template', from_globals=True)
            cg.rot_three()
            cg.load_const(node.name)
            cg.load_global('globals')
            cg.call_function()
            cg.load_global(cmn.TEMPLATE_MAP)
            cg.call_function(5)
            cg.pop_top()
