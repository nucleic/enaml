#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import sys
import types

from . import byteplay as bp
from . import enaml_ast


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
    'from enaml.core.compiler_helpers import '\
        '__add_storage, __construct_node, __make_enamldef, '\
        '__run_operator, __validate_type',
]


# Cleanup code that will be included in every compiled enaml module
CLEANUP = [
    'del __add_storage, __construct_node, __make_enamldef, '\
    '__run_operator, __validate_type'
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


class VarPool(object):
    """ A class for generating private variable names.

    """
    def __init__(self):
        """ Initialize a VarPool.

        """
        self._pool = set()

    def new(self):
        """ Get a new private variable name.

        Returns
        -------
        result : str
            An unused variable name.

        """
        var = '_[var_%d]' % len(self._pool)
        self._pool.add(var)
        return var

    def release(self, name):
        """ Return a variable name to the pool.

        Parameters
        ----------
        name : str
            The variable name which is free to be reused.

        """
        self._pool.discard(name)


class NodeVisitor(object):
    """ A base class for defining node visitor classes.

    This class is used as base class for the various Enaml compilers.

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

    def default_visit(self, node):
        """ The default visitor method.

        This method raises since there should be no unhandled nodes.

        """
        raise ValueError('Unhandled Node %s.' % node)


#------------------------------------------------------------------------------
# EnamlDef Compiler
#------------------------------------------------------------------------------
class EnamlDefCompiler(NodeVisitor):
    """ A compiler class for compiling 'enamldef' blocks.

    This compiler is invoked by the main EnamlCompiler class when it
    reaches an EnamlDef ast node. The main entry point is the 'compile'
    classmethod.

    """
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
        compiler = cls(filename)
        compiler.visit(node)
        code = bp.Code(
            compiler.code_ops, [], [], False, False, True, node.typename,
            filename, node.lineno, node.docstring or None
        )
        return code.to_code()

    def __init__(self, filename):
        """ Initialize an EnamlDefCompiler.

        Parameters
        ----------
        filename : str
            The full name of the file of the node on which the compiler
            is operating.

        """
        self.filename = filename
        self.var_pool = VarPool()
        self.class_stack = []
        self.node_stack = []
        self.name_stack = []
        self.code_stack = []
        self.code_ops = []

    #--------------------------------------------------------------------------
    # Utility Methods
    #--------------------------------------------------------------------------
    @classmethod
    def needs_subclass(cls, child_def):
        """ Get whether or not a ChildDef node needs to be subclassed.

        A ChildDef must be subclassed if it requires storage or has
        bound expressions.

        Parameters
        ----------
        child_def : ChildDef
            The child node of interest

        Returns
        -------
        result : bool
            True if the class for the node must be subclassed, False
            otherwise.

        """
        types = (enaml_ast.StorageDef, enaml_ast.Binding)
        return any(isinstance(item, types) for item in child_def.body)

    @classmethod
    def try_squash_raise(cls, ops):
        """ Wrap a sequence of ops in a try-except clause.

        The exception handling code will squash the traceback for any
        exception raised by the operations, and re-raise the exception
        so that the traceback will appear to have originated from the
        current line number.

        Parameters
        ----------
        ops : list
            A list of code ops to wrap in exception handling code.

        Returns
        -------
        result : list
            A new list of code ops.

        """
        exc_label = bp.Label()
        final_label = bp.Label()
        new_ops = [
            (bp.SETUP_EXCEPT, exc_label)        # TOS
        ]
        new_ops.extend(ops)
        new_ops.extend([                        # TOS
            (bp.POP_BLOCK, None),               # TOS
            (bp.JUMP_FORWARD, final_label),     # TOS
            (exc_label, None),                  # TOS -> tb -> val -> exc
            (bp.ROT_THREE, None),               # TOS -> exc -> tb -> val
            (bp.ROT_TWO, None),                 # TOS -> exc -> val -> tb
            (bp.POP_TOP, None),                 # TOS -> exc -> val
            (bp.RAISE_VARARGS, 0),              # TOS
            (bp.JUMP_FORWARD, final_label),     # TOS
            (bp.END_FINALLY, None),             # TOS
            (final_label, None),                # TOS
        ])
        return new_ops

    @classmethod
    def validate_TOS(cls):
        """ Generate code ops to validate the type of the TOS.

        The ops will assert that the TOS is a subclass of Declarative.

        Returns
        -------
        result : list
            A list of code ops which validates the type of the TOS.

        """
        ops = [                                     # class
            (bp.DUP_TOP, None),                     # class -> class
            (bp.LOAD_GLOBAL, '__validate_type'),    # class -> class -> helper
            (bp.ROT_TWO, None),                     # class -> helper -> class
            (bp.CALL_FUNCTION, 0x0001),             # class -> retval
            (bp.POP_TOP, None),                     # class
        ]
        return cls.try_squash_raise(ops)

    #--------------------------------------------------------------------------
    # Visitors
    #--------------------------------------------------------------------------
    def visit_EnamlDef(self, node):
        """ The compiler visitor for an EnamlDef node.

        """
        # Claim the variables needed for the class and construct node
        class_var = self.var_pool.new()
        node_var = self.var_pool.new()

        # Store the globals as a local for fast access
        self.code_ops.extend([
            (bp.SetLineno, node.lineno),        # <empty>
            (bp.LOAD_GLOBAL, 'globals'),        # func
            (bp.CALL_FUNCTION, 0x0000),         # globals
            (bp.STORE_FAST, '_[f_globals]'),    # <empty>
        ])

        # Create the local scope storage key
        self.code_ops.extend([                  # <empty>
            (bp.LOAD_GLOBAL, 'object'),         # object
            (bp.CALL_FUNCTION, 0x0000),         # key
            (bp.STORE_FAST, '_[scope_key]'),    # <empty>
        ])

        # Build the enamldef class and construct node
        self.code_ops.extend([                      # <empty>
            (bp.LOAD_GLOBAL, '__make_enamldef'),    # helper
            (bp.LOAD_CONST, node.typename),         # helper -> name
            (bp.LOAD_GLOBAL, node.base),            # helper -> name -> base
        ])
        self.code_ops.extend(self.validate_TOS())
        self.code_ops.extend([
            (bp.BUILD_TUPLE, 1),                    # helper -> name -> bases
            (bp.BUILD_MAP, 0),                      # helper -> name -> bases -> dict
            (bp.LOAD_GLOBAL, '__name__'),           # helper -> name -> bases -> dict -> __name__
            (bp.LOAD_CONST, '__module__'),          # helper -> name -> bases -> dict -> __name__ -> '__module__'
            (bp.STORE_MAP, None),                   # helper -> name -> bases -> dict
        ])
        if node.docstring:
            self.code_ops.extend([
                (bp.LOAD_CONST, node.docstring),    # helper -> name -> bases -> dict -> docstring
                (bp.LOAD_CONST, '__doc__'),         # helper -> name -> bases -> dict -> docstring -> '__doc__'
                (bp.STORE_MAP, None),               # helper -> name -> bases -> dict
            ])
        self.code_ops.extend([
            (bp.CALL_FUNCTION, 0x0003),             # class
            (bp.DUP_TOP, None),                     # class -> class
            (bp.STORE_FAST, class_var),             # class
            (bp.LOAD_GLOBAL, '__construct_node'),   # class -> helper
            (bp.ROT_TWO, None),                     # helper -> class
            (bp.LOAD_CONST, node.identifier),       # helper -> class -> identifier
            (bp.LOAD_FAST, '_[scope_key]'),         # helper -> class -> identifier -> key
            (bp.CALL_FUNCTION, 0x0003),             # node
            (bp.STORE_FAST, node_var),              # <empty>
        ])

        # Popuplate the body of the class
        self.class_stack.append(class_var)
        self.node_stack.append(node_var)
        for item in node.body:
            self.visit(item)
        self.class_stack.pop()
        self.node_stack.pop()

        # Store the node on the enamldef and return the class
        self.code_ops.extend([              # <empty>
            (bp.LOAD_FAST, class_var),      # class
            (bp.DUP_TOP, None),             # class -> class
            (bp.LOAD_FAST, node_var),       # class -> class -> node
            (bp.ROT_TWO, None),             # class -> node -> class
            (bp.STORE_ATTR, '__node__'),    # class
            (bp.RETURN_VALUE, None),        # <return>
        ])

        # Release the held variables
        self.var_pool.release(class_var)
        self.var_pool.release(node_var)

    def visit_ChildDef(self, node):
        """ The compiler visitor for a ChildDef node.

        """
        # Claim the variables needed for the class and construct node
        class_var = self.var_pool.new()
        node_var = self.var_pool.new()

        # Load and validate the child class
        self.code_ops.extend([                  # <empty>
            (bp.SetLineno, node.lineno),        # <empty>
            (bp.LOAD_GLOBAL, node.typename),    # class
        ])
        self.code_ops.extend(self.validate_TOS())

        # Subclass the child class if needed
        types = (enaml_ast.StorageDef, enaml_ast.Binding)
        needs_subclass = any(isinstance(item, types) for item in node.body)
        if needs_subclass:
            self.code_ops.extend([              # class
                (bp.LOAD_CONST, node.typename), # class -> name
                (bp.ROT_TWO, None),             # name -> class
                (bp.BUILD_TUPLE, 1),            # name -> bases
                (bp.BUILD_MAP, 0),              # name -> bases -> dict
                (bp.LOAD_GLOBAL, '__name__'),   # name -> bases -> dict -> __name__
                (bp.LOAD_CONST, '__module__'),  # name -> bases -> dict -> __name__ -> '__module__'
                (bp.STORE_MAP, None),           # name -> bases -> dict
                (bp.BUILD_CLASS, None),         # class
            ])

        # Store the class as a local
        self.code_ops.extend([                  # class
            (bp.DUP_TOP, None),                 # class -> class
            (bp.STORE_FAST, class_var),         # class
        ])

        # Build and store the construct node
        self.code_ops.extend([                      # class
            (bp.LOAD_GLOBAL, '__construct_node'),   # class -> helper
            (bp.ROT_TWO, None),                     # helper -> class
            (bp.LOAD_CONST, node.identifier),       # helper -> class -> identifier
            (bp.LOAD_FAST, '_[scope_key]'),         # helper -> class -> identifier -> key
            (bp.CALL_FUNCTION, 0x0003),             # node
            (bp.STORE_FAST, node_var),              # <empty>
        ])

        # Populate the body of the class
        self.class_stack.append(class_var)
        self.node_stack.append(node_var)
        for item in node.body:
            self.visit(item)
        self.class_stack.pop()
        self.node_stack.pop()

        # Add this node to the parent node
        self.code_ops.extend([                      # <empty>
            (bp.LOAD_FAST, self.node_stack[-1]),    # parent
            (bp.LOAD_ATTR, 'children'),             # children
            (bp.LOAD_ATTR, 'append'),               # append
            (bp.LOAD_FAST, node_var),               # append -> node
            (bp.CALL_FUNCTION, 0x0001),             # retval
            (bp.POP_TOP, None),                     # <empty>
        ])

        # Release the held variables
        self.var_pool.release(class_var)
        self.var_pool.release(node_var)

    def visit_StorageDef(self, node):
        """ The compiler visitor for a StorageDef node.

        """
        self.code_ops.extend([                      # <empty>
            (bp.SetLineno, node.lineno),            # <empty>
            (bp.LOAD_GLOBAL, '__add_storage'),      # helper
            (bp.LOAD_FAST, self.class_stack[-1]),   # helper -> class
            (bp.LOAD_CONST, node.name),             # helper -> class -> name
        ])
        if node.typename:
            self.code_ops.append(
                (bp.LOAD_GLOBAL, node.typename)     # helper -> class -> name -> type
            )
        else:
            self.code_ops.append(
                (bp.LOAD_CONST, None)               # helper -> class -> name -> None
            )
        self.code_ops.extend([
            (bp.LOAD_CONST, node.kind),             # helper -> class -> name -> type -> kind
            (bp.CALL_FUNCTION, 0x0004),             # retval
            (bp.POP_TOP, None),                     # <empty>
        ])
        if node.expr is not None:
            self.name_stack.append(node.name)
            self.visit(node.expr)
            self.name_stack.pop()

    def visit_Binding(self, node):
        """ The compiler visitor for a Binding node.

        """
        self.name_stack.append(node.name)
        self.visit(node.expr)
        self.name_stack.pop()

    def visit_OperatorExpr(self, node):
        """ The compiler visitor for an OperatorExpr node.

        """
        self.visit(node.value)
        code = self.code_stack.pop()
        self.code_ops.append((bp.SetLineno, node.lineno))
        ops = [                                     # <empty>
            (bp.LOAD_GLOBAL, '__run_operator'),     # helper
            (bp.LOAD_FAST, self.node_stack[-1]),    # helper -> node
            (bp.LOAD_CONST, self.name_stack[-1]),   # helper -> node -> name
            (bp.LOAD_CONST, node.operator),         # helper -> node -> name -> op
            (bp.LOAD_CONST, code),                  # helper -> node -> name -> op -> code
            (bp.LOAD_FAST, '_[f_globals]'),         # helper -> node -> name -> op -> code -> globals
            (bp.CALL_FUNCTION, 0x0005),             # retval
            (bp.POP_TOP, None),                     # <empty>
        ]
        ops = self.try_squash_raise(ops)
        self.code_ops.extend(ops)

    def visit_PythonExpression(self, node):
        """ The compiler visitor for a PythonExpression node.

        """
        code = compile(node.ast, self.filename, mode='eval')
        code = update_firstlineno(code, node.lineno)
        self.code_stack.append(code)

    def visit_PythonModule(self, node):
        """ The compiler visitor for a PythonModule node.

        """
        code = compile(node.ast, self.filename, mode='exec')
        self.code_stack.append(code)


#------------------------------------------------------------------------------
# Enaml Compiler
#------------------------------------------------------------------------------
class EnamlCompiler(NodeVisitor):
    """ A visitor that will compile an enaml module ast node.

    The entry point is the `compile` classmethod which will compile
    the ast into an appropriate python code object for a module.

    """
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
        compiler = cls(filename)
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
        """ The compiler visitor for a Module node.

        """
        for item in node.body:
            self.visit(item)

    def visit_PythonModule(self, node):
        """ The compiler visitor for a PythonModule node.

        """
        code = compile(node.ast, self.filename, mode='exec')
        bp_code = bp.Code.from_code(code)
        # Skip the SetLineo and ReturnValue codes
        self.code_ops.extend(bp_code.code[1:-2])

    def visit_EnamlDef(self, node):
        """ The compiler visitor for an EnamlDef node.

        """
        # Load the decorators
        for decorator in node.decorators:
            code = compile(decorator.ast, self.filename, mode='eval')
            update_firstlineno(code, decorator.lineno)
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
