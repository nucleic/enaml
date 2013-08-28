#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from . import byteplay as bp


class CodeWriter(object):
    """ A simple class which writes code ops to a list.

    This class is used by the enaml compiler to generate the code
    for an Enaml ast.

    """
    def __init__(self):
        """ Initialize a CodeWriter.

        """
        self.code_ops = []
        self.local_names = set()

    def set_lineno(self, lineno):
        """ Write the instruction to set the line number.

        """
        op = (bp.SetLineno, lineno)
        self.code_ops.append(op)

    def load_name(self, name):
        """ Write instruction to load the given name.

        If the given name lives in the 'local_names' set, a LOAD_FAST
        instruction is returned. Otherwise, a LOAD_GLOBAL instruction
        is returned.

        """
        if name in self.f_locals:
            instruction = bp.LOAD_FAST
        else:
            instruction = bp.LOAD_GLOBAL
        op = (instruction, name)
        self.code_ops.append(op)

    def fetch_globals(self):
        """ Write the instructions to fetch and store the globals.

        """
        ops = [
            (bp.LOAD_GLOBAL, 'globals'),        # func
            (bp.CALL_FUNCTION, 0x0000),         # globals
            (bp.STORE_FAST, '_[f_globals]'),    # <empty>
        ]
        self.code_ops.extend(ops)

    def load_globals(self):
        """ Write the instruction to load the globals.

        """
        op = (bp.LOAD_FAST, '_[f_globals]')
        self.code_ops.append(op)

    def fetch_scope_key(self):
        """ Write the instructions to fetch and store a scope key.

        """
        ops = [                                 # <empty>
            (bp.LOAD_GLOBAL, 'object'),         # object
            (bp.CALL_FUNCTION, 0x0000),         # key
            (bp.STORE_FAST, '_[scope_key]'),    # <empty>
        ]
        self.code_ops.extend(ops)

    def load_scope_key(self):
        """ Write the instruction to load the scope key.

        """
        op = (bp.LOAD_FAST, '_[scope_key]')
        self.code_ops.append(op)

    def load_fast(self, name):
        """ Write the instructions to load a fast local.

        """
        op = (bp.LOAD_FAST, name)
        self.code_ops.append(op)

    def store_fast(self, name):
        """ Write the instructions to store fast the TOS.

        """
        op = (bp.STORE_FAST, name)
        self.code_ops.append(op)

    def store_dup(self, name):
        """ Store a duplicate of the TOS.

        """
        ops = [
            (bp.DUP_TOP, None),
            (bp.STORE_FAST, name),
        ]
        self.code_ops.extend(ops)

    def dup_top(self):
        """ Write the instructions to duplicates the TOS.

        """
        op = (bp.DUP_TOP, None)
        self.code_ops.append(op)

    def validate_d_type(self):
        """ Write the instructions to validate a Declarative type TOS.

        """
        ops = [                                     # class
            (bp.DUP_TOP, None),                     # class -> class
            (bp.LOAD_GLOBAL, '__validate_d_type'),  # class -> class -> helper
            (bp.ROT_TWO, None),                     # class -> helper -> class
            (bp.CALL_FUNCTION, 0x0001),             # class -> retval
            (bp.POP_TOP, None),                     # class
        ]
        self.code_ops.extend(ops)

    def make_subclass(self, name):
        """ Write the instructions to subclass the TOS.

        """
        ops = [                             # class
            (bp.LOAD_CONST, name),          # class -> name
            (bp.ROT_TWO, None),             # name -> class
            (bp.BUILD_TUPLE, 1),            # name -> bases
            (bp.BUILD_MAP, 0),              # name -> bases -> dict
            (bp.LOAD_GLOBAL, '__name__'),   # name -> bases -> dict -> __name__
            (bp.LOAD_CONST, '__module__'),  # name -> bases -> dict -> __name__ -> '__module__'
            (bp.STORE_MAP, None),           # name -> bases -> dict
            (bp.BUILD_CLASS, None),         # class
        ]
        self.code_ops.extend(ops)

    def make_construct_node(self, identifier):
        """ Create a construct node from the TOS.

        """
        ops = [                                     # class
            (bp.LOAD_GLOBAL, '__construct_node'),   # class -> helper
            (bp.ROT_TWO, None),                     # helper -> class
            (bp.LOAD_CONST, identifier),            # helper -> class -> identifier
            (bp.LOAD_FAST, '_[scope_key]'),         # helper -> class -> identifier -> key
            (bp.LOAD_FAST, '_[has_block_idents]'),  # helper -> class -> identifier -> key -> bool
            (bp.CALL_FUNCTION, 0x0004),             # node
        ]
        self.code_ops.extend(ops)

    def add_engine(self, class_var):
        """ Create and add an engine to the class at the given var.

        """
        ops =   [                               # <empty>
            (bp.LOAD_GLOBAL, '__make_engine'),  # helper
            (bp.LOAD_FAST, class_var),          # helper -> class
            (bp.CALL_FUNCTION, 0x0001),         # engine
            (bp.LOAD_FAST, class_var),          # engine -> class
            (bp.STORE_ATTR, '__engine__'),      # <empty>
        ]
        self.code_ops.extend(ops)

    def append_node(self, parent_var, node_var):
        """ Append a node to it's parent node.

        """
        ops = [                                     # <empty>
            (bp.LOAD_FAST, parent_var),             # parent
            (bp.LOAD_ATTR, 'children'),             # children
            (bp.LOAD_ATTR, 'append'),               # append
            (bp.LOAD_FAST, node_var),               # append -> node
            (bp.CALL_FUNCTION, 0x0001),             # retval
            (bp.POP_TOP, None),                     # <empty>
        ]
        self.code_ops.extend(ops)
