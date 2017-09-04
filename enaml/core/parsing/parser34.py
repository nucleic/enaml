#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import ast

from .lexer3 import Python34EnamlLexer
from .parser3 import Python3EnamlParser


class Python34EnamlParser(Python3EnamlParser):
    """Enaml parser supporting Python 3.4 syntax.

    """
    parser_id = '34'

    lexer = Python34EnamlLexer

    def p_atom13(self, p):
        ''' atom : NONE '''
        p[0] = ast.NameConstant(None)

    def p_atom14(self, p):
        ''' atom : FALSE '''
        p[0] = ast.NameConstant(False)

    def p_atom15(self, p):
        ''' atom : TRUE '''
        p[0] = ast.NameConstant(True)

    def _make_args(self, args, defaults=[], vararg=None, kwonlyargs=[],
                   kw_defaults=[], kwarg=None):
        """Build an ast node for function arguments.

        """
        return ast.arguments(args=args, defaults=defaults, vararg=vararg,
                             kwonlyargs=kwonlyargs, kw_defaults=kw_defaults,
                             kwarg=kwarg)
