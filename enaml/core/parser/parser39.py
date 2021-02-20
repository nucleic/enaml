#------------------------------------------------------------------------------
# Copyright (c) 2020, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import ast

from .base_parser import FakeToken, Store, ast_for_testlist, syntax_error
from .parser38 import Python38EnamlParser
from ast import Load


class Python39EnamlParser(Python38EnamlParser):
    """Enaml parser supporting Python 3.8 syntax.

    Main differences from 3.8 parser are :

    - allow any namedexpr in decoartors
    - handle deprecated ast deprecation Index, ExtSlice

    """
    parser_id = '39'

    def p_decorator4(self, p):
        ''' decorator : AT namedexpr_test NEWLINE '''
        p[0] = namedexpr_test

    def p_subcript2(self, p):
        ''' subscript : test '''
        p[0] = p[1]

    def p_subscriptlist2(self, p):
        ''' subscriptlist : subscript COMMA '''
        dims = [p[1]]
        p[0] = ast.Tuple(dims, Load())

    def p_subscriptlist3(self, p):
        ''' subscriptlist : subscript subscriptlist_list '''
        dims = [p[1]] + p[2]
        p[0] = ast.Tuple(dims, Load())

    def p_subscriptlist4(self, p):
        ''' subscriptlist : subscript subscriptlist_list COMMA '''
        dims = [p[1]] + p[2]
        p[0] = ast.Tuple(dims, Load())
