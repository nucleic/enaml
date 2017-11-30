#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from ..compat import IS_PY3, USE_WORDCODE
from .byteplay import (
    LOAD_ATTR, LOAD_CONST, ROT_TWO, DUP_TOP, CALL_FUNCTION, POP_TOP, LOAD_FAST,
    BUILD_TUPLE, ROT_THREE, UNPACK_SEQUENCE, BINARY_SUBSCR, GET_ITER,
    LOAD_NAME, RETURN_VALUE
)


from . import byteplay as bp
if not IS_PY3:
    from .byteplay import DUP_TOPX
else:
    from .byteplay import DUP_TOP_TWO

if USE_WORDCODE:
    from .byteplay import CALL_FUNCTION_KW


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

        Parameters
        ----------
        func : object
            The object being called.

        argtuple : tuple
            The argument tuple from the stack (see notes).

        argspec : int
            The argument tuple specification.

        Notes
        -----
        The `argstuple` contains both positional and keyword argument
        information. `argspec` is an int which specifies how to parse
        the information. The lower 16bits of `argspec` are significant.
        The lowest 8 bits are the number of positional arguments which
        are the first n items in `argtuple`. The second 8 bits are the
        number of keyword arguments which follow the positional args in
        `argtuple` and alternate name -> value. `argtuple` can be parsed
        into a conventional tuple and dict with the following:

            nargs = argspec & 0xFF
            args = argtuple[:nargs]
            kwargs = dict(zip(argtuple[nargs::2], argtuple[nargs+1::2]))

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

        This method should perform an appropriate store operation.

        Parameters
        ----------
        func : object
            The object being called.

        argtuple : tuple
            The argument tuple from the stack (see Notes).

        argspec : int
            The argument tuple specification.

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


def inject_tracing(codelist, nested=False):
    """ Inject tracing code into the given code list.

    This will inject the bytecode operations required to trace the
    execution of the code using a `CodeTracer` object. The generated
    opcodes expect a fast local '_[tracer]' to be available when the
    code is executed.

    Parameters
    ----------
    codelist : list
        The list of byteplay code ops to modify.
    nested : bool
        Is the code modified defined inside an already traced code in which
        case the tracer is in the local namespace and not the fast locals.

    Returns
    -------
    result : list
        A *new* list of code ops which implement the desired behavior.

    """
    # If the code is nested into another already traced code, we need to use
    # LOAD_NAME to access it rather than LOAD_FAST
    tracer_op = LOAD_NAME if nested else LOAD_FAST

    # This builds a mapping of code idx to a list of ops, which are the
    # tracing bytecode instructions which will be inserted into the code
    # object being transformed. The ops assume that a tracer object is
    # available in the fast locals using a non-clashable name. All of
    # the ops have a net-zero effect on the execution stack. Provided
    # that the tracer has no visible side effects, the tracing is
    # transparent.
    inserts = {}
    for idx, (op, op_arg) in enumerate(codelist):
        if op == LOAD_ATTR:
            code = [                        # obj
                (DUP_TOP, None),            # obj -> obj
                (tracer_op, '_[tracer]'),   # obj -> obj -> tracer
                (LOAD_ATTR, 'load_attr'),   # obj -> obj -> tracefunc
                (ROT_TWO, None),            # obj -> tracefunc -> obj
                (LOAD_CONST, op_arg),       # obj -> tracefunc -> obj -> attr
                (CALL_FUNCTION, 0x0002),    # obj -> retval
                (POP_TOP, None),            # obj
            ]
            inserts[idx] = code
        elif op == CALL_FUNCTION:
            # This computes the number of objects on the stack between
            # TOS and the object being called. Only the last 16bits of
            # the op_arg are signifcant. The lowest 8 are the number of
            # positional args on the stack, the upper 8 is the number of
            # kwargs. For kwargs, the number of items on the stack is
            # twice this number since the values on the stack alternate
            # name, value.
            # From Python 3.6, CALL_FUNCTION is only used for positional
            # arguments and the argument is directly the number of arguments
            # on the stack.
            if USE_WORDCODE:
                n_stack_args = op_arg
            else:
                n_stack_args = (op_arg & 0xFF) + 2 * ((op_arg >> 8) & 0xFF)
            code = [                                               # func -> arg(0) -> arg(1) -> ... -> arg(n-1)
                (BUILD_TUPLE, n_stack_args),                       # func -> argtuple
                (DUP_TOP_TWO, None) if IS_PY3 else (DUP_TOPX, 2),  # func -> argtuple -> func -> argtuple
                (tracer_op, '_[tracer]'),                          # func -> argtuple -> func -> argtuple -> tracer
                (LOAD_ATTR, 'call_function'),                      # func -> argtuple -> func -> argtuple -> tracefunc
                (ROT_THREE, None),                                 # func -> argtuple -> tracefunc -> func -> argtuple
                (LOAD_CONST, op_arg),                              # func -> argtuple -> tracefunc -> func -> argtuple -> argspec
                (CALL_FUNCTION, 0x0003),                           # func -> argtuple -> retval
                (POP_TOP, None),                                   # func -> argtuple
                (UNPACK_SEQUENCE, n_stack_args),                   # func -> arg(n-1) -> arg(n-2) -> ... -> arg(0)
                (BUILD_TUPLE, n_stack_args),                       # func -> reversedargtuple
                (UNPACK_SEQUENCE, n_stack_args),                   # func -> arg(0) -> arg(1) -> ... -> arg(n-1)
            ]
            inserts[idx] = code
        elif USE_WORDCODE and op == CALL_FUNCTION_KW:
            # New in Python 3.6.
            # All positional and keywords argument are in order on the stack
            # and the first item is a tuple containing the keywords names.

            # TODO implement
            # This is quite low priority as tracing and inverting is only used
            # to detect getattr and setattr called without keyword arguments
            # both in this project and in traits-enaml. So there are no use
            # case for this at the time being.
            pass
        elif op == BINARY_SUBSCR:
            code = [                                               # obj -> idx
                (DUP_TOP_TWO, None) if IS_PY3 else (DUP_TOPX, 2),  # obj -> idx -> obj -> idx
                (tracer_op, '_[tracer]'),                          # obj -> idx -> obj -> idx -> tracer
                (LOAD_ATTR, 'binary_subscr'),                      # obj -> idx -> obj -> idx -> tracefunc
                (ROT_THREE, None),                                 # obj -> idx -> tracefunc -> obj -> idx
                (CALL_FUNCTION, 0x0002),                           # obj -> idx -> retval
                (POP_TOP, None),                                   # obj -> idx
            ]
            inserts[idx] = code
        elif op == GET_ITER:
            code = [                        # obj
                (DUP_TOP, None),            # obj -> obj
                (tracer_op, '_[tracer]'),   # obj -> obj -> tracer
                (LOAD_ATTR, 'get_iter'),    # obj -> obj -> tracefunc
                (ROT_TWO, None),            # obj -> tracefunc -> obj
                (CALL_FUNCTION, 0x0001),    # obj -> retval
                (POP_TOP, None),            # obj
            ]
            inserts[idx] = code
        elif op == RETURN_VALUE:
            code = [
                (DUP_TOP, None),                # obj
                (tracer_op, '_[tracer]'),       # obj -> obj -> tracer
                (LOAD_ATTR, 'return_value'),    # obj -> obj -> tracefunc
                (ROT_TWO, None),                # obj -> tracefunc -> obj
                (CALL_FUNCTION, 0x0001),        # obj -> retval
                (POP_TOP, None),                # obj
            ]
            inserts[idx] = code
        elif isinstance(op_arg, bp.Code):
            # Inject tracing in nested code object if they use their parent
            # locals.
            if not op_arg.newlocals:
                op_arg.code = inject_tracing(op_arg.code, nested=True)

    # Create a new code list which interleaves the generated code with
    # the original code at the appropriate location.
    new_code = []
    for idx, code_op in enumerate(codelist):
        if idx in inserts:
            new_code.extend(inserts[idx])
        new_code.append(code_op)

    return new_code


def inject_inversion(codelist):
    """ Inject inversion code into the given code list.

    This will inject the bytecode operations required to invert the
    execution of the code using a `CodeInverter` object. The generated
    opcodes expect the fast local '_[inverter]' and '_[value]' to be
    available when the code is executed.

    Parameters
    ----------
    codelist : list
        The list of byteplay code ops to modify.

    Returns
    -------
    result : list
        A *new* list of code ops which implement the desired behavior.

    Raises
    ------
    ValueError
        The given code is not suitable for inversion.

    """
    opcode, oparg = codelist[-2]
    new_code = codelist[:-2]
    if opcode == LOAD_NAME and len(codelist) == 3:
        new_code.extend([                   #:
            (LOAD_FAST, '_[inverter]'),     #: inverter
            (LOAD_ATTR, 'load_name'),       #: invertfunc
            (LOAD_CONST, oparg),            #: invertfunc -> name
            (LOAD_FAST, '_[value]'),        #: invertfunc -> name - > value
            (CALL_FUNCTION, 0x0002),        #: retval
            (RETURN_VALUE, None),           #:
        ])
    elif opcode == LOAD_ATTR:
        new_code.extend([                   #: obj
            (LOAD_FAST, '_[inverter]'),     #: obj -> inverter
            (LOAD_ATTR, 'load_attr'),       #: obj -> invertfunc
            (ROT_TWO, None),                #: invertfunc -> obj
            (LOAD_CONST, oparg),            #: invertfunc -> obj -> attr
            (LOAD_FAST, '_[value]'),        #: invertfunc -> obj -> attr -> value
            (CALL_FUNCTION, 0x0003),        #: retval
            (RETURN_VALUE, None),           #:
        ])
    elif opcode == CALL_FUNCTION:
        if USE_WORDCODE:
            n_stack_args = oparg
        else:
            n_stack_args = (oparg & 0xFF) + 2 * ((oparg >> 8) & 0xFF)
        new_code.extend([                   #: func -> arg(0) -> arg(1) -> ... -> arg(n-1)
            (BUILD_TUPLE, n_stack_args),    #: func -> argtuple
            (LOAD_FAST, '_[inverter]'),     #: func -> argtuple -> inverter
            (LOAD_ATTR, 'call_function'),   #: func -> argtuple -> invertfunc
            (ROT_THREE, None),              #: invertfunc -> func -> argtuple
            (LOAD_CONST, oparg),            #: invertfunc -> func -> argtuple -> argspec
            (LOAD_FAST, '_[value]'),        #: invertfunc -> func -> argtuple -> argspec -> value
            (CALL_FUNCTION, 0x0004),        #: retval
            (RETURN_VALUE, None),           #:
        ])
    elif USE_WORDCODE and opcode == CALL_FUNCTION_KW:
            # New in Python 3.6.
            # All positional and keywords argument are in order on the stack
            # and the first item is a tuple containing the keywords names.

            # TODO implement
            # This is quite low priority as tracing and inverting is only used
            # to detect getattr and setattr called without keyword arguments
            # both in this project and in traits-enaml. So there are no use
            # case for this at the time being.
            pass
    elif opcode == BINARY_SUBSCR:
        new_code.extend([                   #: obj -> index
            (LOAD_FAST, '_[inverter]'),     #: obj -> index -> inverter
            (LOAD_ATTR, 'binary_subscr'),   #: obj -> index -> invertfunc
            (ROT_THREE, None),              #: invertfunc -> obj -> index
            (LOAD_FAST, '_[value]'),        #: invertfunc -> obj -> index -> value
            (CALL_FUNCTION, 0x0003),        #: retval
            (RETURN_VALUE, None),           #:
        ])
    else:
        raise ValueError("can't invert code")

    return new_code
