# byteplay: CPython assembler/disassembler
# Copyright (C) 2006 Noam Raphael | Version: http://code.google.com/p/byteplay
# Rewritten 2009 Demur Rumed | Version: http://github.com/serprex/byteplay
#                            Screwed the style over, modified stack logic to be more flexible, updated to Python 3
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

__version__ = '0.4'
__all__ = [
    'opmap',
    'opname',
    'opcodes',
    'hasflow',
    'stack_effect',
    'cmp_op',
    'hasarg',
    'hasname',
    'hasjrel',
    'hasjabs',
    'hasjump',
    'haslocal',
    'hascompare',
    'hasfree',
    'hascode',
    'hasconst',
    'Opcode',
    'SetLineno',
    'Label',
    'isopcode',
    'Code']


from sys import version_info
if version_info < (3, 4):
    raise NotImplementedError("Currently only Python versions 3.4 and 3.5 are supported!")

import opcode
from dis import findlabels
from types import CodeType
from enum import Enum


class Opcode(int):
    __str__ = __repr__ = lambda s: opname[s]


opmap = {name.replace('+', '_'): Opcode(code) for name, code in opcode.opmap.items()}
opname = {code: name for name, code in opmap.items()}
opcodes = set(opname)
for cmp_op, hasarg in opmap.items():
    globals()[cmp_op] = hasarg
    __all__.append(cmp_op)
cmp_op = opcode.cmp_op

del __all__

hasarg = {x for x in opcodes if x >= opcode.HAVE_ARGUMENT}
hasconst = {Opcode(x) for x in opcode.hasconst}
hasname = {Opcode(x) for x in opcode.hasname}
hasjrel = {Opcode(x) for x in opcode.hasjrel}
hasjabs = {Opcode(x) for x in opcode.hasjabs}
hasjump = hasjabs | hasjrel
haslocal = {Opcode(x) for x in opcode.haslocal}
hascompare = {Opcode(x) for x in opcode.hascompare}
hasfree = {Opcode(x) for x in opcode.hasfree}
hascode = {MAKE_FUNCTION, MAKE_CLOSURE}

if version_info.minor > 2:
    STOP_CODE = -1
if version_info.minor < 4:
    _se = {
        IMPORT_FROM: 1,
        DUP_TOP: 1,
        LOAD_CONST: 1,
        LOAD_NAME: 1,
        LOAD_GLOBAL: 1,
        LOAD_FAST: 1,
        LOAD_CLOSURE: 1,
        LOAD_DEREF: 1,
        BUILD_MAP: 1,
        LOAD_BUILD_CLASS: 1,
        YIELD_VALUE: 0,
        UNARY_POSITIVE: 0,
        UNARY_NEGATIVE: 0,
        UNARY_NOT: 0,
        UNARY_INVERT: 0,
        GET_ITER: 0,
        LOAD_ATTR: 0,
        IMPORT_NAME: 0,
        ROT_TWO: 0,
        ROT_THREE: 0,
        NOP: 0,
        DELETE_GLOBAL: 0,
        DELETE_NAME: 0,
        DELETE_FAST: 0,
        STORE_LOCALS: 0,
        IMPORT_NAME: -1,
        POP_TOP: -1,
        PRINT_EXPR: -1,
        IMPORT_STAR: -1,
        DELETE_ATTR: -1,
        STORE_DEREF: -1,
        STORE_NAME: -1,
        STORE_GLOBAL: -1,
        STORE_FAST: -1,
        BINARY_POWER: -1,
        BINARY_MULTIPLY: -1,
        BINARY_FLOOR_DIVIDE: -1,
        BINARY_TRUE_DIVIDE: -1,
        BINARY_MODULO: -1,
        BINARY_ADD: -1,
        BINARY_SUBTRACT: -1,
        BINARY_SUBSCR: -1,
        BINARY_LSHIFT: -1,
        BINARY_RSHIFT: -1,
        BINARY_AND: -1,
        BINARY_XOR: -1,
        BINARY_OR: -1,
        COMPARE_OP: -1,
        INPLACE_POWER: -1,
        INPLACE_MULTIPLY: -1,
        INPLACE_FLOOR_DIVIDE: -1,
        INPLACE_TRUE_DIVIDE: -1,
        INPLACE_MODULO: -1,
        INPLACE_ADD: -1,
        INPLACE_SUBTRACT: -1,
        INPLACE_LSHIFT: -1,
        INPLACE_RSHIFT: -1,
        INPLACE_AND: -1,
        INPLACE_XOR: -1,
        INPLACE_OR: -1,
        LIST_APPEND: -1,
        SET_ADD: -1,
        DELETE_SUBSCR: -2,
        STORE_ATTR: -2,
        STORE_MAP: -2,
        MAP_ADD: -2,
        STORE_SUBSCR: -3}
    _rf = {CALL_FUNCTION: lambda x: -((x & 0xFF00) >> 7) - (x & 0xFF),
           CALL_FUNCTION_VAR_KW: lambda x: -((x & 0xFF00) >> 7) - (x & 0xFF) - 2,
           CALL_FUNCTION_VAR: lambda x: -((x & 0xFF00) >> 7 | 1) - (x & 0xFF),
           CALL_FUNCTION_KW: lambda x: -((x & 0xFF00) >> 7 | 1) - (x & 0xFF),
           RAISE_VARARGS: lambda x: x,
           MAKE_FUNCTION: lambda x: x,
           UNPACK_EX: lambda x: (x & 0xFF) + (x >> 8),
           UNPACK_SEQUENCE: lambda x: x - 1,
           MAKE_CLOSURE: lambda x: x - 1,
           BUILD_TUPLE: lambda x: 1 - x,
           BUILD_LIST: lambda x: 1 - x,
           BUILD_SET: lambda x: 1 - x,
           BUILD_SLICE: lambda x: 1 - x}
    if version_info.minor > 1:
        _se[DUP_TOP_TWO] = 2
        _se[DELETE_DEREF] = 0
    else:
        _se[ROT_FOUR] = 0
        _rf[DUP_TOPX] = lambda x: x

    def stack_effect(op, arg=None):
        if op in _se:
            return _se[op]
        if arg is None:
            raise ValueError("%s requires arg" % op)
        if op in _rf:
            return _rf[op](arg)
        raise ValueError("Unknown %s %s" % (op, arg))
else:
    from dis import stack_effect

hasflow = hasjump | {
    POP_BLOCK,
    END_FINALLY,
    BREAK_LOOP,
    RETURN_VALUE,
    RAISE_VARARGS,
    STOP_CODE,
    POP_EXCEPT}

if version_info < (3, 5):
    hasflow |= {WITH_CLEANUP}
else:
    hasflow |= {WITH_CLEANUP_START, WITH_CLEANUP_FINISH, SETUP_ASYNC_WITH}
    coroutine_opcodes = {GET_AWAITABLE, GET_AITER, GET_ANEXT, BEFORE_ASYNC_WITH, SETUP_ASYNC_WITH}


class Label:
    pass


class SetLinenoType:
    def __repr__(self):
        return 'SetLineno'
SetLineno = SetLinenoType()


def isopcode(x):
    return x is not SetLineno and not isinstance(x, Label)


# Flags for codeobject.co_flags, taken from Include/code.h, other flags are no longer used
CO_OPTIMIZED   = 0x0001
CO_NEWLOCALS   = 0x0002
CO_VARARGS     = 0x0004
CO_VARKEYWORDS = 0x0008
CO_NESTED      = 0x0010
CO_GENERATOR   = 0x0020
CO_NOFREE      = 0x0040

if version_info >= (3, 5):
    CO_COROUTINE          = 0x0080
    CO_ITERABLE_COROUTINE = 0x0100

CO_FUTURE_BARRY_AS_BDFL = 0x40000

if version_info >= (3, 5):
    CO_FUTURE_GENERATOR_STOP = 0x80000


class Code(object):
    """An object which holds all the information which a Python code object
    holds, but in an easy-to-play-with representation

    The attributes are:

    Affecting action
    code - list of 2-tuples: the code
    freevars - list of strings: the free vars of the code (those are names
               of variables created in outer functions and used in the function)
    args - list of strings: the arguments of the code
    kwonly - number of keyword only arguments
    varargs - boolean: Does args end with a '*args' argument
    varkwargs - boolean: Does args end with a '**kwargs' argument
    newlocals - boolean: Should a new local namespace be created
                (True in functions, False for module and exec code)

    force_generator - set CO_GENERATOR in co_flags for generator Code objects without generator-specific code
    Python 3.5:
        force_coroutine - set CO_COROUTINE in co_flags for coroutine Code objects (native coroutines) without coroutine-specific code
        force_iterable_coroutine - set CO_ITERABLE_COROUTINE in co_flags for generator-based coroutine Code objects
        future_generator_stop - set CO_FUTURE_GENERATOR_STOP flag (see PEP-479)

    Not affecting action
    name - string: the name of the code (co_name)
    filename - string: the file name of the code (co_filename)
    firstlineno - int: the first line number (co_firstlineno)
    docstring - string or None: the docstring (the first item of co_consts,
                if it's str)

    code is a list of 2-tuples. The first item is an opcode, or SetLineno, or a
    Label instance. The second item is the argument, if applicable, or None"""

    def __init__(self, code, freevars, args, kwonly, varargs, varkwargs, newlocals,
                 name, filename, firstlineno, docstring,
                 force_generator=False,
                 *, force_coroutine=None, force_iterable_coroutine=None, future_generator_stop=None):
        self.code = code
        self.freevars = freevars
        self.args = args
        self.kwonly = kwonly
        self.varargs = varargs
        self.varkwargs = varkwargs
        self.newlocals = newlocals
        self.name = name
        self.filename = filename
        self.firstlineno = firstlineno
        self.docstring = docstring
        self.force_generator = force_generator
        if version_info < (3, 5):
            # Flags unsupported in earlier versions
            assert force_coroutine is None and force_iterable_coroutine is None and future_generator_stop is None
        else:
            self.force_coroutine = bool(force_coroutine)
            self.force_iterable_coroutine = bool(force_iterable_coroutine)
            self.future_generator_stop = bool(future_generator_stop)

    @staticmethod
    def _findlinestarts(code):
        """Find the offsets in a byte code which are start of lines in the source
        Generate pairs offset,lineno as described in Python/compile.c
        This is a modified version of dis.findlinestarts, which allows multiplelinestarts
        with the same line number"""
        lineno = code.co_firstlineno
        addr = 0
        for byte_incr, line_incr in zip(code.co_lnotab[0::2], code.co_lnotab[1::2]):
            if byte_incr:
                yield addr, lineno
                addr += byte_incr
            lineno += line_incr
        yield addr, lineno

    @classmethod
    def from_code(cls, co):
        """Disassemble a Python code object into a Code object"""
        free_cell_isection = set(co.co_cellvars) & set(co.co_freevars)
        if free_cell_isection:
            print(co.co_name + ': has non-empty co.co_cellvars & co.co_freevars', free_cell_isection)
            return None

        co_code = co.co_code
        labels = {addr: Label() for addr in findlabels(co_code)}
        linestarts = dict(cls._findlinestarts(co))
        cellfree = co.co_cellvars + co.co_freevars
        code = []
        n = len(co_code)
        i = extended_arg = 0
        is_generator = False
        if version_info >= (3, 5):
            is_coroutine = False

        while i < n:
            op = Opcode(co_code[i])
            if i in labels:
                code.append((labels[i], None))
            if i in linestarts:
                code.append((SetLineno, linestarts[i]))
            i += 1
            if op in hascode:
                lastop, lastarg = code[-2]
                if lastop != LOAD_CONST:
                    raise ValueError("%s should be preceded by LOAD_CONST" % op)

                sub_code = Code.from_code(lastarg)
                if sub_code is None:
                    print(co.co_name + ': has unexpected subcode block')
                    return None

                code[-2] = (LOAD_CONST, sub_code)
            if op not in hasarg:
                code.append((op, None))
            else:
                arg = co_code[i] | co_code[i + 1] << 8 | extended_arg
                extended_arg = 0
                i += 2
                if op == opcode.EXTENDED_ARG:
                    extended_arg = arg << 16
                else:
                    byteplay_arg = co.co_consts[arg] if op in hasconst else \
                                   co.co_names[arg] if op in hasname else \
                                   labels[arg] if op in hasjabs else \
                                   labels[i + arg] if op in hasjrel else \
                                   co.co_varnames[arg] if op in haslocal else \
                                   cmp_op[arg] if op in hascompare else \
                                   cellfree[arg] if op in hasfree else \
                                   arg
                    code.append((op, byteplay_arg))

            if op == YIELD_VALUE or op == YIELD_FROM:
                is_generator = True

            if version_info >= (3, 5) and op in coroutine_opcodes:
                is_coroutine = True

        varargs = not not co.co_flags & CO_VARARGS
        varkwargs = not not co.co_flags & CO_VARKEYWORDS
        force_generator = not is_generator and (co.co_flags & CO_GENERATOR)

        if version_info >= (3, 5):
            force_coroutine = not is_coroutine and (co.co_flags & CO_COROUTINE)
            force_iterable_coroutine = co.co_flags & CO_ITERABLE_COROUTINE
            assert not (force_coroutine and force_iterable_coroutine)
            future_generator_stop = co.co_flags & CO_FUTURE_GENERATOR_STOP
        else:
            force_coroutine = None
            force_iterable_coroutine =None
            future_generator_stop = None

        return cls(code=code,
                   freevars=co.co_freevars,
                   args=co.co_varnames[:co.co_argcount + varargs + varkwargs + co.co_kwonlyargcount],
                   kwonly=co.co_kwonlyargcount,
                   varargs=varargs,
                   varkwargs=varkwargs,
                   newlocals=not not co.co_flags & CO_NEWLOCALS,
                   name=co.co_name,
                   filename=co.co_filename,
                   firstlineno=co.co_firstlineno,
                   docstring=co.co_consts[0] if co.co_consts and isinstance(co.co_consts[0], str) else None,
                   force_generator=force_generator,
                   force_coroutine=force_coroutine,
                   force_iterable_coroutine=force_iterable_coroutine,
                   future_generator_stop=future_generator_stop)

    def __eq__(self, other):
        try:
            if (self.freevars != other.freevars or
                    self.args != other.args or
                    self.kwonly != other.kwonly or
                    self.varargs != other.varargs or
                    self.varkwargs != other.varkwargs or
                    self.newlocals != other.newlocals or
                    self.name != other.name or
                    self.filename != other.filename or
                    self.firstlineno != other.firstlineno or
                    self.docstring != other.docstring or
                    self.force_generator != other.force_generator or
                    len(self.code) != len(other.code)):
                return False
            elif version_info >= (3, 5):
                if (self.force_coroutine != other.force_coroutine or
                        self.force_iterable_coroutine != other.force_iterable_coroutine or
                        self.future_generator_stop != other.future_generator_stop):
                    return False


            # This isn't trivial due to labels
            lmap = {}
            for (op1, arg1), (op2, arg2) in zip(self.code, other.code):
                if isinstance(op1, Label):
                    if lmap.setdefault(arg1, arg2) is not arg2:
                        return False
                else:
                    if op1 != op2:
                        return False
                    if op1 in hasjump:
                        if lmap.setdefault(arg1, arg2) is not arg2:
                            return False
                    elif arg1 != arg2:
                        return False

            return True
        except:
            return False

    def _compute_stacksize(self, logging=False):
        code = self.code
        label_pos = {op[0]: pos for pos, op in enumerate(code) if isinstance(op[0], Label)}
        # sf_targets are the targets of SETUP_FINALLY opcodes. They are recorded
        # because they have special stack behaviour. If an exception was raised
        # in the block pushed by a SETUP_FINALLY opcode, the block is popped
        # and 3 objects are pushed. On return or continue, the block is popped
        # and 2 objects are pushed. If nothing happened, the block is popped by
        # a POP_BLOCK opcode and 1 object is pushed by a (LOAD_CONST, None)
        # operation
        # Our solution is to record the stack state of SETUP_FINALLY targets
        # as having 3 objects pushed, which is the maximum. However, to make
        # stack recording consistent, the get_next_stacks function will always
        # yield the stack state of the target as if 1 object was pushed, but
        # this will be corrected in the actual stack recording
        if version_info < (3, 5):
            sf_targets = {label_pos[arg] for op, arg in code
                          if (op == SETUP_FINALLY or op == SETUP_WITH)}
        else:
            sf_targets = {label_pos[arg] for op, arg in code
                          if (op == SETUP_FINALLY or op == SETUP_WITH or op == SETUP_ASYNC_WITH)}

        states = [None] * len(code)
        maxsize = 0

        class BlockType(Enum):
            DEFAULT = 0,
            TRY_FINALLY = 1,
            TRY_EXCEPT = 2,
            LOOP_BODY = 3,
            WITH_BLOCK = 4,
            EXCEPTION = 5,
            SILENCED_EXCEPTION_BLOCK = 6,

        class State:

            def __init__(self, pos=0, stack=(0,), block_stack=(BlockType.DEFAULT,), log=[]):
                self._pos = pos
                self._stack = stack
                self._block_stack = block_stack
                self._log = log

            @property
            def pos(self):
                return self._pos

            @property
            def stack(self):
                return self._stack

            @stack.setter
            def stack(self, val):
                self._stack = val

            def newstack(self, n):
                if self._stack[-1] < -n:
                    raise ValueError("Popped a non-existing element at %s %s" %
                                     (self._pos, code[self._pos - 4: self._pos + 3]))
                return self._stack[:-1] + (self._stack[-1] + n,)

            @property
            def block_stack(self):
                return self._block_stack

            @property
            def log(self):
                return self._log

            def newlog(self, msg):
                if not logging:
                    return None

                log_msg = str(self._pos) + ": " + msg
                if self._stack:
                    log_msg += " (on stack: "
                    log_depth = 2
                    log_depth = min(log_depth, len(self._stack))
                    for pos in range(-1, -log_depth, -1):
                        log_msg += str(self._stack[pos]) + ", "
                    log_msg += str(self._stack[-log_depth])
                    log_msg += ")"
                else:
                    log_msg += " (empty stack)"
                return [log_msg] + self._log

        op = [State()]

        while op:
            cur_state = op.pop()
            o = sum(cur_state.stack)
            if o > maxsize:
                maxsize = o

            o, arg = code[cur_state.pos]

            if isinstance(o, Label):
                if cur_state.pos in sf_targets:
                    cur_state.stack = cur_state.newstack(5)
                if states[cur_state.pos] is None:
                    states[cur_state.pos] = cur_state
                elif states[cur_state.pos].stack != cur_state.stack:
                    check_pos = cur_state.pos + 1
                    while code[check_pos][0] not in hasflow:
                        check_pos += 1
                    if code[check_pos][0] not in (RETURN_VALUE, RAISE_VARARGS, STOP_CODE):
                        if cur_state.pos not in sf_targets:
                            raise ValueError("Inconsistent code at %s %s %s\n%s" %
                                             (cur_state.pos, cur_state.stack, states[cur_state.pos].stack,
                                              code[cur_state.pos - 5:cur_state.pos + 4]))
                        else:
                            # SETUP_FINALLY target inconsistent code!
                            #
                            # Since Python 3.2 assigned exception is cleared at the end of
                            # the except clause (named exception handler).
                            # To perform this CPython (checked in version 3.4.3) adds special
                            # bytecode in exception handler which currently breaks 'regularity' of bytecode.
                            # Exception handler is wrapped in try/finally block and POP_EXCEPT opcode
                            # is inserted before END_FINALLY, as a result cleanup-finally block is executed outside
                            # except handler. It's not a bug, as it doesn't cause any problems during execution, but
                            # it breaks 'regularity' and we can't check inconsistency here. Maybe issue should be
                            # posted to Python bug tracker.
                            pass
                    continue
                else:
                    continue

            if o not in (BREAK_LOOP, RETURN_VALUE, RAISE_VARARGS, STOP_CODE):
                next_pos = cur_state.pos + 1

                if not isopcode(o):
                    op += State(next_pos, cur_state.stack, cur_state.block_stack, cur_state.log),

                elif o not in hasflow:
                    if o in (LOAD_GLOBAL, LOAD_CONST, LOAD_NAME, LOAD_FAST, LOAD_ATTR, LOAD_DEREF,
                             LOAD_CLASSDEREF, LOAD_CLOSURE,
                             STORE_GLOBAL, STORE_NAME, STORE_FAST, STORE_ATTR, STORE_DEREF,
                             DELETE_GLOBAL, DELETE_NAME, DELETE_FAST, DELETE_ATTR, DELETE_DEREF,
                             IMPORT_NAME, IMPORT_FROM, COMPARE_OP):
                        se = stack_effect(o, 0)
                    else:
                        se = stack_effect(o, arg)

                    log = cur_state.newlog("non-flow command (" + str(o) + ", se = " + str(se) + ")")
                    op += State(next_pos, cur_state.newstack(se), cur_state.block_stack, log),

                elif o == FOR_ITER:
                    inside_for_log = cur_state.newlog("FOR_ITER (+1)")
                    op += State(label_pos[arg], cur_state.newstack(-1), cur_state.block_stack, cur_state.log),\
                          State(next_pos, cur_state.newstack(1), cur_state.block_stack, inside_for_log)

                elif o in (JUMP_FORWARD, JUMP_ABSOLUTE):
                    after_jump_log = cur_state.newlog(str(o))
                    op += State(label_pos[arg], cur_state.stack, cur_state.block_stack, after_jump_log),

                elif o in (JUMP_IF_FALSE_OR_POP, JUMP_IF_TRUE_OR_POP):
                    after_jump_log = cur_state.newlog(str(o) + ", jumped")
                    log = cur_state.newlog(str(o) + ", not jumped (-1)")
                    op += State(label_pos[arg], cur_state.stack, cur_state.block_stack, after_jump_log),\
                          State(next_pos, cur_state.newstack(-1), cur_state.block_stack, log)

                elif o in {POP_JUMP_IF_TRUE, POP_JUMP_IF_FALSE}:
                    after_jump_log = cur_state.newlog(str(o) + ", jumped (-1)")
                    log = cur_state.newlog(str(o) + ", not jumped (-1)")
                    op += State(label_pos[arg], cur_state.newstack(-1), cur_state.block_stack, after_jump_log),\
                          State(next_pos, cur_state.newstack(-1), cur_state.block_stack, log)

                elif o == CONTINUE_LOOP:
                    next_stack, next_block_stack = cur_state.stack, cur_state.block_stack
                    last_popped_block = None
                    while next_block_stack[-1] != BlockType.LOOP_BODY:
                        last_popped_block = next_block_stack[-1]
                        next_stack, next_block_stack = next_stack[:-1], next_block_stack[:-1]

                    if next_stack != cur_state.stack:
                        log = cur_state.newlog("CONTINUE_LOOP, from non-loop block")
                    else:
                        log = cur_state.newlog("CONTINUE_LOOP")

                    jump_to_pos = label_pos[arg]
                    if last_popped_block == BlockType.WITH_BLOCK:
                        next_stack = next_stack[:-1] + (next_stack[-1] - 1,)
                    op += State(jump_to_pos, next_stack, next_block_stack, log),

                elif o == SETUP_LOOP:
                    inside_loop_log = cur_state.newlog("SETUP_LOOP (+block)")
                    op += State(label_pos[arg], cur_state.stack, cur_state.block_stack, cur_state.log),\
                          State(next_pos, cur_state.stack + (0,), cur_state.block_stack + (BlockType.LOOP_BODY,), inside_loop_log)

                elif o == SETUP_EXCEPT:
                    inside_except_log = cur_state.newlog("SETUP_EXCEPT, exception (+6, +block)")
                    inside_try_log = cur_state.newlog("SETUP_EXCEPT, try-block (+block)")
                    op += State(label_pos[arg], cur_state.stack + (6,), cur_state.block_stack + (BlockType.EXCEPTION,), inside_except_log),\
                          State(next_pos, cur_state.stack + (0,), cur_state.block_stack + (BlockType.TRY_EXCEPT,), inside_try_log)

                elif o == SETUP_FINALLY:
                    inside_finally_block = cur_state.newlog("SETUP_FINALLY (+1)")
                    inside_try_log = cur_state.newlog("SETUP_FINALLY try-block (+block)")
                    op += State(label_pos[arg], cur_state.newstack(1), cur_state.block_stack, inside_finally_block),\
                          State(next_pos, cur_state.stack + (0,), cur_state.block_stack + (BlockType.TRY_FINALLY,), inside_try_log)

                elif o == POP_BLOCK:
                    log = cur_state.newlog("POP_BLOCK (-block)")
                    op += State(next_pos, cur_state.stack[:-1], cur_state.block_stack[:-1], log),

                elif o == POP_EXCEPT:
                    log = cur_state.newlog("POP_EXCEPT (-block)")
                    op += State(next_pos, cur_state.stack[:-1], cur_state.block_stack[:-1], log),

                elif o == END_FINALLY:
                    if cur_state.block_stack[-1] == BlockType.SILENCED_EXCEPTION_BLOCK:
                        log = cur_state.newlog("END_FINALLY pop silenced exception block (-block)")
                        op += State(next_pos, cur_state.stack[:-1], cur_state.block_stack[:-1], log),
                    elif cur_state.block_stack[-1] == BlockType.EXCEPTION:
                        # Reraise exception
                        pass
                    else:
                        log = cur_state.newlog("END_FINALLY (-6)")
                        op += State(next_pos, cur_state.newstack(-6), cur_state.block_stack, log),

                elif o == SETUP_WITH or (version_info >= (3, 5) and o == SETUP_ASYNC_WITH):
                    inside_with_block = cur_state.newlog("SETUP_WITH, with-block (+1, +block)")
                    inside_finally_block = cur_state.newlog("SETUP_WITH, finally (+1)")
                    op += State(label_pos[arg], cur_state.newstack(1), cur_state.block_stack, inside_finally_block),\
                          State(next_pos, cur_state.stack + (1,), cur_state.block_stack + (BlockType.WITH_BLOCK,), inside_with_block)

                elif version_info < (3, 5) and o == WITH_CLEANUP:
                    # There is special case when 'with' __exit__ function returns True,
                    # that's the signal to silence exception, in this case additional element is pushed
                    # and next END_FINALLY command won't reraise exception.
                    log = cur_state.newlog("WITH_CLEANUP (-1)")
                    silenced_exception_log = cur_state.newlog("WITH_CLEANUP silenced_exception (+1, +block)")
                    op += State(next_pos, cur_state.newstack(-1), cur_state.block_stack, log),\
                          State(next_pos, cur_state.newstack(-7) + (8,), cur_state.block_stack + (BlockType.SILENCED_EXCEPTION_BLOCK,), silenced_exception_log)

                elif version_info >= (3, 5) and o == WITH_CLEANUP_START:
                    # There is special case when 'with' __exit__ function returns True,
                    # that's the signal to silence exception, in this case additional element is pushed
                    # and next END_FINALLY command won't reraise exception.
                    # Emulate this situation on WITH_CLEANUP_START with creating special block which will be
                    # handled differently by WITH_CLEANUP_FINISH and will cause END_FINALLY not to reraise exception.
                    log = cur_state.newlog("WITH_CLEANUP_START (+1)")
                    silenced_exception_log = cur_state.newlog("WITH_CLEANUP_START silenced_exception (+block)")
                    op += State(next_pos, cur_state.newstack(1), cur_state.block_stack, log),\
                          State(next_pos, cur_state.newstack(-7) + (9,), cur_state.block_stack + (BlockType.SILENCED_EXCEPTION_BLOCK,), silenced_exception_log)

                elif version_info >= (3, 5) and o == WITH_CLEANUP_FINISH:
                    if cur_state.block_stack[-1] == BlockType.SILENCED_EXCEPTION_BLOCK:
                        # See comment in WITH_CLEANUP_START handler
                        log = cur_state.newlog("WITH_CLEANUP_FINISH silenced_exception (-1)")
                        op += State(next_pos, cur_state.newstack(-1), cur_state.block_stack, log),
                    else:
                        log = cur_state.newlog("WITH_CLEANUP_FINISH (-2)")
                        op += State(next_pos, cur_state.newstack(-2), cur_state.block_stack, log),

                else:
                    raise ValueError("Unhandled opcode %s" % o)

        return maxsize + 6  # for exception raise in deepest place

    def to_code(self, from_function=False):
        """Assemble a Python code object from a Code object"""

        num_fastnames = sum(1 for op, arg in self.code if isopcode(op) and op in haslocal)
        is_function = self.newlocals or num_fastnames > 0 or len(self.args) > 0
        nested = is_function and from_function

        co_flags = {op[0] for op in self.code}

        is_generator = self.force_generator or (YIELD_VALUE in co_flags or YIELD_FROM in co_flags)
        no_free = (not self.freevars) and (not co_flags & hasfree)

        if version_info >= (3, 5):
            is_native_coroutine = bool(self.force_coroutine or (co_flags & coroutine_opcodes))
            assert not (is_native_coroutine and self.force_iterable_coroutine)

        co_flags =\
            (not(STORE_NAME in co_flags or LOAD_NAME in co_flags or DELETE_NAME in co_flags)) |\
            (self.newlocals and CO_NEWLOCALS) |\
            (self.varargs and CO_VARARGS) |\
            (self.varkwargs and CO_VARKEYWORDS) |\
            (is_generator and CO_GENERATOR) |\
            (no_free and CO_NOFREE) |\
            (nested and CO_NESTED)

        if version_info >= (3, 5):
            co_flags |= (is_native_coroutine and CO_COROUTINE) |\
                        (self.force_iterable_coroutine and CO_ITERABLE_COROUTINE) |\
                        (self.future_generator_stop and CO_FUTURE_GENERATOR_STOP)

        co_consts = [self.docstring]
        co_names = []
        co_varnames = list(self.args)
        co_freevars = tuple(self.freevars)

        # Find all cellvars beforehand for two reasons
        # Need the number of them to construct the numeric arg for ops in hasfree
        # Need to put args which are cells in the beginning of co_cellvars
        cellvars = {arg for op, arg in self.code
                    if isopcode(op) and op in hasfree
                    and arg not in co_freevars}
        co_cellvars = [jumps for jumps in self.args if jumps in cellvars]

        def index(seq, item, eq=True, can_append=True):
            for i, x in enumerate(seq):
                if x == item if eq else x is item:
                    return i
            if can_append:
                seq.append(item)
                return len(seq) - 1
            else:
                raise IndexError("Item not found")

        jumps = []
        label_pos = {}
        lastlineno = self.firstlineno
        lastlinepos = 0
        co_code = bytearray()
        co_lnotab = bytearray()

        for i, (op, arg) in enumerate(self.code):
            if isinstance(op, Label):
                label_pos[op] = len(co_code)
            elif op is SetLineno:
                incr_lineno = arg - lastlineno
                incr_pos = len(co_code) - lastlinepos
                lastlineno = arg
                lastlinepos += incr_pos
                if incr_lineno != 0 or incr_pos != 0:
                    while incr_pos > 255:
                        co_lnotab += b"\xFF\0"
                        incr_pos -= 255
                    while incr_lineno > 255:
                        co_lnotab += (0xFF00|incr_pos).to_bytes(2, "little")
                        incr_pos = 0
                        incr_lineno -= 255
                    if incr_pos or incr_lineno:
                        co_lnotab += bytes((incr_pos, incr_lineno))
            elif op == opcode.EXTENDED_ARG:
                self.code[i + 1][1] |= 1 << 32
            elif op not in hasarg:
                co_code.append(op)
            else:
                if op in hasconst:
                    if isinstance(arg, Code) and\
                            i + 2 < len(self.code) and self.code[i + 2][0] in hascode:
                        arg = arg.to_code(from_function=is_function)
                        assert arg is not None
                    arg = index(co_consts, arg, 0)
                elif op in hasname:
                    arg = index(co_names, arg)
                elif op in hasjump:
                    jumps.append((len(co_code), arg))
                    co_code += op.to_bytes(3, "little")
                    continue
                elif op in haslocal:
                    arg = index(co_varnames, arg)
                elif op in hascompare:
                    arg = index(cmp_op, arg, can_append=False)
                elif op in hasfree:
                    try:
                        arg = index(co_freevars, arg, can_append=False) + len(cellvars)
                    except IndexError:
                        arg = index(co_cellvars, arg)
                if arg > 0xFFFF:
                    co_code += (opcode.EXTENDED_ARG | ((arg & 0xFFFF0000) >> 8)).to_bytes(3, "little")
                co_code += (op | (arg << 8)).to_bytes(3, "little")

        for pos, label in jumps:
            jump = label_pos[label]
            if co_code[pos] in hasjrel:
                jump -= pos + 3
            if jump > 0xFFFF:
                raise NotImplementedError("Extended jumps not implemented")
            co_code[pos + 1] = jump & 0xFF
            co_code[pos + 2] = jump >> 8

        co_argcount = len(self.args) - self.varargs - self.varkwargs - self.kwonly
        co_stacksize = self._compute_stacksize()

        return CodeType(co_argcount, self.kwonly, len(co_varnames), co_stacksize, co_flags,
                        bytes(co_code), tuple(co_consts), tuple(co_names), tuple(co_varnames),
                        self.filename, self.name, self.firstlineno, bytes(co_lnotab), co_freevars,
                        tuple(co_cellvars))
