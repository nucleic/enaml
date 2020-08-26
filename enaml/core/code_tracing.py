#------------------------------------------------------------------------------
# Copyright (c) 2013-2019, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
from types import CodeType

import bytecode as bc


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
        """ Called before the CALL_FUNCTION opcode is executed.

        The CALL_FUNCTION is only used for function call with only positional
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
    for idx, instr in enumerate(bytecode):
        # Filter out SetLineno and Label
        if not isinstance(instr, bc.Instr):
            continue
        i_name = instr.name
        i_arg = instr.arg
        if i_name == "LOAD_ATTR":
            tracing_code = [                           # obj
                bc.Instr("DUP_TOP"),                   # obj -> obj
                bc.Instr(tracer_op, '_[tracer]'),      # obj -> obj -> tracer
                bc.Instr("LOAD_ATTR", 'load_attr'),    # obj -> obj -> tracefunc
                bc.Instr("ROT_TWO"),                   # obj -> tracefunc -> obj
                bc.Instr("LOAD_CONST", i_arg),         # obj -> tracefunc -> obj -> attr
                bc.Instr("CALL_FUNCTION", 0x0002),     # obj -> retval
                bc.Instr("POP_TOP"),                   # obj
            ]
            inserts[idx] = tracing_code
        elif i_name == "CALL_FUNCTION":
            # From Python 3.6, CALL_FUNCTION is only used for positional
            # arguments and the argument is directly the number of arguments
            # on the stack.
            n_stack_args = i_arg
            tracing_code = [                                         # func -> arg(0) -> arg(1) -> ... -> arg(n-1)
                bc.Instr("BUILD_TUPLE", n_stack_args),       # func -> argtuple
                bc.Instr("DUP_TOP_TWO"),                     # func -> argtuple -> func -> argtuple
                bc.Instr(tracer_op, '_[tracer]'),            # func -> argtuple -> func -> argtuple -> tracer
                bc.Instr("LOAD_ATTR", 'call_function'),      # func -> argtuple -> func -> argtuple -> tracefunc
                bc.Instr("ROT_THREE"),                       # func -> argtuple -> tracefunc -> func -> argtuple
                bc.Instr("LOAD_CONST", i_arg),               # func -> argtuple -> tracefunc -> func -> argtuple -> argspec
                bc.Instr("CALL_FUNCTION", 0x0003),           # func -> argtuple -> retval
                bc.Instr("POP_TOP"),                         # func -> argtuple
                bc.Instr("UNPACK_SEQUENCE", n_stack_args),   # func -> arg(n-1) -> arg(n-2) -> ... -> arg(0)
                bc.Instr("BUILD_TUPLE", n_stack_args),       # func -> reversedargtuple
                bc.Instr("UNPACK_SEQUENCE", n_stack_args),   # func -> arg(0) -> arg(1) -> ... -> arg(n-1)
            ]
            inserts[idx] = tracing_code

        # We do not trace CALL_FUNCTION_KW and CALL_FUNCTION_EX since
        # tracing and inverting only require to detect getattr and setattr
        # both in this project and in traits-enaml. Those two are always called
        # using the CALL_FUNCTION bytecode instruction.

        elif i_name == "BINARY_SUBSCR":
            tracing_code = [                                     # obj -> idx
                bc.Instr("DUP_TOP_TWO"),                 # obj -> idx -> obj -> idx
                bc.Instr(tracer_op, '_[tracer]'),        # obj -> idx -> obj -> idx -> tracer
                bc.Instr("LOAD_ATTR", 'binary_subscr'),  # obj -> idx -> obj -> idx -> tracefunc
                bc.Instr("ROT_THREE"),                   # obj -> idx -> tracefunc -> obj -> idx
                bc.Instr("CALL_FUNCTION", 0x0002),       # obj -> idx -> retval
                bc.Instr("POP_TOP"),                     # obj -> idx
            ]
            inserts[idx] = tracing_code
        elif i_name == "GET_ITER":
            tracing_code = [                               # obj
                bc.Instr("DUP_TOP"),               # obj -> obj
                bc.Instr(tracer_op, '_[tracer]'),  # obj -> obj -> tracer
                bc.Instr("LOAD_ATTR", 'get_iter'), # obj -> obj -> tracefunc
                bc.Instr("ROT_TWO"),               # obj -> tracefunc -> obj
                bc.Instr("CALL_FUNCTION", 0x0001), # obj -> retval
                bc.Instr("POP_TOP"),               # obj
            ]
            inserts[idx] = tracing_code
        elif i_name == "RETURN_VALUE":
            tracing_code = [
                bc.Instr("DUP_TOP"),                   # obj
                bc.Instr(tracer_op, '_[tracer]'),      # obj -> obj -> tracer
                bc.Instr("LOAD_ATTR", 'return_value'), # obj -> obj -> tracefunc
                bc.Instr("ROT_TWO"),                   # obj -> tracefunc -> obj
                bc.Instr("CALL_FUNCTION", 0x0001),     # obj -> retval
                bc.Instr("POP_TOP"),                   # obj
            ]
            inserts[idx] = tracing_code
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
    if i_name == "LOAD_NAME" and len(bytecode) == 2:
        new_code.extend([                             #
            bc.Instr("LOAD_FAST", '_[inverter]'),     # inverter
            bc.Instr("LOAD_ATTR", 'load_name'),       # invertfunc
            bc.Instr("LOAD_CONST", i_arg),            # invertfunc -> name
            bc.Instr("LOAD_FAST", '_[value]'),        # invertfunc -> name - > value
            bc.Instr("CALL_FUNCTION", 0x0002),        # retval
           bc.Instr ("RETURN_VALUE"),                 #
        ])
    elif i_name == "LOAD_ATTR":
        new_code.extend([                   # obj
            bc.Instr("LOAD_FAST", '_[inverter]'),     # obj -> inverter
            bc.Instr("LOAD_ATTR", 'load_attr'),       # obj -> invertfunc
            bc.Instr("ROT_TWO"),                      # invertfunc -> obj
            bc.Instr("LOAD_CONST", i_arg),            # invertfunc -> obj -> attr
            bc.Instr("LOAD_FAST", '_[value]'),        # invertfunc -> obj -> attr -> value
            bc.Instr("CALL_FUNCTION", 0x0003),        # retval
            bc.Instr("RETURN_VALUE"),                 #
        ])

    # In Python 3.6+ CALL_FUNCTION is only used for calls with positional arguments
    # and the argument of the opcode is teh number of argument on the stack.
    elif i_name == "CALL_FUNCTION":
        n_stack_args = i_arg
        new_code.extend([                             # func -> arg(0) -> arg(1) -> ... -> arg(n-1)
            bc.Instr("BUILD_TUPLE", n_stack_args),    # func -> argtuple
            bc.Instr("LOAD_FAST", '_[inverter]'),     # func -> argtuple -> inverter
            bc.Instr("LOAD_ATTR", 'call_function'),   # func -> argtuple -> invertfunc
            bc.Instr("ROT_THREE"),                    # invertfunc -> func -> argtuple
            bc.Instr("LOAD_CONST", i_arg),            # invertfunc -> func -> argtuple -> argspec
            bc.Instr("LOAD_FAST", '_[value]'),        # invertfunc -> func -> argtuple -> argspec -> value
            bc.Instr("CALL_FUNCTION", 0x0004),        # retval
            bc.Instr("RETURN_VALUE"),                 #
        ])

    # We do not trace CALL_FUNCTION_KW and CALL_FUNCTION_EX since tracing and
    # inverting only require to detect getattr and setattr both in this project
    # and in traits-enaml. Those two are always called using the CALL_FUNCTION
    # bytecode instruction.

    elif i_name == "BINARY_SUBSCR":
        new_code.extend([                             # obj -> index
            bc.Instr("LOAD_FAST", '_[inverter]'),     # obj -> index -> inverter
            bc.Instr("LOAD_ATTR", 'binary_subscr'),   # obj -> index -> invertfunc
            bc.Instr("ROT_THREE"),                    # invertfunc -> obj -> index
            bc.Instr("LOAD_FAST", '_[value]'),        # invertfunc -> obj -> index -> value
            bc.Instr("CALL_FUNCTION", 0x0003),        # retval
            bc.Instr("RETURN_VALUE"),                 #
        ])
    else:
        raise ValueError("can't invert code")

    return new_code
