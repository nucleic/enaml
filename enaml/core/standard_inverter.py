#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
from .code_tracing import CodeInverter


class StandardInverter(CodeInverter):
    """ The standard code inverter for Enaml expressions.

    """
    __slots__ = '_nonlocals'

    def __init__(self, nonlocals):
        """ Initialize a StandardInverter.

        Parameters
        ----------
        nonlocals : Nonlocals
            The nonlocal scope for the executing expression.

        """
        self._nonlocals = nonlocals

    #--------------------------------------------------------------------------
    # CodeInverter Interface
    #--------------------------------------------------------------------------
    def load_name(self, name, value):
        """ Called before the LOAD_NAME opcode is executed.

        This method performs STORE_NAME by storing to the nonlocals.
        See also: `CodeInverter.load_name`.

        """
        self._nonlocals[name] = value

    def load_attr(self, obj, attr, value):
        """ Called before the LOAD_ATTR opcode is executed.

        This method performs STORE_ATTR via the builtin `setattr`.
        See also: `CodeInverter.load_attr`.

        """
        setattr(obj, attr, value)

    def call_function(self, func, argtuple, argspec, value):
        """ Called before the CALL_FUNCTION opcode is executed.

        This method inverts a call to the builtin `getattr` into a call
        to the builtin `setattr`. All other calls will raise.
        See also: `CodeInverter.call_function`.

        """
        nargs = argspec & 0xFF
        nkwargs = (argspec >> 8) & 0xFF
        if (func is getattr and (nargs == 2 or nargs == 3) and nkwargs == 0):
            obj, attr = argtuple[0], argtuple[1]
            setattr(obj, attr, value)
        else:
            self.fail()

    def binary_subscr(self, obj, idx, value):
        """ Called before the BINARY_SUBSCR opcode is executed.

        This method performs a STORE_SUBSCR operation through standard
        setitem semantics. See also: `CodeInverter.binary_subscr`.

        """
        obj[idx] = value

