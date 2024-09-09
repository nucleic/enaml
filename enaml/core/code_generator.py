# ------------------------------------------------------------------------------
# Copyright (c) 2013-2024, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ------------------------------------------------------------------------------
import ast
from contextlib import contextmanager

import bytecode as bc
from atom.api import Atom, Bool, Int, List, Str

from ..compat import PY310, PY311, PY312, PY313


class _ReturnNoneIdentifier(ast.NodeVisitor):
    """Visit top level nodes looking for return None."""

    def __init__(self) -> None:
        super().__init__()
        # Lines on which an explicit return None or return exist
        self.lines: set[int] = set()

    def visit_Return(self, node: ast.Return) -> None:
        if not node.value or (
            isinstance(node.value, ast.Constant) and node.value.value is None
        ):
            self.lines.add(node.lineno)

    # Do not inspect nodes in which a return None won't be relevant.
    def visit_AsyncFunctionDef(self, node):
        pass

    def visit_FunctionDef(self, node):
        pass

    def visit_ClassDef(self, node):
        pass


class CodeGenerator(Atom):
    """A class for generating bytecode operations.

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
        """Create a Python code object from the current code ops."""
        bc_code = bc.Bytecode(self.code_ops)
        bc_code.argnames = self.args
        # The number of positional or keyword args correspond to all args minus:
        # - the positionals only
        # - the keywords only
        # - the variadic positional
        # - the variadic keyword
        bc_code.argcount = (
            len(self.args)
            - self.kwonlyargs
            - self.posonlyargs
            - self.varargs
            - self.varkwargs
        )
        bc_code.posonlyargcount = self.posonlyargs
        bc_code.kwonlyargcount = self.kwonlyargs

        for name in ("name", "filename", "firstlineno", "docstring"):
            setattr(bc_code, name, getattr(self, name))

        # Set flags appropriately and update flags based on the instructions
        for setting, flag in zip(
            (self.varargs, self.varkwargs, self.newlocals),
            (
                bc.CompilerFlags.VARARGS,
                bc.CompilerFlags.VARKEYWORDS,
                bc.CompilerFlags.NEWLOCALS,
            ),
        ):
            # Set the flag
            if setting:
                bc_code.flags |= flag
            # Unset the flag if it was set
            else:
                bc_code.flags ^= bc_code.flags & flag
        bc_code.update_flags()
        # Ensure all code objects starts with a RESUME to get the right frame
        if PY311:
            for i, instr in enumerate(bc_code):
                if isinstance(instr, bc.Instr):
                    if instr.name != "RESUME":
                        bc_code.insert(i, bc.Instr("RESUME", 0))
                    break

        return bc_code.to_code()

    def set_lineno(self, lineno):
        """Set the current line number in the code."""
        self.code_ops.append(  # TOS
            bc.SetLineno(lineno),  # TOS
        )

    def load_global(self, name, push_null=False):
        """Load a global variable onto the TOS."""
        if PY311:
            args = (push_null, name)
        else:
            args = name
        self.code_ops.append(  # TOS
            bc.Instr("LOAD_GLOBAL", args),  # TOS -> value
        )

    def load_name(self, name):
        """Load a named variable onto the TOS."""
        self.code_ops.append(  # TOS
            bc.Instr("LOAD_NAME", name),  # TOS -> value
        )

    def load_fast(self, name):
        """Load a fast local variable onto the TOS."""
        self.code_ops.append(  # TOS
            bc.Instr("LOAD_FAST", name),  # TOS -> value
        )

    def load_const(self, const):
        """Load a const value onto the TOS."""
        self.code_ops.append(  # TOS
            bc.Instr("LOAD_CONST", const),  # TOS -> value
        )

    def load_attr(self, name):
        """Load an attribute from the object on TOS."""
        if PY312:
            args = (False, name)
        else:
            args = name
        self.code_ops.append(             # TOS -> obj
            bc.Instr("LOAD_ATTR", args),  # TOS -> value
        )

    def load_method(self, name):
        """Load a method from an object on TOS."""
        if PY312:
            self.code_ops.append(                     # TOS -> obj
                                                      # on 3.12 the order is reversed
                bc.Instr("LOAD_ATTR", (True, name)),  # TOS -> method -> self
            )
        else:
            # On 3.10 one has to use call_method next
            self.code_ops.append(bc.Instr("LOAD_METHOD", name))

    def store_global(self, name):
        """Store the TOS as a global."""
        self.code_ops.append(  # TOS -> value
            bc.Instr("STORE_GLOBAL", name),  # TOS
        )

    def store_name(self, name):
        """Store the TOS under name."""
        self.code_ops.append(  # TOS -> value
            bc.Instr("STORE_NAME", name),  # TOS
        )

    def store_fast(self, name):
        """Store the TOS as a fast local."""
        self.code_ops.append(  # TOS -> value
            bc.Instr("STORE_FAST", name),  # TOS
        )

    def store_attr(self, name):
        """Store the value at 2nd as an attr on 1st."""
        self.code_ops.append(  # TOS -> val -> obj
            bc.Instr("STORE_ATTR", name),  # TOS
        )

    def delete_global(self, name):
        """Delete a named global variable."""
        self.code_ops.append(  # TOS
            bc.Instr("DELETE_GLOBAL", name),  # TOS
        )

    def delete_fast(self, name):
        """Delete a named fast local variable."""
        self.code_ops.append(  # TOS
            bc.Instr("DELETE_FAST", name),  # TOS
        )

    def return_value(self):
        """Return the value from the TOS."""
        if PY312 and self.code_ops and self.code_ops[-1].name == "LOAD_CONST":
            self.code_ops[-1] = bc.Instr("RETURN_CONST", self.code_ops[-1].arg)
        else:
            self.code_ops.append(  # TOS -> value
                bc.Instr("RETURN_VALUE"),  # TOS
            )

    def binary_subscr(self):
        """Subscript the #2 item with the TOS."""
        self.code_ops.append(  # TOS -> obj -> idx
            bc.Instr("BINARY_SUBSCR"),  # TOS -> value
        )

    def binary_multiply(self):
        """Multiply the 2 items on the TOS."""
        if PY311:
            instr = bc.Instr("BINARY_OP", 5)
        else:
            instr = bc.Instr("BINARY_MULTIPLY")
        self.code_ops.append(  # TOS -> val_1 -> val_2
            instr,  # TOS -> retval
        )

    def binary_add(self):
        """Add the 2 items on the TOS."""
        if PY311:
            instr = bc.Instr("BINARY_OP", 0)
        else:
            instr = bc.Instr("BINARY_ADD")
        self.code_ops.append(  # TOS -> val_1 -> val_2
            instr,  # TOS -> retval
        )

    def dup_top(self):
        """Duplicate the value on the TOS."""
        if PY311:
            instr = bc.Instr("COPY", 1)
        else:
            instr = bc.Instr("DUP_TOP")
        self.code_ops.append(  # TOS -> value
            instr,  # TOS -> value -> value
        )

    def build_map(self, n=0):
        """Build a map and store it onto the TOS."""
        self.code_ops.append(  # TOS
            bc.Instr("BUILD_MAP", n),  # TOS -> map
        )

    def build_tuple(self, n=0):
        """Build a tuple from items on the TOS."""
        if n == 0:
            self.code_ops.append(  # TOS
                bc.Instr("LOAD_CONST", ()),  # TOS -> tuple
            )
        else:
            self.code_ops.append(  # TOS
                bc.Instr("BUILD_TUPLE", n),  # TOS -> tuple
            )

    def build_list(self, n=0):
        """Build a list from items on the TOS."""
        self.code_ops.append(  # TOS
            bc.Instr("BUILD_LIST", n),  # TOS -> list
        )

    def add_map(self):
        """Store the key/value pair on the TOS into the map at 3rd pos."""
        # WARNING in Python 3.8 the order is           # TOS -> map -> key -> value
        self.code_ops.append(  # TOS -> map -> value -> key
            bc.Instr("MAP_ADD", 1),
        )

    def store_subscr(self):
        """Store the index/value pair on the TOS into the 3rd item."""
        self.code_ops.append(  # TOS -> value -> obj -> index
            bc.Instr("STORE_SUBSCR"),  # TOS
        )

    def load_build_class(self):
        """Build a class from the top 3 stack items."""
        self.code_ops.append(  # TOS
            bc.Instr("LOAD_BUILD_CLASS"),  # TOS -> builtins.__build_class__
        )

    def make_function(self, flags=0, name=None):
        """Make a function from a code object on the TOS."""
        if not PY311:
            self.load_const(name)
        if PY313:
            if flags:
                self.code_ops.extend(
                    (
                        bc.Instr("MAKE_FUNCTION"), # TOS -> qual_name -> code
                        bc.Instr("SET_FUNCTION_ATTRIBUTE", flags),  # TOS -> func -> attrs
                    )
                )
            else:
                self.code_ops.append(bc.Instr("MAKE_FUNCTION"))
        else:
            self.code_ops.append(  # TOS -> qual_name -> code -> defaults
                bc.Instr("MAKE_FUNCTION", flags),  # TOS -> func
            )

    def push_null(self):
        """Push NULL on the TOS."""
        self.code_ops.append(  # TOS
            bc.Instr("PUSH_NULL"),  # TOS -> NULL
        )

    def call_function(self, n_args=0, n_kwds=0, is_method: bool = False):
        """Call a function on the TOS with the given args and kwargs."""
        if PY313:
            # NOTE: In Python 3.13 the caller must push null
            # onto the stack before calling this
            # TOS -> func -> null -> args -> kwargs_names -> kwargs (tuple)
            arg = n_args + n_kwds
            self.code_ops.append(bc.Instr("CALL_KW" if n_kwds else "CALL", arg))
        elif PY311:
            # NOTE: In Python 3.11 the caller must push null
            # onto the stack before calling this
            # TOS -> null -> func -> args -> kwargs -> kwargs_names
            # In Python 3.12 PRECALL was removed
            arg = n_args + n_kwds
            ops = [bc.Instr("CALL", arg)]
            if not PY312:
                ops = [bc.Instr("PRECALL", arg)] + ops
            if n_kwds:
                ops.insert(0, bc.Instr("KW_NAMES", 3))
            self.code_ops.extend(ops)
        else:
            if n_kwds:
                if is_method:
                    raise ValueError(
                        "Method calling convention cannot be used with keywords"
                    )
                # kwargs_name should be a tuple listing the keyword
                # arguments names
                # TOS -> func -> args -> kwargs -> kwargs_names
                op, arg = "CALL_FUNCTION_KW", n_args + n_kwds
            elif is_method:
                op, arg = "CALL_METHOD", n_args
            else:
                op, arg = "CALL_FUNCTION", n_args
            self.code_ops.append(bc.Instr(op, arg))  # TOS -> retval

    def call_function_var(self, n_args=0, n_kwds=0):
        """Call a variadic function on the TOS with the given args and kwargs."""
        # Under Python 3.6+ positional arguments should always be stored
        # in a tuple and keywords in a mapping.
        argspec = 1 if n_kwds else 0

        self.code_ops.append(  # TOS -> func -> args -> kwargs -> varargs
            bc.Instr("CALL_FUNCTION_EX", argspec),  # TOS -> retval
        )

    def pop_top(self):
        """Pop the value from the TOS."""
        self.code_ops.append(  # TOS -> value
            bc.Instr("POP_TOP"),  # TOS
        )

    def rot_two(self):
        """Rotate the two values on the TOS."""
        if PY311:
            instr = bc.Instr("SWAP", 2)
        else:
            instr = bc.Instr("ROT_TWO")
        self.code_ops.append(  # TOS -> val_1 -> val_2
            instr,  # TOS -> val_2 -> val_1
        )

    def rot_three(self):
        """Rotate the three values on the TOS."""
        if PY311:
            self.code_ops.extend(
                (  # TOS -> val_1 -> val_2 -> val_3
                    bc.Instr("SWAP", 3),  # TOS -> val_3 -> val_2 -> val_1
                    bc.Instr("SWAP", 2),  # TOS -> val_3 -> val_1 -> val_2
                )
            )
        else:
            self.code_ops.append(  # TOS -> val_1 -> val_2 -> val_3
                bc.Instr("ROT_THREE")  # TOS -> val_3 -> val_1 -> val_2
            )

    def unpack_sequence(self, n):
        """Unpack the sequence on the TOS."""
        self.code_ops.append(  # TOS -> obj
            bc.Instr("UNPACK_SEQUENCE", n),  # TOS -> val_n -> val_2 -> val_1
        )

    @contextmanager
    def try_squash_raise(self):
        """A context manager for squashing tracebacks.

        The code written during this context will be wrapped so that
        any exception raised will appear to have been generated from
        the code, rather than any function called by the code.

        Under Python 3.11 this is safe to use only if the inner code does not
        contain TryBegin pseudo-instructions.

        """
        exc_label = bc.Label()
        end_label = bc.Label()
        if PY311:
            self.code_ops.append(tb := bc.TryBegin(exc_label, False))
            first_new = len(self.code_ops)
            yield
            for i in self.code_ops[first_new:]:
                if isinstance(i, bc.TryBegin):
                    raise ValueError(
                        "try_squash_raise cannot wrap a block containing "
                        "exception handling logic. Wrapped block is:\n"
                        f"{self.code_ops[first_new:]}"
                    )
            ops = [
                bc.TryEnd(tb),
                bc.Instr("JUMP_FORWARD", end_label),
                # Under Python 3.11 only the actual exception is pushed
                exc_label,  # TOS -> val
                bc.Instr("LOAD_CONST", None),  # TOS -> val -> None
                bc.Instr("COPY", 2),  # TOS -> val -> None -> val
                bc.Instr("STORE_ATTR", "__traceback__"),  # TOS -> val
                bc.Instr("RAISE_VARARGS", 1),
                end_label,
            ]
            self.code_ops.extend(ops)
        else:
            op_code = "SETUP_FINALLY"
            self.code_ops.append(
                bc.Instr(op_code, exc_label),  # TOS
            )
            yield
            # exc is only the exception type which can be used for matching
            # val is the exception value, raising it directly preserve the traceback
            # tb is the traceback and is of little interest
            # We reset the traceback to None to make it appear as if the code
            # raised the exception instead of a function called by it
            ops = [  # TOS
                bc.Instr("POP_BLOCK"),  # TOS
                bc.Instr("JUMP_FORWARD", end_label),  # TOS
                exc_label,  # TOS -> tb -> val -> exc
                bc.Instr("POP_TOP"),  # TOS -> tb -> val
                bc.Instr("ROT_TWO"),  # TOS -> val -> tb
                bc.Instr("POP_TOP"),  # TOS -> val
                bc.Instr("DUP_TOP"),  # TOS -> val -> val
                bc.Instr("LOAD_CONST", None),  # TOS -> val -> val -> None
                bc.Instr("ROT_TWO"),  # TOS -> val -> None -> val
                bc.Instr("STORE_ATTR", "__traceback__"),  # TOS -> val
                bc.Instr("RAISE_VARARGS", 1),  # TOS
                bc.Instr("POP_EXCEPT"),
                bc.Instr("JUMP_FORWARD", end_label),  # TOS
                end_label,  # TOS
            ]
            self.code_ops.extend(ops)

    @contextmanager
    def for_loop(self, iter_var, fast_var=True):
        """A context manager for creating for-loops.

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
        self.code_ops.append(
            bc.Instr("SETUP_LOOP", end_label),
        )
        if PY311 and not fast_var:
            # LOAD_GLOBAL expects a tuple on 3.11
            iter_var = (False, iter_var)
        self.code_ops.extend(
            [
                bc.Instr(load_op, iter_var),
                bc.Instr("GET_ITER"),
                start_label,
                bc.Instr("FOR_ITER", jump_label),
            ]
        )
        yield
        self.code_ops.extend(
            [
                bc.Instr("JUMP_BACKWARD", start_label)
                if PY312
                else bc.Instr("JUMP_ABSOLUTE", start_label),
                jump_label,
            ]
        )
        self.code_ops.extend(
            bc.Instr("POP_BLOCK"),
            end_label,
        )
        if PY312:
            self.code_ops.append(bc.Instr("END_FOR"))

    def insert_python_block(self, pydata, trim=True):
        """Insert the compiled code for a Python Module ast or string."""
        if PY310:
            _inspector = _ReturnNoneIdentifier()
            _inspector.visit(pydata)
        code = compile(pydata, self.filename, mode="exec")
        bc_code = bc.Bytecode.from_code(code)
        if PY311:  # Trim irrelevant RESUME opcode
            bc_code = bc_code[1:]
        # On python 3.10 with a with or try statement the implicit return None
        # can be duplicated. We remove return None from all basic blocks when
        # it was not present in the AST
        if PY310:
            cfg = bc.ControlFlowGraph.from_bytecode(bc_code)
            new_end = None
            last_block = cfg[-1]
            for block in list(cfg):
                if isinstance(block[-1], bc.Instr) and (
                    (rc := (block[-1].name == "RETURN_CONST" and block[-1].arg is None))
                    or (
                        block[-1].name == "RETURN_VALUE"
                        and block[-2].name == "LOAD_CONST"
                        and block[-2].arg is None
                        and block[-1].lineno not in _inspector.lines
                    )
                ):
                    if rc:
                        del block[-1]
                    else:
                        del block[-2:]
                    # If as a result of the trimming the block is empty, we add
                    # a NOP to make sure it is valid still
                    if not any(isinstance(i, bc.Instr) for i in block):
                        block.append(bc.Instr("NOP"))
                    # If we have multiple block jump to the end of the last block
                    # to execute the code that may be appended to this block
                    if block is not last_block:
                        # We use a NOP to be sure to always have a valid jump target
                        new_end = new_end or cfg.add_block([bc.Instr("NOP")])
                        block.append(bc.Instr("JUMP_FORWARD", new_end))
                    elif new_end is not None:
                        last_block.next_block = new_end

            bc_code = cfg.to_bytecode()
        # Skip the LOAD_CONST RETURN_VALUE pair if it exists
        elif trim and bc_code[-1].name == "RETURN_VALUE":
            bc_code = bc_code[:-2]

        self.code_ops.extend(bc_code)

    def insert_python_expr(self, pydata, trim=True):
        """Insert the compiled code for a Python Expression ast or string."""
        code = compile(pydata, self.filename, mode="eval")
        bc_code = bc.Bytecode.from_code(code)
        if PY311:  # Trim irrelevant RESUME opcode
            bc_code = bc_code[1:]
        if bc_code[-1].name == "RETURN_CONST":
            bc_code[-1] = bc.Instr(
                "LOAD_CONST", bc_code[-1].arg, location=bc_code[-1].location
            )
            trim = False
        if trim:  # skip RETURN_VALUE opcode
            bc_code = bc_code[:-1]
        self.code_ops.extend(bc_code)

    def rewrite_to_fast_locals(self, local_names):
        """Rewrite the locals to be loaded from fast locals.

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
            if not isinstance(instr, bc.Instr):
                continue
            if instr.name == "STORE_NAME":
                stored_names.add(instr.arg)
                instr.name = "STORE_FAST"
        for idx, instr in enumerate(code_ops):
            if not isinstance(instr, bc.Instr):
                continue
            i_name = instr.name
            if i_name == "LOAD_NAME":
                i_arg = instr.arg
                if i_arg in local_names:
                    op = "LOAD_FAST"
                    arg_names.append(i_arg)
                elif i_arg in stored_names:
                    op = "LOAD_FAST"
                elif PY311:
                    # TODO: Is there a better way to do this?
                    code_ops[idx] = bc.Instr("LOAD_GLOBAL", (False, instr.arg))
                    continue
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
