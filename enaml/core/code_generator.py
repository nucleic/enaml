#------------------------------------------------------------------------------
# Copyright (c) 2013-2020, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from contextlib import contextmanager

import bytecode as bc
from atom.api import Atom, Bool, Int, List, Str

from ..compat import USE_WORDCODE, POS_ONLY_ARGS, PY38


class CodeGenerator(Atom):
    """ A class for generating bytecode operations.

    This class matches enaml needs and does not support freevars or cellvars.

    """
    #: The arguments for the code.
    args = List()

    #: Number of positional only arguments
    posonlyargs = Int()

    #: Number of keyword only arguments
    kwonlyargs = Int()

    #: Whether the code takes variadic args.
    varargs = Bool(False)

    #: Whether the code takes variadic kwargs.
    varkwargs = Bool(False)

    #: Whether the code object should get new locals.
    newlocals = Bool(False)

    #: The name for the code object.
    name = Str()

    #: The full name of the file which is being compiled.
    filename = Str()

    #: The first line number for the code object.
    firstlineno = Int(1)

    #: The docstring for the code object.
    docstring = Str()

    #: The list of generated code operations.
    code_ops = List()

    def to_code(self):
        """ Create a Python code object from the current code ops.

        """
        bc_code = bc.Bytecode(self.code_ops)
        bc_code.argnames = self.args
        # The number of positional or keyword args correspond to all args minus:
        # - the positionals only
        # - the keywords only
        # - the variadic positional
        # - the variadic keyword
        bc_code.argcount = (len(self.args) -
                            self.kwonlyargs -
                            self.posonlyargs -
                            self.varargs -
                            self.varkwargs)
        if POS_ONLY_ARGS:
            bc_code.posonlyargcount = self.posonlyargs
        bc_code.kwonlyargcount = self.kwonlyargs


        for name in ("name", "filename", "firstlineno", "docstring"):
            setattr(bc_code, name, getattr(self, name))

        # Set flags appropriately and update flags based on the instructions
        for setting, flag in zip((self.varargs, self.varkwargs, self.newlocals),
                                 (bc.CompilerFlags.VARARGS,
                                  bc.CompilerFlags.VARKEYWORDS,
                                  bc.CompilerFlags.NEWLOCALS)
                                 ):
            # Set the flag
            if setting:
                bc_code.flags |= flag
            # Unset the flag if it was set
            else:
                bc_code.flags ^= (bc_code.flags & flag)
        bc_code.update_flags()

        return bc_code.to_code()

    def set_lineno(self, lineno):
        """ Set the current line number in the code.

        """
        self.code_ops.append(                           # TOS
            bc.SetLineno(lineno),                       # TOS
        )

    def load_global(self, name):
        """ Load a global variable onto the TOS.

        """
        self.code_ops.append(                           # TOS
            bc.Instr("LOAD_GLOBAL", name),              # TOS -> value
        )

    def load_name(self, name):
        """ Load a named variable onto the TOS.

        """
        self.code_ops.append(                           # TOS
            bc.Instr("LOAD_NAME", name),                # TOS -> value
        )

    def load_fast(self, name):
        """ Load a fast local variable onto the TOS.

        """
        self.code_ops.append(                           # TOS
            bc.Instr("LOAD_FAST", name),                # TOS -> value
        )

    def load_const(self, const):
        """ Load a const value onto the TOS.

        """
        self.code_ops.append(                           # TOS
            bc.Instr("LOAD_CONST", const),              # TOS -> value
        )

    def load_attr(self, name):
        """ Load an attribute from the object on TOS.

        """
        self.code_ops.append(                           # TOS -> obj
            bc.Instr("LOAD_ATTR", name),                # TOS -> value
        )

    def store_global(self, name):
        """ Store the TOS as a global.

        """
        self.code_ops.append(                           # TOS -> value
            bc.Instr("STORE_GLOBAL", name),             # TOS
        )

    def store_name(self, name):
        """ Store the TOS under name.

        """
        self.code_ops.append(                           # TOS -> value
            bc.Instr("STORE_NAME", name),             # TOS
        )

    def store_fast(self, name):
        """ Store the TOS as a fast local.

        """
        self.code_ops.append(                           # TOS -> value
            bc.Instr("STORE_FAST", name),               # TOS
        )

    def store_attr(self, name):
        """ Store the value at 2nd as an attr on 1st.

        """
        self.code_ops.append(                           # TOS -> val -> obj
            bc.Instr("STORE_ATTR", name),               # TOS
        )

    def delete_global(self, name):
        """ Delete a named global variable.

        """
        self.code_ops.append(                           # TOS
            bc.Instr("DELETE_GLOBAL", name),            # TOS
        )

    def delete_fast(self, name):
        """ Delete a named fast local variable.

        """
        self.code_ops.append(                           # TOS
            bc.Instr("DELETE_FAST", name),                     # TOS
        )

    def return_value(self):
        """ Return the value from the TOS.

        """
        self.code_ops.append(                           # TOS -> value
            bc.Instr("RETURN_VALUE"),                   # TOS
        )

    def binary_subscr(self):
        """ Subscript the #2 item with the TOS.

        """
        self.code_ops.append(                           # TOS -> obj -> idx
            bc.Instr("BINARY_SUBSCR"),                  # TOS -> value
        )

    def binary_multiply(self):
        """ Multiple the 2 items on the TOS.

        """
        self.code_ops.append(                           # TOS -> val_1 -> val_2
            bc.Instr("BINARY_MULTIPLY"),                # TOS -> retval
        )

    def binary_add(self):
        """ Multiple the 2 items on the TOS.

        """
        self.code_ops.append(                           # TOS -> val_1 -> val_2
            bc.Instr("BINARY_ADD"),                     # TOS -> retval
        )

    def dup_top(self):
        """ Duplicate the value on the TOS.

        """
        self.code_ops.append(                           # TOS -> value
            bc.Instr("DUP_TOP"),                        # TOS -> value -> value
        )

    def build_map(self, n=0):
        """ Build a map and store it onto the TOS.

        """
        self.code_ops.append(                           # TOS
            bc.Instr("BUILD_MAP", n),                   # TOS -> map
        )

    def build_tuple(self, n=0):
        """ Build a tuple from items on the TOS.

        """
        if n == 0:
            self.code_ops.append(                       # TOS
                bc.Instr("LOAD_CONST", ()),             # TOS -> tuple
            )
        else:
            self.code_ops.append(                       # TOS
                bc.Instr("BUILD_TUPLE", n),             # TOS -> tuple
            )

    def build_list(self, n=0):
        """ Build a list from items on the TOS.

        """
        self.code_ops.append(                           # TOS
            bc.Instr("BUILD_LIST", n),                  # TOS -> list
        )

    def add_map(self):
        """ Store the key/value pair on the TOS into the map at 3rd pos.

        """
        # WARNING in Python 3.8 the order is           # TOS -> map -> key -> value
        self.code_ops.append(                          # TOS -> map -> value -> key
            bc.Instr("MAP_ADD", 1),
        )

    def store_subscr(self):
        """ Store the index/value pair on the TOS into the 3rd item.

        """
        self.code_ops.append(                           # TOS -> value -> obj -> index
            bc.Instr("STORE_SUBSCR"),                   # TOS
        )

    def load_build_class(self):
        """ Build a class from the top 3 stack items.

        """
        self.code_ops.append(                           # TOS
            bc.Instr("LOAD_BUILD_CLASS"),               # TOS -> builtins.__build_class__
        )

    def make_function(self, n_defaults=0):
        """ Make a function from a code object on the TOS.

        """
        self.code_ops.append(                           # TOS -> qual_name -> code -> defaults
            bc.Instr("MAKE_FUNCTION", n_defaults),      # TOS -> func
        )

    def call_function(self, n_args=0, n_kwds=0):
        """ Call a function on the TOS with the given args and kwargs.

        """
        if USE_WORDCODE:
            if n_kwds:
                # kwargs_name should be a tuple listing the keyword
                # arguments names
                # TOS -> func -> args -> kwargs -> kwargs_names
                op, arg = "CALL_FUNCTION_KW", n_args+n_kwds
            else:
                op, arg = "CALL_FUNCTION", n_args
        else:
            argspec = ((n_kwds & 0xFF) << 8) + (n_args & 0xFF)
            op, arg = "CALL_FUNCTION", argspec  # TOS -> func -> args -> kwargs

        self.code_ops.append(bc.Instr(op, arg))          # TOS -> retval

    def call_function_var(self, n_args=0, n_kwds=0):
        """ Call a variadic function on the TOS with the given args and kwargs.

        """
        if USE_WORDCODE:
            # Under Python 3.6 positional arguments should always be stored
            # in a tuple and keywords in a mapping.
            argspec = 1 if n_kwds else 0
        else:
            argspec = ((n_kwds & 0xFF) << 8) + (n_args & 0xFF)

        opcode = ("CALL_FUNCTION_EX" if USE_WORDCODE else
                  "CALL_FUNCTION_VAR")
        self.code_ops.append(                           # TOS -> func -> args -> kwargs -> varargs
            bc.Instr(opcode, argspec),                  # TOS -> retval
        )

    def pop_top(self):
        """ Pop the value from the TOS.

        """
        self.code_ops.append(                           # TOS -> value
            bc.Instr("POP_TOP"),                        # TOS
        )

    def rot_two(self):
        """ Rotate the two values on the TOS.

        """
        self.code_ops.append(                           # TOS -> val_1 -> val_2
            bc.Instr("ROT_TWO"),                        # TOS -> val_2 -> val_1
        )

    def rot_three(self):
        """ Rotate the three values on the TOS.

        """
        self.code_ops.append(                           # TOS -> val_1 -> val_2 -> val_3
            bc.Instr("ROT_THREE"),                      # TOS -> val_3 -> val_1 -> val_2
        )

    def unpack_sequence(self, n):
        """ Unpack the sequence on the TOS.

        """
        self.code_ops.append(                           # TOS -> obj
            bc.Instr("UNPACK_SEQUENCE", n),             # TOS -> val_n -> val_2 -> val_1
        )

    @contextmanager
    def try_squash_raise(self):
        """ A context manager for squashing tracebacks.

        The code written during this context will be wrapped so that
        any exception raised will appear to have been generated from
        the code, rather than any function called by the code.

        """
        exc_label = bc.Label()
        end_label = bc.Label()
        op_code = "SETUP_FINALLY" if PY38 else "SETUP_EXCEPT"
        self.code_ops.append(
            bc.Instr(op_code, exc_label),         # TOS
        )
        yield
        self.code_ops.extend([                           # TOS
            bc.Instr("POP_BLOCK"),                       # TOS
            bc.Instr("JUMP_FORWARD", end_label),         # TOS
            exc_label,                                   # TOS -> tb -> val -> exc
            bc.Instr("ROT_THREE"),                       # TOS -> exc -> tb -> val
            bc.Instr("ROT_TWO"),                         # TOS -> exc -> val -> tb
            bc.Instr("POP_TOP"),                         # TOS -> exc -> val
            bc.Instr("RAISE_VARARGS", 2),                # TOS
            bc.Instr("JUMP_FORWARD", end_label),         # TOS
            bc.Instr("END_FINALLY"),                     # TOS
            end_label,                                   # TOS
        ])

    @contextmanager
    def for_loop(self, iter_var, fast_var=True):
        """ A context manager for creating for-loops.

        Parameters
        ----------
        iter_var : str
            The name of the loop iter variable.

        fast_var : bool, optional
            Whether the iter_var lives in fast locals. The default is
            True. If False, the iter_var is loaded from globals.

        """
        start_label = bc.Label()
        jump_label = bc.Label()
        # Unused under Python 3.8+ since the compiler handle the blocks
        # automatically
        end_label = bc.Label()
        load_op = "LOAD_FAST" if fast_var else "LOAD_GLOBAL"
        if PY38:
            self.code_ops.append(bc.Instr("SETUP_LOOP", end_label),)
        self.code_ops.extend([
            bc.Instr(load_op, iter_var),
            bc.Instr("GET_ITER"),
            start_label,
            bc.Instr("FOR_ITER", jump_label),
        ])
        yield
        self.code_ops.extend([
            bc.Instr("JUMP_ABSOLUTE", start_label),
            jump_label,
        ])
        if PY38:
            self.code_ops.extend(
                bc.Instr("POP_BLOCK"),
                end_label,
            )

    def insert_python_block(self, pydata, trim=True):
        """ Insert the compiled code for a Python Module ast or string.

        """
        code = compile(pydata, self.filename, mode='exec')
        bc_code = bc.Bytecode.from_code(code)
        if trim:  # skip  ReturnValue
            bc_code = bc_code[:-1]
        self.code_ops.extend(bc_code)

    def insert_python_expr(self, pydata, trim=True):
        """ Insert the compiled code for a Python Expression ast or string.

        """
        code = compile(pydata, self.filename, mode='eval')
        bc_code = bc.Bytecode.from_code(code)
        if trim:  # skip ReturnValue
            bc_code = bc_code[:-1]
        self.code_ops.extend(bc_code)

    def rewrite_to_fast_locals(self, local_names):
        """ Rewrite the locals to be loaded from fast locals.

        Given a set of available local names, this method will rewrite
        the current code ops, replaces every instance of a *_NAME opcode
        with a *_FAST or *_GLOBAL depending on whether or not the name
        exists in local_names or was written via STORE_NAME. This method
        is useful to convert the code so it can be used as a function.

        Parameters
        ----------
        local_names : set
            The set of available locals for the code.

        Returns
        -------
        result : list
            The list of names which must be provided as arguments.

        """
        arg_names = []
        stored_names = set()
        code_ops = self.code_ops
        for idx, instr in enumerate(code_ops):
            if instr.name == "STORE_NAME":
                stored_names.add(instr.arg)
                instr.name = "STORE_FAST"
        for idx, instr in enumerate(code_ops):
            i_name = instr.name
            if i_name == "LOAD_NAME":
                i_arg = instr.arg
                if i_arg in local_names:
                    op = "LOAD_FAST"
                    arg_names.append(i_arg)
                elif i_arg in stored_names:
                    op = "LOAD_FAST"
                else:
                    op = "LOAD_GLOBAL"
                instr.name = op
            elif i_name == "DELETE_NAME":
                if instr.arg in stored_names:
                    op = "DELETE_FAST"
                else:
                    op = "DELETE_GLOBAL"
                instr.name = op
        self.args = arg_names
        self.newlocals = True
        return arg_names
