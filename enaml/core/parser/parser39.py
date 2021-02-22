#------------------------------------------------------------------------------
# Copyright (c) 2020-2021, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import ast

from .base_parser import Load
from .parser38 import Python38EnamlParser


class Python39EnamlParser(Python38EnamlParser):
    """Enaml parser supporting Python 3.8 syntax.

    Main differences from 3.8 parser are :

    - allow any namedexpr in decoartors
    - handle deprecated ast deprecation Index, ExtSlice

    """
    parser_id = '39'

    # PEP 614, relaxed grammar restrictions on decorators.

    def p_decorator4(self, p):
        ''' decorator : AT namedexpr_test NEWLINE '''
        p[0] = p[1]

    # slice, Index and ExtSlice are considered deprecated and will be removed
    # in future Python versions. value itself should be used instead of
    # Index(value). Tuple(slices, Load()) should be used instead of
    # ExtSlice(slices).

    def p_subscript2(self, p):
        ''' subscript : test '''
        p[0] = p[1]

    def p_subscriptlist2(self, p):
        ''' subscriptlist : subscript COMMA '''
        dims = [p[1]]
        p[0] = ast.Tuple(dims, Load)

    def p_subscriptlist3(self, p):
        ''' subscriptlist : subscript subscriptlist_list '''
        dims = [p[1]] + p[2]
        p[0] = ast.Tuple(dims, Load)

    def p_subscriptlist4(self, p):
        ''' subscriptlist : subscript subscriptlist_list COMMA '''
        dims = [p[1]] + p[2]
        p[0] = ast.Tuple(dims, Load)
