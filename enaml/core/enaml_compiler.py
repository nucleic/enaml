#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from contextlib import contextmanager
import sys

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


#------------------------------------------------------------------------------
# Compiler Helpers
#------------------------------------------------------------------------------
# Code that will be executed at the top of every enaml module
STARTUP = ['from enaml.core.compiler_helpers import __compiler_helpers']


# Cleanup code that will be included in every compiled enaml module
CLEANUP = []


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
# Block Compiler
#------------------------------------------------------------------------------
class BlockCompiler(NodeVisitor):
    """ A base class for creating block compilers.

    This class provides the functionality which is common between the
    compilers for the 'enamldef' and 'template' blocks.

    """
    def __init__(self, filename):
        """ Initialize a BlockCompiler.

        Parameters
        ----------
        filename : str
            The full name of the file which is being compiled.

        """
        self.filename = filename
        self.var_pool = VarPool()
        self.local_names = set()
        self.has_locals = False
        self.class_stack = []
        self.node_stack = []
        self.bind_stack = []
        self.code_stack = []
        self.code_ops = []

    #--------------------------------------------------------------------------
    # Utilities
    #--------------------------------------------------------------------------
    def set_lineno(self, lineno):
        """ Set the current line number in the code.

        """
        self.code_ops.append((bp.SetLineno, lineno))

    def load_name(self, name):
        """ Load a name onto the TOS.

        If the name is contained in the 'local_names' set, it is loaded
        from the fast locals, otherwise it is loaded from the globals.

        Parameters
        ----------
        name : str
            The name of the object to load onto the TOS.

        """
        if name in self.local_names:
            inst = bp.LOAD_FAST
        else:
            inst = bp.LOAD_GLOBAL
        self.code_ops.append((inst, name))

    def fetch_globals(self):
        """ Fetch the globals and store into fast locals.

        """
        self.code_ops.extend([
            (bp.LOAD_GLOBAL, 'globals'),        # func
            (bp.CALL_FUNCTION, 0x0000),         # globals
            (bp.STORE_FAST, '_[f_globals]'),    # <empty>
        ])

    def load_globals(self):
        """ Load the globals onto the TOS.

        """
        self.code_ops.append((bp.LOAD_FAST, '_[f_globals]'))

    def fetch_helpers(self):
        """ Fetch the compiler helpers and store into fast locals.

        """
        self.code_ops.extend([
            (bp.LOAD_GLOBAL, '__compiler_helpers'), # helpers
            (bp.STORE_FAST, '_[helpers]'),          # <empty>
        ])

    def load_helper(self, name):
        """ Load a compiler helper onto the TOS.

        Parameters
        ----------
        name : str
            The name of the helper function to load onto the TOS.

        """
        self.code_ops.extend([
            (bp.LOAD_FAST, '_[helpers]'),   # helpers
            (bp.LOAD_CONST, name),          # helpers -> name
            (bp.BINARY_SUBSCR, None),       # helper
        ])

    def make_scope_key(self):
        """ Create a scope key and store into fast locals.

        """
        self.code_ops.extend([
            (bp.LOAD_GLOBAL, 'object'),         # object
            (bp.CALL_FUNCTION, 0x0000),         # key
            (bp.STORE_FAST, '_[scope_key]'),    # <empty>
        ])

    def load_scope_key(self):
        """ Load the scope key onto the TOS.

        """
        self.code_ops.append((bp.LOAD_FAST, '_[scope_key]'))

    def validate_d_type(self):
        """ Write instructions which assert a Declarative type at TOS.

        """
        self.code_ops.append(                   # class
            (bp.DUP_TOP, None)                  # class -> class
        )
        self.load_helper('validate_d_type')     # class -> class -> helper
        self.code_ops.extend([
            (bp.ROT_TWO, None),                 # class -> helper -> class
            (bp.CALL_FUNCTION, 0x0001),         # class -> retval
            (bp.POP_TOP, None),                 # class
        ])

    @contextmanager
    def try_squash_raise(self):
        """ A context manager for squashing tracebacks.

        The code written during this context will be wrapped so that
        any exception raised will appear to have been generated from
        this code, rather than any function called by the code.

        """
        exc_label = bp.Label()
        final_label = bp.Label()
        self.code_ops.append(
            (bp.SETUP_EXCEPT, exc_label)
        )
        yield
        self.code_ops.extend([                  # TOS
            (bp.POP_BLOCK, None),               # TOS
            (bp.JUMP_FORWARD, final_label),     # TOS
            (exc_label, None),                  # TOS -> tb -> val -> exc
            (bp.ROT_THREE, None),               # TOS -> exc -> tb -> val
            (bp.ROT_TWO, None),                 # TOS -> exc -> val -> tb
            (bp.POP_TOP, None),                 # TOS -> exc -> val
            (bp.RAISE_VARARGS, 2),              # TOS
            (bp.JUMP_FORWARD, final_label),     # TOS
            (bp.END_FINALLY, None),             # TOS
            (final_label, None),                # TOS
        ])

    def needs_subclass(cls, node):
        """ Get whether or not a ChildDef node needs subclassing.

        A child def class must be subclassed if it uses storage or
        has attribute bindings.

        Parameters
        ----------
        node : ChildDef
            The child def node of interest.

        Returns
        -------
        result : bool
            True if the class must be subclassed, False otherwise.

        """
        types = (enaml_ast.StorageExpr, enaml_ast.Binding)
        return any(isinstance(item, types) for item in node.body)

    def needs_engine(cls, node):
        """ Get whether or not a node needs an expression engine.

        A node requires an engine if it has attribute bindings.

        Parameters
        ----------
        node : EnamlDef or ChildDef
            The node of interest.

        Returns
        -------
        result : bool
            True if the class requires an engine, False otherwise.

        """
        for item in node.body:
            if isinstance(item, enaml_ast.Binding):
                return True
            if isinstance(item, enaml_ast.StorageExpr):
                if item.expr is not None:
                    return True
        return False

    def has_identifiers(cls, node):
        """ Get whether or not a node has block identifiers.

        Parameters
        ----------
        node : EnamlDef, ChildDef, Template, or TemplateInst
            The node of interest.

        Returns
        -------
        result : bool
            True if the node or any of it's decendents have identifiers,
            False otherwise.

        """
        stack = [node]
        while stack:
            node = stack.pop()
            if isinstance(node, (enaml_ast.EnamlDef, enaml_ast.ChildDef)):
                if node.identifier:
                    return True
                stack.extend(node.body)
            elif isinstance(node, enaml_ast.TemplateInst):
                if node.identifiers:
                    return True
                stack.extend(node.body)
            elif isinstance(node, enaml_ast.Template):
                stack.extend(node.body)
        return False

    #--------------------------------------------------------------------------
    # Visitors
    #--------------------------------------------------------------------------
    def visit_ChildDef(self, node):
        """ The compiler visitor for a ChildDef node.

        """
        # Claim the variables needed for the class and construct node
        class_var = self.var_pool.new()
        node_var = self.var_pool.new()

        # Load and validate the child class
        self.set_lineno(node.lineno)
        self.load_name(node.typename)
        self.validate_d_type()

        # Subclass the child class if needed
        if self.needs_subclass(node):
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
        self.load_helper('construct_node')
        self.code_ops.extend([                      # class -> helper
            (bp.ROT_TWO, None),                     # helper -> class
            (bp.LOAD_CONST, node.identifier),       # helper -> class -> identifier
        ])
        self.load_scope_key()
        self.code_ops.extend([                      # helper -> class -> identifier -> key
            (bp.LOAD_CONST, self.has_locals),       # helper -> class -> identifier -> key -> bool
            (bp.CALL_FUNCTION, 0x0004),             # node
            (bp.STORE_FAST, node_var),              # <empty>
        ])

        # Build an engine for the new class if needed.
        if self.needs_engine(node):
            self.load_helper('make_engine')
            self.code_ops.extend([                  # helper
                (bp.LOAD_FAST, class_var),          # helper -> class
                (bp.CALL_FUNCTION, 0x0001),         # engine
                (bp.LOAD_FAST, class_var),          # engine -> class
                (bp.STORE_ATTR, '__engine__'),      # <empty>
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

    def visit_StorageExpr(self, node):
        """ The compiler visitor for a StorageExpr node.

        """
        self.set_lineno(node.lineno)
        with self.try_squash_raise():
            self.load_helper('add_storage')
            self.code_ops.extend([                      # helper
                (bp.LOAD_FAST, self.class_stack[-1]),   # helper -> class
                (bp.LOAD_CONST, node.name),             # helper -> class -> name
            ])
            if node.typename:
                self.load_name(node.typename)           # helper -> class -> name -> type
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
            self.bind_stack.append(node.name)
            self.visit(node.expr)
            self.bind_stack.pop()

    def visit_Binding(self, node):
        """ The compiler visitor for a Binding node.

        """
        self.bind_stack.append(node.name)
        self.visit(node.expr)
        self.bind_stack.pop()

    def visit_OperatorExpr(self, node):
        """ The compiler visitor for an OperatorExpr node.

        """
        self.visit(node.value)
        code = self.code_stack.pop()
        self.set_lineno(node.lineno)
        with self.try_squash_raise():
            self.load_helper('run_operator')
            self.code_ops.extend([                      # helper
                (bp.LOAD_FAST, self.node_stack[-1]),    # helper -> node
                (bp.LOAD_CONST, self.bind_stack[-1]),   # helper -> node -> name
                (bp.LOAD_CONST, node.operator),         # helper -> node -> name -> op
                (bp.LOAD_CONST, code),                  # helper -> node -> name -> op -> code
            ])
            self.load_globals()
            self.code_ops.extend([                      # helper -> node -> name -> op -> code -> globals
                (bp.CALL_FUNCTION, 0x0005),             # retval
                (bp.POP_TOP, None),                     # <empty>
            ])

    def visit_PythonExpression(self, node):
        """ The compiler visitor for a PythonExpression node.

        """
        code = compile(node.ast, self.filename, mode='eval')
        self.code_stack.append(code)

    def visit_PythonModule(self, node):
        """ The compiler visitor for a PythonModule node.

        """
        code = compile(node.ast, self.filename, mode='exec')
        self.code_stack.append(code)


#------------------------------------------------------------------------------
# EnamlDef Compiler
#------------------------------------------------------------------------------
class EnamlDefCompiler(BlockCompiler):
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

    #--------------------------------------------------------------------------
    # Visitors
    #--------------------------------------------------------------------------
    def visit_EnamlDef(self, node):
        """ The compiler visitor for an EnamlDef node.

        """
        # Determine whether instances of the block need local storage.
        self.has_locals = self.has_identifiers(node)

        # Claim the variables needed for the class and construct node
        class_var = self.var_pool.new()
        node_var = self.var_pool.new()

        # Prepare the block for execution
        self.set_lineno(node.lineno)
        self.fetch_globals()
        self.fetch_helpers()
        self.make_scope_key()

        # Build the enamldef class
        self.load_helper('make_enamldef')           # helper
        self.code_ops.append(
            (bp.LOAD_CONST, node.typename)          # helper -> name
        )
        self.load_name(node.base)                   # helper -> name -> base
        self.validate_d_type()
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
        self.code_ops.append(
            (bp.CALL_FUNCTION, 0x0003),             # class
        )

        # Store the class as a local
        self.code_ops.extend([                      # class
            (bp.DUP_TOP, None),                     # class -> class
            (bp.STORE_FAST, class_var),             # class
        ])

        # Build the construct node
        self.load_helper('construct_node')
        self.code_ops.extend([                      # class -> helper
            (bp.ROT_TWO, None),                     # helper -> class
            (bp.LOAD_CONST, node.identifier),       # helper -> class -> identifier
        ])
        self.load_scope_key()
        self.code_ops.extend([                      # helper -> class -> identifier -> key
            (bp.LOAD_CONST, self.has_locals),       # helper -> class -> identifier -> key -> bool
            (bp.CALL_FUNCTION, 0x0004),             # node
            (bp.STORE_FAST, node_var),              # <empty>
        ])

        # Build an engine for the new class if needed.
        if self.needs_engine(node):
            self.load_helper('make_engine')
            self.code_ops.extend([                  # helper
                (bp.LOAD_FAST, class_var),          # helper -> class
                (bp.CALL_FUNCTION, 0x0001),         # engine
                (bp.LOAD_FAST, class_var),          # engine -> class
                (bp.STORE_ATTR, '__engine__'),      # <empty>
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


#------------------------------------------------------------------------------
# Template Compiler
#------------------------------------------------------------------------------
class TemplateCompiler(BlockCompiler):
    """ A compiler class for compiling 'template' blocks.

    This compiler is invoked by the main EnamlCompiler class when it
    reaches a Template ast node. The main entry point is the 'compile'
    classmethod.

    """
    @classmethod
    def compile(cls, node, filename):
        """ Compile a Template node into a code object.

        Parameters
        ----------
        node : Template
            The enaml ast node representing the template block.

        filename : str
            The full name of the file which contains the node.

        Returns
        -------
        result : CodeType
            A Python code object which implements the template block.

        """
        compiler = cls(filename)
        compiler.visit(node)
        code = bp.Code(
            compiler.code_ops, [], [], False, False, True,
            node.name, filename, node.lineno, None
        )
        return code.to_code()

    #--------------------------------------------------------------------------
    # Utilities
    #--------------------------------------------------------------------------
    def has_template_locals(self, node):
        """ Get whether or not a Template has local scope variables.

        A template will have local scope variables if it has parameters,
        const expressions, or child identifiers.

        Parameters
        ----------
        node : Template
            The template node of interest.

        Returns
        -------
        result : bool
            True if the node has locals, False otherwise.

        """
        parameters = node.parameters
        if parameters.params or parameters.starparam:
            return True
        # The parser enforces that the StorageExpr is 'static'
        StorageExpr = enaml_ast.StorageExpr
        if any(isinstance(b, StorageExpr) for b in node.body):
            return True
        return self.has_identifiers(node)

    #--------------------------------------------------------------------------
    # Visitors
    #--------------------------------------------------------------------------
    def visit_Template(self, node):
        """ The compiler visitor for a Template node.

        """
        # Determine whether instances of the block need local storage.
        self.has_locals = self.has_template_locals(node)

        # Claim the variable for the template node
        node_var = self.var_pool.new()

        # Prepare the block for execution
        self.set_lineno(node.lineno)
        self.fetch_globals()
        self.fetch_helpers()
        self.make_scope_key()

        # Create and store the template node
        self.load_helper('template_node')
        self.load_scope_key()
        self.code_ops.extend([                  # helper -> scope_key
            (bp.LOAD_CONST, self.has_locals),   # helper -> scope_key -> bool
            (bp.CALL_FUNCTION, 0x0002),         # node
            (bp.STORE_FAST, node_var),          # <empty>
        ])

        # Populate the body of the template
        self.node_stack.append(node_var)
        for item in node.body:
            self.visit(item)
        self.node_stack.pop()

        # Return the template node
        self.code_ops.extend([
            (bp.LOAD_FAST, node_var),
            (bp.RETURN_VALUE, None),
        ])

        # Release the held variables
        self.var_pool.release(node_var)


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
        # Generate the template code
        code = TemplateCompiler.compile(node, self.filename)
        self.code_ops.extend([
            (bp.LOAD_CONST, code),
            (bp.MAKE_FUNCTION, 0),
            (bp.STORE_NAME, node.name)
        ])
