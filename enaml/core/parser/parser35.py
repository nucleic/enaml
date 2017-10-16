#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import ast

from .lexer3 import Python35EnamlLexer
from .base_parser import Load
from .parser34 import Python34EnamlParser


class Python35EnamlParser(Python34EnamlParser):
    """Enaml parser supporting Python 3.5 syntax.

    Main differences from base parser are :

    - support for matmult syntax
    - support for async/await syntax

    Notes
    -----
    Because the lexer turn await and async into names outside of async def
    blocks we do not need to check that async for, async with and await are
    used in the proper places. (will break for 3.7)

    """
    parser_id = '35'

    lexer = Python35EnamlLexer

    augassign_table = dict(list(Python34EnamlParser.augassign_table.items()) +
                           [('@=', ast.MatMult())])

    _NOTIFICATION_DISALLOWED =\
        dict(list(Python34EnamlParser._NOTIFICATION_DISALLOWED.items()) +
             [(ast.AsyncFunctionDef, 'async function definition')])

    _DECL_FUNCDEF_DISALLOWED =\
        dict(list(Python34EnamlParser._DECL_FUNCDEF_DISALLOWED.items()) +
             [(ast.AsyncFunctionDef, 'async function definition')])

    def set_call_arguments(self, node, args):
        """Set the arguments for an ast.Call node.

        On Python 3.5+, the starargs and kwargs attributes does not exists
        anymore.

        Parameters
        ----------
        node : ast.Call
            Node was arguments should be set.

        args : Arguments
            Arguments for the function call.

        """
        pos_args = args.args
        if args.starargs:
            pos_args += [ast.Starred(value=args.starargs, ctx=Load)]
        key_args = args.keywords
        if args.kwargs:
            key_args += [ast.keyword(arg=None, value=args.kwargs)]
        node.args = pos_args
        node.keywords = key_args

    def p_test_or_star_new2(self, p):
        ''' test_or_star_new : star_expr '''
        p[0] = p[1]

    def p_augassign(self, p):
        ''' augassign : AMPEREQUAL
                      | CIRCUMFLEXEQUAL
                      | DOUBLESLASHEQUAL
                      | DOUBLESTAREQUAL
                      | LEFTSHIFTEQUAL
                      | MINUSEQUAL
                      | PERCENTEQUAL
                      | PLUSEQUAL
                      | RIGHTSHIFTEQUAL
                      | SLASHEQUAL
                      | STAREQUAL
                      | VBAREQUAL
                      | ATEQUAL '''
        super(Python35EnamlParser, self).p_augassign(p)

    def p_term_op5(self, p):
        ''' term_op : AT factor '''
        p[0] = [ast.MatMult(), p[2]]

    def p_dosm_colon(self, p):
        ''' dosm_colon : DOUBLESTAR expr '''
        p[0] = (None, p[2])

    def p_compound_stmt(self, p):
        ''' compound_stmt : if_stmt
                          | while_stmt
                          | for_stmt
                          | try_stmt
                          | with_stmt
                          | funcdef
                          | classdef
                          | decorated
                          | async_funcdef
                          | async_for_stmt
                          | async_with_stmt '''
        super(Python35EnamlParser, self).p_compound_stmt(p)

    def p_decorated(self, p):
        ''' decorated : decorators funcdef
                      | decorators classdef
                      | decorators async_funcdef'''
        decs = p[1]
        target = p[2]
        target.decorator_list = decs
        p[0] = target

    def p_async_funcdef1(self, p):
        ''' async_funcdef : ASYNC funcdef '''
        async_funcdef = ast.AsyncFunctionDef()
        funcdef = p[2]
        for attr in tuple(funcdef._fields) + ('lineno', 'col_offset'):
            setattr(async_funcdef, attr, getattr(funcdef, attr))
        p[0] = async_funcdef

    def p_async_for_stmt(self, p):
        ''' async_for_stmt : ASYNC for_stmt '''
        async_for = ast.AsyncFor()
        for_node = p[2]
        for attr in tuple(for_node._fields) + ('lineno', 'col_offset'):
            setattr(async_for, attr, getattr(for_node, attr))
        p[0] = async_for

    def p_async_with_stmt(self, p):
        ''' async_with_stmt : ASYNC with_stmt '''
        async_with = ast.AsyncWith()
        with_node = p[2]
        for attr in tuple(with_node._fields) + ('lineno', 'col_offset'):
            setattr(async_with, attr, getattr(with_node, attr))
        p[0] = async_with

    def p_atom_expr3(self, p):
        ''' atom_expr : AWAIT atom '''
        p[0] = ast.Await(value=p[1])

    def p_atom_expr4(self, p):
        ''' atom_expr : AWAIT atom trailer_list '''
        root = p[2]
        for node in p[3]:
            if isinstance(node, ast.Call):
                node.func = root
            elif isinstance(node, ast.Attribute):
                node.value = root
            elif isinstance(node, ast.Subscript):
                node.value = root
            else:
                raise TypeError('Unexpected trailer node: %s' % node)
            root = node
        p[0] = ast.Await(value=node)
