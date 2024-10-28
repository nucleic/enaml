#------------------------------------------------------------------------------
# Copyright (c) 2013-2024, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from types import CodeType

import bytecode as bc
from ..compat import PY311, PY312, PY313


class CodeTracer(object):
    """ A base class for implementing code tracers.

    This class defines the interface for a code tracer object, which is
    an object which can be passed as the first argument to a code object
    which has been transformed to enable tracing. Methods on the tracer
    are called with relevant arguments from the Python stack when that
    particular code segment is executing. The return value of a tracer
    method is ignored; exceptions are propagated.

    """
    __slots__ = ()

    def dynamic_load(self, obj, attr, value):
        """ Called when an dynamic attribute is loaded.

        This method is called by the dynamic scope when it loads an
        attribute from some object in the object hierarchy due to the
        execution of the LOAD_NAME opcode.

        Parameters
        ----------
        obj : Object
            The Enaml object which owns the dynamically scoped attr.

        attr : str
            The name of the attribute which was loaded.

        value : object
            The value which was loaded.

        """
        pass

    def load_attr(self, obj, attr):
        """ Called before the LOAD_ATTR opcode is executed.

        Parameters
        ----------
        obj : object
            The object which owns the attribute.

        attr : string
            The attribute being loaded.

        """
        pass

    def call_function(self, func, argtuple, argspec):
        """ Called before the CALL opcode is executed.

        The CALL is only used for function call with only positional
        arguments in Python 3.6+ so argspec is actually just the argument
        number but is kept for backward compatibility.

        Parameters
        ----------
        func : object
            The object being called.

        argtuple : tuple
            The argument tuple from the stack.

        argspec : int
            Len of the argtuple kept for backward compatibility.

        """
        pass

    def binary_subscr(self, obj, idx):
        """ Called before the BINARY_SUBSCR opcode is executed.

        Parameters
        ----------
        obj : object
            The object being indexed.

        idx : object
            The index.

        """
        pass

    def get_iter(self, obj):
        """ Called before the GET_ITER opcode is executed.

        Parameters
        ----------
        obj : object
            The object which should return an iterator.

        """
        pass

    def return_value(self, value):
        """ Called before the RETURN_VALUE opcode is executed.

        Parameters
        ----------
        value : object
            The value that will be returned from the code object.

        """
        pass


class CodeInverter(object):
    """ A base class for implementing code inverters.

    This class defines the interface for a code inverter object, which is
    an object which can be passed as the first argument to a code object
    which has been transformed to enable inversion. The methods on the
    inverter are called with relevant arguments from the Python stack
    when that particular code segment is executing. The return values of
    a tracer method is ignored; exceptions are propagated.

    The default behavior of an inverter is to raise. Implementations
    must provide their own code in order to enable inversion.

    """
    __slots__ = ()

    def fail(self):
        """ Called by handlers to raise an inversion exception.

        """
        raise RuntimeError("can't assign to expression")

    def load_name(self, name, value):
        """ Called before the LOAD_NAME opcode is executed.

        This method should perform a STORE_NAME operation.

        Parameters
        ----------
        name : string
            The name being loaded.

        value : object
            The value to store.

        """
        self.fail()

    def load_attr(self, obj, attr, value):
        """ Called before the LOAD_ATTR opcode is executed.

        This method should perform a STORE_ATTR operation.

        Parameters
        ----------
        obj : object
            The object which owns the attribute.

        attr : string
            The attribute being loaded.

        value : object
            The value to store

        """
        self.fail()

    def call_function(self, func, argtuple, argspec, value):
        """ Called before the CALL_FUNCTION opcode is executed.

        The CALL_FUNCTION is only used for function call with only positional
        arguments in Python 3.6+ so argspec is actually just the argument
        number but is kept for backward compatibility.

        This method should perform an appropriate store operation.

        Parameters
        ----------
        func : object
            The object being called.

        argtuple : tuple
            The argument tuple from the stack.

        argspec : int
            Len of the argtuple kept for backward compatibility.

        value : object
            The value to store.

        Notes
        -----
        The semantics of the arguments is identical to the method
        `call_function` on the `CodeTracer` type.

        """
        self.fail()

    def binary_subscr(self, obj, idx, value):
        """ Called before the BINARY_SUBSCR opcode is executed.

        This method should perform a STORE_SUBSCR operation.

        Parameters
        ----------
        obj : object
            The object being indexed.

        idx : object
            The index.

        value : object
            The value to store.

        """
        self.fail()

if PY313:
    def call_tracer_load_attr(tracer_op: str, i_arg: int, Instr=bc.Instr):
        return [                                         # obj
            Instr(tracer_op, '_[tracer]'),               # obj -> tracer
            Instr("LOAD_ATTR", (False, 'load_attr')),    # obj -> tracefunc
            Instr("PUSH_NULL"),                          # obj -> tracefunc -> null
            Instr("COPY", 3),                            # obj -> tracefunc -> null -> obj
            Instr("LOAD_CONST", i_arg),                  # obj -> tracefunc -> null -> obj -> attr
            Instr("CALL", 0x0002),                       # obj -> retval
            Instr("POP_TOP"),                            # obj
        ]

    def call_tracer_call_function(tracer_op: str, i_arg: int, Instr=bc.Instr):
        # n_stack_args = i_arg
        return [                                           # func -> null -> arg(0) -> arg(1) -> ... -> arg(n-1)
            Instr("BUILD_TUPLE", i_arg),                   # func -> null -> argtuple
            Instr(tracer_op, '_[tracer]'),                 # func -> null -> argtuple -> tracer
            Instr("LOAD_ATTR", (False, 'call_function')),  # func -> null -> argtuple -> tracefunc
            Instr("PUSH_NULL"),                            # func -> null -> argtuple -> tracefunc -> null
            Instr("COPY", 5),                              # func -> null -> argtuple -> tracefunc -> null -> func
            Instr("COPY", 4),                              # func -> null -> argtuple -> tracefunc -> null -> func -> argtuple
            Instr("LOAD_CONST", i_arg),                    # func -> null -> argtuple -> tracefunc -> null -> func -> argtuple -> argspec
            Instr("CALL", 0x0003),                         # func -> null -> argtuple -> retval
            Instr("POP_TOP"),                              # func -> null -> argtuple
            Instr("UNPACK_SEQUENCE", i_arg),               # func -> null -> arg(n-1) -> arg(n-2) -> ... -> arg(0)
            Instr("BUILD_TUPLE", i_arg),                   # func -> null -> reversedargtuple
            Instr("UNPACK_SEQUENCE", i_arg),               # func -> null -> arg(0) -> arg(1) -> ... -> arg(n-1)
        ]

    def call_tracer_binary_subscr(tracer_op: str, Instr=bc.Instr):
        return [                                           # obj -> idx
            Instr(tracer_op, '_[tracer]'),                 # obj -> idx -> tracer
            Instr("LOAD_ATTR", (False, 'binary_subscr')),  # obj -> idx -> tracefunc
            Instr("PUSH_NULL"),                            # obj -> idx -> tracefunc -> null
            Instr("COPY", 4),                              # obj -> idx -> tracefunc -> null -> obj
            Instr("COPY", 4),                              # obj -> idx -> tracefunc -> null -> obj -> idx
            Instr("CALL", 0x0002),                         # obj -> idx -> retval
            Instr("POP_TOP"),                              # obj -> idx
        ]

    def call_tracer_get_iter(tracer_op: str, Instr=bc.Instr):
        return [                                      # obj
            Instr(tracer_op, '_[tracer]'),            # obj -> tracer
            Instr("LOAD_ATTR", (False, 'get_iter')),  # obj -> tracefunc
            Instr("PUSH_NULL"),                       # obj -> tracefunc -> null
            Instr("COPY", 3),                         # obj -> tracefunc -> null -> obj
            Instr("CALL", 0x0001),                    # obj -> retval
            Instr("POP_TOP"),                         # obj
        ]

    def call_tracer_return_value(tracer_op: str, Instr=bc.Instr):
        return [
            Instr(tracer_op, '_[tracer]'),                # obj -> tracer
            Instr("LOAD_ATTR", (False, 'return_value')),  # obj -> tracefunc
            Instr("PUSH_NULL"),                           # obj -> tracefunc -> null
            Instr("COPY", 3),                             # obj -> tracefunc -> null -> obj
            Instr("CALL", 0x0001),                        # obj -> retval
            Instr("POP_TOP"),                             # obj
        ]

    def call_tracer_return_const(tracer_op: str, const, Instr=bc.Instr):
        return [
            Instr(tracer_op, '_[tracer]'),                # obj -> tracer
            Instr("LOAD_ATTR", (False, 'return_value')),  # obj -> tracefunc
            Instr("PUSH_NULL"),                           # obj -> tracefunc -> null
            Instr("LOAD_CONST", const),                   # obj -> tracefunc -> null -> obj
            Instr("CALL", 0x0001),                        # obj -> retval
            Instr("POP_TOP"),                             # obj
        ]

elif PY312:
    def call_tracer_load_attr(tracer_op: str, i_arg: int, Instr=bc.Instr):
        return [                                         # obj
            Instr("PUSH_NULL"),                          # obj -> null
            Instr(tracer_op, '_[tracer]'),               # obj -> null -> tracer
            Instr("LOAD_ATTR", (False, 'load_attr')),    # obj -> null -> tracefunc
            Instr("COPY", 3),                            # obj -> null -> tracefunc -> obj
            Instr("LOAD_CONST", i_arg),                  # obj -> null -> tracefunc -> obj -> attr
            Instr("CALL", 0x0002),                       # obj -> retval
            Instr("POP_TOP"),                            # obj
        ]

    def call_tracer_call_function(tracer_op: str, i_arg: int, Instr=bc.Instr):
        # n_stack_args = i_arg
        return [                                           # func -> arg(0) -> arg(1) -> ... -> arg(n-1)
            Instr("BUILD_TUPLE", i_arg),                   # func -> argtuple
            Instr("PUSH_NULL"),                            # func -> argtuple -> null
            Instr(tracer_op, '_[tracer]'),                 # func -> argtuple -> null -> tracer
            Instr("LOAD_ATTR", (False, 'call_function')),  # func -> argtuple -> null -> tracefunc
            Instr("COPY", 4),                              # func -> argtuple -> null -> tracefunc -> func
            Instr("COPY", 4),                              # func -> argtuple -> null -> tracefunc -> func -> argtuple
            Instr("LOAD_CONST", i_arg),                    # func -> argtuple -> null -> tracefunc -> func -> argtuple -> argspec
            Instr("CALL", 0x0003),                         # func -> argtuple -> retval
            Instr("POP_TOP"),                              # func -> argtuple
            Instr("UNPACK_SEQUENCE", i_arg),               # func -> arg(n-1) -> arg(n-2) -> ... -> arg(0)
            Instr("BUILD_TUPLE", i_arg),                   # func -> reversedargtuple
            Instr("UNPACK_SEQUENCE", i_arg),               # func -> arg(0) -> arg(1) -> ... -> arg(n-1)
        ]

    def call_tracer_binary_subscr(tracer_op: str, Instr=bc.Instr):
        return [                                           # obj -> idx
            Instr("PUSH_NULL"),                            # obj -> idx -> null
            Instr(tracer_op, '_[tracer]'),                 # obj -> idx -> null -> tracer
            Instr("LOAD_ATTR", (False, 'binary_subscr')),  # obj -> idx -> null -> tracefunc
            Instr("COPY", 4),                              # obj -> idx -> null -> tracefunc -> obj
            Instr("COPY", 4),                              # obj -> idx -> null -> tracefunc -> obj -> idx
            Instr("CALL", 0x0002),                         # obj -> idx -> retval
            Instr("POP_TOP"),                              # obj -> idx
        ]

    def call_tracer_get_iter(tracer_op: str, Instr=bc.Instr):
        return [                                      # obj
            Instr("PUSH_NULL"),                       # obj -> null
            Instr(tracer_op, '_[tracer]'),            # obj -> null -> tracer
            Instr("LOAD_ATTR", (False, 'get_iter')),  # obj -> null -> tracefunc
            Instr("COPY", 3),                         # obj -> null -> tracefunc -> obj
            Instr("CALL", 0x0001),                    # obj -> retval
            Instr("POP_TOP"),                         # obj
        ]

    def call_tracer_return_value(tracer_op: str, Instr=bc.Instr):
        return [
            Instr("PUSH_NULL"),                           # obj -> null
            Instr(tracer_op, '_[tracer]'),                # obj -> null -> tracer
            Instr("LOAD_ATTR", (False, 'return_value')),  # obj -> null -> tracefunc
            Instr("COPY", 3),                             # obj -> null -> tracefunc -> obj
            Instr("CALL", 0x0001),                        # obj -> retval
            Instr("POP_TOP"),                             # obj
        ]

    def call_tracer_return_const(tracer_op: str, const, Instr=bc.Instr):
        return [
            Instr("PUSH_NULL"),                           # obj -> null
            Instr(tracer_op, '_[tracer]'),                # obj -> null -> tracer
            Instr("LOAD_ATTR", (False, 'return_value')),  # obj -> null -> tracefunc
            Instr("LOAD_CONST", const),                   # obj -> null -> tracefunc -> obj
            Instr("CALL", 0x0001),                        # obj -> retval
            Instr("POP_TOP"),                             # obj
        ]

elif PY311:
    def call_tracer_load_attr(tracer_op: str, i_arg: int, Instr=bc.Instr):
        return [                                # obj
            Instr("PUSH_NULL"),                 # obj -> null
            Instr(tracer_op, '_[tracer]'),      # obj -> null -> tracer
            Instr("LOAD_ATTR", 'load_attr'),    # obj -> null -> tracefunc
            Instr("COPY", 3),                   # obj -> null -> tracefunc -> obj
            Instr("LOAD_CONST", i_arg),         # obj -> null -> tracefunc -> obj -> attr
            Instr("PRECALL", 0x0002),
            Instr("CALL", 0x0002),              # obj -> retval
            Instr("POP_TOP"),                   # obj
        ]

    def call_tracer_call_function(tracer_op: str, i_arg: int, Instr=bc.Instr):
        # n_stack_args = i_arg
        return [                                      # func -> arg(0) -> arg(1) -> ... -> arg(n-1)
            Instr("BUILD_TUPLE", i_arg),              # func -> argtuple
            Instr("PUSH_NULL"),                       # func -> argtuple -> null
            Instr(tracer_op, '_[tracer]'),            # func -> argtuple -> null -> tracer
            Instr("LOAD_ATTR", 'call_function'),      # func -> argtuple -> null -> tracefunc
            Instr("COPY", 4),                         # func -> argtuple -> null -> tracefunc -> func
            Instr("COPY", 4),                         # func -> argtuple -> null -> tracefunc -> func -> argtuple
            Instr("LOAD_CONST", i_arg),               # func -> argtuple -> null -> tracefunc -> func -> argtuple -> argspec
            Instr("PRECALL", 0x0003),
            Instr("CALL", 0x0003),                    # func -> argtuple -> retval
            Instr("POP_TOP"),                         # func -> argtuple
            Instr("UNPACK_SEQUENCE", i_arg),          # func -> arg(n-1) -> arg(n-2) -> ... -> arg(0)
            Instr("BUILD_TUPLE", i_arg),              # func -> reversedargtuple
            Instr("UNPACK_SEQUENCE", i_arg),          # func -> arg(0) -> arg(1) -> ... -> arg(n-1)
        ]

    def call_tracer_binary_subscr(tracer_op: str, Instr=bc.Instr):
        return [                                  # obj -> idx
            Instr("PUSH_NULL"),                   # obj -> idx -> null
            Instr(tracer_op, '_[tracer]'),        # obj -> idx -> null -> tracer
            Instr("LOAD_ATTR", 'binary_subscr'),  # obj -> idx -> null -> tracefunc
            Instr("COPY", 4),                     # obj -> idx -> null -> tracefunc -> obj
            Instr("COPY", 4),                     # obj -> idx -> null -> tracefunc -> obj -> idx
            Instr("PRECALL", 0x0002),
            Instr("CALL", 0x0002),                # obj -> idx -> retval
            Instr("POP_TOP"),                     # obj -> idx
        ]

    def call_tracer_get_iter(tracer_op: str, Instr=bc.Instr):
        return [                             # obj
            Instr("PUSH_NULL"),              # obj -> null
            Instr(tracer_op, '_[tracer]'),   # obj -> null -> tracer
            Instr("LOAD_ATTR", 'get_iter'),  # obj -> null -> tracefunc
            Instr("COPY", 3),                # obj -> null -> tracefunc -> obj
            Instr("PRECALL", 0x0001),
            Instr("CALL", 0x0001),           # obj -> retval
            Instr("POP_TOP"),                # obj
        ]

    def call_tracer_return_value(tracer_op: str, Instr=bc.Instr):
        return [
            Instr("PUSH_NULL"),                  # obj -> null
            Instr(tracer_op, '_[tracer]'),       # obj -> null -> tracer
            Instr("LOAD_ATTR", 'return_value'),  # obj -> null -> tracefunc
            Instr("COPY", 3),                    # obj -> null -> tracefunc -> obj
            Instr("PRECALL", 0x0001),
            Instr("CALL", 0x0001),               # obj -> retval
            Instr("POP_TOP"),                    # obj
        ]

    def call_tracer_return_const(tracer_op: str, const, Instr=bc.Instr):
        raise NotImplementedError()

else:
    def call_tracer_load_attr(tracer_op: str, i_arg: int, Instr=bc.Instr):
        return [                                # obj
            Instr("DUP_TOP"),                   # obj -> obj
            Instr(tracer_op, '_[tracer]'),      # obj -> obj -> tracer
            Instr("LOAD_ATTR", 'load_attr'),    # obj -> obj -> tracefunc
            Instr("ROT_TWO"),                   # obj -> tracefunc -> obj
            Instr("LOAD_CONST", i_arg),         # obj -> tracefunc -> obj -> attr
            Instr("CALL_FUNCTION", 0x0002),     # obj -> retval
            Instr("POP_TOP"),                   # obj
        ]

    def call_tracer_call_function(tracer_op: str, i_arg: int, Instr=bc.Instr):
        # n_stack_args = i_arg
        return [                                      # func -> arg(0) -> arg(1) -> ... -> arg(n-1)
            Instr("BUILD_TUPLE", i_arg),              # func -> argtuple
            Instr("DUP_TOP_TWO"),                     # func -> argtuple -> func -> argtuple
            Instr(tracer_op, '_[tracer]'),            # func -> argtuple -> func -> argtuple -> tracer
            Instr("LOAD_ATTR", 'call_function'),      # func -> argtuple -> func -> argtuple -> tracefunc
            Instr("ROT_THREE"),                       # func -> argtuple -> tracefunc -> func -> argtuple
            Instr("LOAD_CONST", i_arg),               # func -> argtuple -> tracefunc -> func -> argtuple -> argspec
            Instr("CALL_FUNCTION", 0x0003),           # func -> argtuple -> retval
            Instr("POP_TOP"),                         # func -> argtuple
            Instr("UNPACK_SEQUENCE", i_arg),          # func -> arg(n-1) -> arg(n-2) -> ... -> arg(0)
            Instr("BUILD_TUPLE", i_arg),              # func -> reversedargtuple
            Instr("UNPACK_SEQUENCE", i_arg),          # func -> arg(0) -> arg(1) -> ... -> arg(n-1)
        ]

    def call_tracer_binary_subscr(tracer_op: str, Instr=bc.Instr):
        return [                                  # obj -> idx
            Instr("DUP_TOP_TWO"),                 # obj -> idx -> obj -> idx
            Instr(tracer_op, '_[tracer]'),        # obj -> idx -> obj -> idx -> tracer
            Instr("LOAD_ATTR", 'binary_subscr'),  # obj -> idx -> obj -> idx -> tracefunc
            Instr("ROT_THREE"),                   # obj -> idx -> tracefunc -> obj -> idx
            Instr("CALL_FUNCTION", 0x0002),       # obj -> idx -> retval
            Instr("POP_TOP"),                     # obj -> idx
        ]

    def call_tracer_get_iter(tracer_op: str, Instr=bc.Instr):
        return [                             # obj
            Instr("DUP_TOP"),                # obj -> obj
            Instr(tracer_op, '_[tracer]'),   # obj -> obj -> tracer
            Instr("LOAD_ATTR", 'get_iter'),  # obj -> obj -> tracefunc
            Instr("ROT_TWO"),                # obj -> tracefunc -> obj
            Instr("CALL_FUNCTION", 0x0001),  # obj -> retval
            Instr("POP_TOP"),                # obj
        ]

    def call_tracer_return_value(tracer_op: str, Instr=bc.Instr):
        return [                                 # obj
            Instr("DUP_TOP"),                    # obj -> obj
            Instr(tracer_op, '_[tracer]'),       # obj -> obj -> tracer
            Instr("LOAD_ATTR", 'return_value'),  # obj -> obj -> tracefunc
            Instr("ROT_TWO"),                    # obj -> tracefunc -> obj
            Instr("CALL_FUNCTION", 0x0001),      # obj -> retval
            Instr("POP_TOP"),                    # obj
        ]

    def call_tracer_return_const(tracer_op: str, const, Instr=bc.Instr):
        raise NotImplementedError()


def inject_tracing(bytecode, nested=False):
    """ Inject tracing code into the given code list.

    This will inject the bytecode operations required to trace the
    execution of the code using a `CodeTracer` object. The generated
    opcodes expect a fast local '_[tracer]' to be available when the
    code is executed.

    Parameters
    ----------
    bytecode : bytecode.Bytecode
        The bytecode to modify.
    nested : bool
        Is the code modified defined inside an already traced code in which
        case the tracer is in the local namespace and not the fast locals.

    Returns
    -------
    result : list
        A *new* list of code ops which implement the desired behavior.

    """
    # If the code is nested into another already traced code, we need to use
    # LOAD_NAME to access the tracer rather than LOAD_FAST
    tracer_op = "LOAD_NAME" if nested else "LOAD_FAST"

    # This builds a mapping of code idx to a list of ops, which are the
    # tracing bytecode instructions which will be inserted into the code
    # object being transformed. The ops assume that a tracer object is
    # available in the fast locals using a non-clashable name. All of
    # the ops have a net-zero effect on the execution stack. Provided
    # that the tracer has no visible side effects, the tracing is
    # transparent.
    inserts = {}
    i_name = None
    for idx, instr in enumerate(bytecode):
        # Filter out SetLineno and Label
        if not isinstance(instr, bc.Instr):
            continue
        last_i_name = i_name
        i_name = instr.name
        i_arg = instr.arg
        if i_name == "LOAD_ATTR":
            inserts[idx] = call_tracer_load_attr(tracer_op, i_arg[1] if PY312 else i_arg)
        # We do not trace CALL_FUNCTION_KW and CALL_FUNCTION_EX since
        # tracing and inverting only require to detect getattr and setattr
        # both in this project and in traits-enaml. Those two are always called
        # using the CALL_FUNCTION bytecode instruction.
        elif i_name == "CALL_FUNCTION":
            # From Python 3.6, CALL_FUNCTION is only used for positional
            # arguments and the argument is directly the number of arguments
            # on the stack.
            inserts[idx] = call_tracer_call_function(tracer_op, i_arg)
        elif PY312 and i_name == "CALL" and last_i_name != "KW_NAMES":
            # On Python 3.12, CALL is not preceded with a PRECALL
            # Skip, if the last instruction was a KW_NAMES
            inserts[idx] = call_tracer_call_function(tracer_op, i_arg)
        elif i_name == "PRECALL" and last_i_name != "KW_NAMES":
            # On Python 3.11, CALL is preceded with a PRECALL
            # Skip, if the last instruction was a KW_NAMES
            inserts[idx] = call_tracer_call_function(tracer_op, i_arg)
        elif i_name == "BINARY_SUBSCR":
            inserts[idx] = call_tracer_binary_subscr(tracer_op)
        elif i_name == "GET_ITER":
            inserts[idx] = call_tracer_get_iter(tracer_op)
        elif i_name == "RETURN_VALUE":
            inserts[idx] = call_tracer_return_value(tracer_op)
        elif i_name == "RETURN_CONST":
            inserts[idx] = call_tracer_return_const(tracer_op, i_arg)
        elif isinstance(i_arg, CodeType):
            # Inject tracing in nested code object if they use their parent
            # locals.
            inner = bc.Bytecode.from_code(i_arg)
            if not inner.flags & bc.CompilerFlags.NEWLOCALS:
                instr.arg = inject_tracing(inner, nested=True).to_code()

    # Create a new code list which interleaves the generated code with
    # the original code at the appropriate location.
    new_code = bytecode.copy()
    new_code.clear()
    for idx, code_op in enumerate(bytecode):
        if idx in inserts:
            new_code.extend(inserts[idx])
        new_code.append(code_op)

    return new_code

if PY313:
    def call_inverter_load_name(i_arg: int, Instr=bc.Instr):
        return [
            Instr("LOAD_FAST", '_[inverter]'),         # inverter
            Instr("LOAD_ATTR", (False, 'load_name')),  # invertfunc
            Instr("PUSH_NULL"),                        # inverterfunc -> null
            Instr("LOAD_CONST", i_arg),                # invertfunc -> null -> name
            Instr("LOAD_FAST", '_[value]'),            # invertfunc -> null -> name - > value
            Instr("CALL", 0x0002),                     # retval
            Instr("RETURN_VALUE"),                     #
        ]

    def call_inverter_load_attr(i_arg: int, Instr=bc.Instr):
        return [                                       # obj
            Instr("LOAD_FAST", '_[inverter]'),         # obj -> inverter
            Instr("LOAD_ATTR", (False, 'load_attr')),  # obj -> invertfunc
            Instr("SWAP", 2),                          # invertfunc -> obj
            Instr("PUSH_NULL"),                        # invertfunc -> obj -> null
            Instr("SWAP", 2),                          # invertfunc -> null -> obj
            Instr("LOAD_CONST", i_arg),                # invertfunc -> null -> obj -> attr
            Instr("LOAD_FAST", '_[value]'),            # invertfunc -> null -> obj -> attr -> value
            Instr("CALL", 0x0003),                     # retval
            Instr("RETURN_VALUE"),                     #
        ]

    def call_inverter_call_function(i_arg: int, Instr=bc.Instr):
        # n_stack_args = i_arg
        return [                                           # func -> null -> arg(0) -> arg(1) -> ... -> arg(n-1)
            Instr("BUILD_TUPLE", i_arg),                   # func -> null -> argtuple
            Instr("LOAD_FAST", '_[inverter]'),             # func -> null -> argtuple -> inverter
            Instr("LOAD_ATTR", (False, 'call_function')),  # func -> null -> argtuple -> invertfunc
            Instr("SWAP", 4),                              # invertfunc -> null -> argtuple -> func
            Instr("SWAP", 2),                              # invertfunc -> null -> func -> argtuple
            Instr("LOAD_CONST", i_arg),                    # invertfunc -> null -> func -> argtuple -> argspec
            Instr("LOAD_FAST", '_[value]'),                # invertfunc -> null -> func -> argtuple -> argspec -> value
            Instr("CALL", 0x0004),                         # retval
            Instr("RETURN_VALUE"),                         #
        ]

    def call_inverter_binary_subsrc(Instr=bc.Instr):
        return [                                           # obj -> index
            Instr("PUSH_NULL"),                            # obj -> index -> null
            Instr("SWAP", 2),                              # obj -> null -> index
            Instr("LOAD_FAST", '_[inverter]'),             # obj -> null -> index -> inverter
            Instr("LOAD_ATTR", (False, 'binary_subscr')),  # obj -> null -> index -> invertfunc
            Instr("SWAP", 4),                              # invertfunc -> null -> index ->  obj
            Instr("SWAP", 2),                              # invertfunc -> null ->  obj -> index
            Instr("LOAD_FAST", '_[value]'),                # invertfunc -> null ->  obj -> index -> value
            Instr("CALL", 0x0003),                         # retval
            Instr("RETURN_VALUE"),                         #
        ]
elif PY312:
    def call_inverter_load_name(i_arg: int, Instr=bc.Instr):
        return [
            Instr("PUSH_NULL"),                        # null -> inverter
            Instr("LOAD_FAST", '_[inverter]'),         # null -> inverter
            Instr("LOAD_ATTR", (False, 'load_name')),  # null -> invertfunc
            Instr("LOAD_CONST", i_arg),                # null -> invertfunc -> name
            Instr("LOAD_FAST", '_[value]'),            # null -> invertfunc -> name - > value
            Instr("CALL", 0x0002),                     # retval
            Instr("RETURN_VALUE"),                     #
        ]

    def call_inverter_load_attr(i_arg: int, Instr=bc.Instr):
        return [                                       # obj
            Instr("PUSH_NULL"),                        # obj -> null
            Instr("SWAP", 2),                          # null -> obj
            Instr("LOAD_FAST", '_[inverter]'),         # null -> obj -> inverter
            Instr("LOAD_ATTR", (False, 'load_attr')),  # null -> obj -> invertfunc
            Instr("SWAP", 2),                          # null -> invertfunc -> obj
            Instr("LOAD_CONST", i_arg),                # null -> invertfunc -> obj -> attr
            Instr("LOAD_FAST", '_[value]'),            # null -> invertfunc -> obj -> attr -> value
            Instr("CALL", 0x0003),                     # retval
            Instr("RETURN_VALUE"),                     #
        ]

    def call_inverter_call_function(i_arg: int, Instr=bc.Instr):
        # n_stack_args = i_arg
        return [                                           # func -> arg(0) -> arg(1) -> ... -> arg(n-1)
            Instr("BUILD_TUPLE", i_arg),                   # func -> argtuple
            Instr("PUSH_NULL"),                            # func -> argtuple -> null
            Instr("SWAP", 3),                              # null -> argtuple -> func
            Instr("LOAD_FAST", '_[inverter]'),             # null -> argtuple -> func -> inverter
            Instr("LOAD_ATTR", (False, 'call_function')),  # null -> argtuple -> func -> invertfunc
            Instr("SWAP", 3),                              # null -> invertfunc -> func -> argtuple
            Instr("LOAD_CONST", i_arg),                    # null -> invertfunc -> func -> argtuple -> argspec
            Instr("LOAD_FAST", '_[value]'),                # null -> invertfunc -> func -> argtuple -> argspec -> value
            Instr("CALL", 0x0004),                         # retval
            Instr("RETURN_VALUE"),                         #
        ]

    def call_inverter_binary_subsrc(Instr=bc.Instr):
        return [                                           # obj -> index
            Instr("PUSH_NULL"),                            # obj -> index -> null
            Instr("SWAP", 3),                              # null -> index -> obj
            Instr("LOAD_FAST", '_[inverter]'),             # null -> index -> obj -> inverter
            Instr("LOAD_ATTR", (False, 'binary_subscr')),  # null -> index -> obj -> invertfunc
            Instr("SWAP", 3),                              # null -> invertfunc -> obj -> index
            Instr("LOAD_FAST", '_[value]'),                # null -> invertfunc -> obj -> index -> value
            Instr("CALL", 0x0003),                         # retval
            Instr("RETURN_VALUE"),                         #
        ]
elif PY311:
    def call_inverter_load_name(i_arg: int, Instr=bc.Instr):
        return [
            Instr("PUSH_NULL"),                    # null -> inverter
            Instr("LOAD_FAST", '_[inverter]'),     # null -> inverter
            Instr("LOAD_ATTR", 'load_name'),       # null -> invertfunc
            Instr("LOAD_CONST", i_arg),            # null -> invertfunc -> name
            Instr("LOAD_FAST", '_[value]'),        # null -> invertfunc -> name - > value
            Instr("PRECALL", 0x0002),
            Instr("CALL", 0x0002),                 # retval
            Instr("RETURN_VALUE"),                 #
        ]

    def call_inverter_load_attr(i_arg: int, Instr=bc.Instr):
        return [                                   # obj
            Instr("PUSH_NULL"),                    # obj -> null
            Instr("SWAP", 2),                      # null -> obj
            Instr("LOAD_FAST", '_[inverter]'),     # null -> obj -> inverter
            Instr("LOAD_ATTR", 'load_attr'),       # null -> obj -> invertfunc
            Instr("SWAP", 2),                      # null -> invertfunc -> obj
            Instr("LOAD_CONST", i_arg),            # null -> invertfunc -> obj -> attr
            Instr("LOAD_FAST", '_[value]'),        # null -> invertfunc -> obj -> attr -> value
            Instr("PRECALL", 0x0003),              #
            Instr("CALL", 0x0003),                 # retval
            Instr("RETURN_VALUE"),                 #
        ]

    def call_inverter_call_function(i_arg: int, Instr=bc.Instr):
        # n_stack_args = i_arg
        return [                                   # func -> arg(0) -> arg(1) -> ... -> arg(n-1)
            Instr("BUILD_TUPLE", i_arg),           # func -> argtuple
            Instr("PUSH_NULL"),                    # func -> argtuple -> null
            Instr("SWAP", 3),                      # null -> argtuple -> func
            Instr("LOAD_FAST", '_[inverter]'),     # null -> argtuple -> func -> inverter
            Instr("LOAD_ATTR", 'call_function'),   # null -> argtuple -> func -> invertfunc
            Instr("SWAP", 3),                      # null -> invertfunc -> func -> argtuple
            Instr("LOAD_CONST", i_arg),            # null -> invertfunc -> func -> argtuple -> argspec
            Instr("LOAD_FAST", '_[value]'),        # null -> invertfunc -> func -> argtuple -> argspec -> value
            Instr("PRECALL", 0x0004),
            Instr("CALL", 0x0004),                 # retval
            Instr("RETURN_VALUE"),                 #
        ]

    def call_inverter_binary_subsrc(Instr=bc.Instr):
        return [                                   # obj -> index
            Instr("PUSH_NULL"),                    # obj -> index -> null
            Instr("SWAP", 3),                      # null -> index -> obj
            Instr("LOAD_FAST", '_[inverter]'),     # null -> index -> obj -> inverter
            Instr("LOAD_ATTR", 'binary_subscr'),   # null -> index -> obj -> invertfunc
            Instr("SWAP", 3),                      # null -> invertfunc -> obj -> index
            Instr("LOAD_FAST", '_[value]'),        # null -> invertfunc -> obj -> index -> value
            Instr("PRECALL", 0x0003),              #
            Instr("CALL", 0x0003),                 # retval
            Instr("RETURN_VALUE"),                 #
        ]
else:
    def call_inverter_load_name(i_arg: int, Instr=bc.Instr):
        return [
            Instr("LOAD_FAST", '_[inverter]'),     # inverter
            Instr("LOAD_ATTR", 'load_name'),       # invertfunc
            Instr("LOAD_CONST", i_arg),            # invertfunc -> name
            Instr("LOAD_FAST", '_[value]'),        # invertfunc -> name - > value
            Instr("CALL_FUNCTION", 0x0002),        # retval
            Instr("RETURN_VALUE"),                 #
        ]

    def call_inverter_load_attr(i_arg: int, Instr=bc.Instr):
        return [                                   # obj
            Instr("LOAD_FAST", '_[inverter]'),     # obj -> inverter
            Instr("LOAD_ATTR", 'load_attr'),       # obj -> invertfunc
            Instr("ROT_TWO"),                      # invertfunc -> obj
            Instr("LOAD_CONST", i_arg),            # invertfunc -> obj -> attr
            Instr("LOAD_FAST", '_[value]'),        # invertfunc -> obj -> attr -> value
            Instr("CALL_FUNCTION", 0x0003),        # retval
            Instr("RETURN_VALUE"),                 #
        ]

    def call_inverter_call_function(i_arg: int, Instr=bc.Instr):
        # n_stack_args = i_arg
        return [                                   # func -> arg(0) -> arg(1) -> ... -> arg(n-1)
            Instr("BUILD_TUPLE", i_arg),           # func -> argtuple
            Instr("LOAD_FAST", '_[inverter]'),     # func -> argtuple -> inverter
            Instr("LOAD_ATTR", 'call_function'),   # func -> argtuple -> invertfunc
            Instr("ROT_THREE"),                    # invertfunc -> func -> argtuple
            Instr("LOAD_CONST", i_arg),            # invertfunc -> func -> argtuple -> argspec
            Instr("LOAD_FAST", '_[value]'),        # invertfunc -> func -> argtuple -> argspec -> value
            Instr("CALL_FUNCTION", 0x0004),        # retval
            Instr("RETURN_VALUE"),                 #
        ]

    def call_inverter_binary_subsrc(Instr=bc.Instr):
        return [                                   # obj -> index
            Instr("LOAD_FAST", '_[inverter]'),     # obj -> index -> inverter
            Instr("LOAD_ATTR", 'binary_subscr'),   # obj -> index -> invertfunc
            Instr("ROT_THREE"),                    # invertfunc -> obj -> index
            Instr("LOAD_FAST", '_[value]'),        # invertfunc -> obj -> index -> value
            Instr("CALL_FUNCTION", 0x0003),        # retval
            Instr("RETURN_VALUE"),                 #
        ]


def inject_inversion(bytecode):
    """ Inject inversion code into the given bytecode.

    This will inject the bytecode operations required to invert the
    execution of the code using a `CodeInverter` object. The generated
    opcodes expect the fast local '_[inverter]' and '_[value]' to be
    available when the code is executed.

    Parameters
    ----------
    bytecode : bc.Bytecode
        The list of code ops to modify.

    Returns
    -------
    result : list
        A *new* list of code ops which implement the desired behavior.

    Raises
    ------
    ValueError
        The given code is not suitable for inversion.

    """
    instr = bytecode[-2]
    i_name, i_arg = instr.name, instr.arg
    new_code = bytecode[:-2]
    # In Python 3.11 there is a RESUME in the bytecode
    if i_name == "LOAD_NAME" and len(bytecode) >= 2:
        new_code.extend(call_inverter_load_name(i_arg))
    elif i_name == "LOAD_ATTR":
        new_code.extend(call_inverter_load_attr(i_arg[1] if PY312 else i_arg))
    elif i_name == "CALL":
        # In Python 3.11 PRECALL is before CALL (CALL is new in 3.11)
        if not PY312:
            new_code.pop()  # Remove PRECALL
        new_code.extend(call_inverter_call_function(i_arg))
    elif i_name == "CALL_FUNCTION":
        # In Python 3.6+ CALL_FUNCTION is only used for calls with positional arguments
        # and the argument of the opcode is the number of argument on the stack.
        new_code.extend(call_inverter_call_function(i_arg))
    # We do not trace CALL_FUNCTION_KW and CALL_FUNCTION_EX since tracing and
    # inverting only require to detect getattr and setattr both in this project
    # and in traits-enaml. Those two are always called using the CALL_FUNCTION
    # bytecode instruction.
    elif i_name == "BINARY_SUBSCR":
        new_code.extend(call_inverter_binary_subsrc())
    else:
        raise ValueError("can't invert code '%s'" % i_name)

    return new_code
