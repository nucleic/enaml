#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .compiler_base import CompilerBase


class EnamlDefCompiler(CompilerBase):
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
        compiler = cls()
        cg = compiler.code_generator
        cg.filename = filename
        compiler.visit(node)
        code = cg.to_code(
            newlocals=True, name=node.typename, lineno=node.lineno,
            docstring=node.docstring or None
        )
        return code

    #--------------------------------------------------------------------------
    # Visitors
    #--------------------------------------------------------------------------
    def visit_EnamlDef(self, node):
        """ The compiler visitor for an EnamlDef node.

        """
        # Determine whether declaration instances need local storage.
        self.has_locals = self.has_identifiers(node)

        # Claim the variables needed for the class and construct node
        class_var = self.var_pool.new()
        node_var = self.var_pool.new()

        # Prepare the block for execution
        self.set_lineno(node.lineno)
        self.fetch_globals()
        self.fetch_helpers()
        self.make_scope_key()

        # Load the type name and the base class
        self.load_helper('make_enamldef')           # helper
        self.code_ops.extend([
            (bp.LOAD_CONST, node.typename),         # helper -> name
            (bp.LOAD_GLOBAL, node.base),            # helper -> name -> base
        ])

        # Validate the type of the base class
        self.validate_declarative()

        # Build the enamldef class
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
