#------------------------------------------------------------------------------
# Copyright (c) 2020, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import ast

from .base_parser import FakeToken, Store, ast_for_testlist, syntax_error
from .parser36 import Python36EnamlParser


class Python38EnamlParser(Python36EnamlParser):
    """Enaml parser supporting Python 3.8 syntax.

    Main differences from 3.6 parser are :

    - set type_ignore to [] on Module
    - add support for the walrus operator

    """
    parser_id = '38'

    def create_module(self, body, **kwargs):
        """Create a module object with the given body.

        We set type_ignores to [].

        """
        return ast.Module(body=body, type_ignores=[])

    def _make_args(self, args, defaults=[], vararg=None, kwonlyargs=[],
                   kw_defaults=[], kwarg=None, posonlyargs=[]):
        """Build an ast node for function arguments.

        """
        return ast.arguments(posonlyargs=posonlyargs, args=args,
                             defaults=defaults, vararg=vararg,
                             kwonlyargs=kwonlyargs, kw_defaults=kw_defaults,
                             kwarg=kwarg)

    # Python 3.8 started alowing star expr in return and yield
    def p_return_stmt2(self, p):
        ''' return_stmt : RETURN testlist_star_expr '''
        value = ast_for_testlist(p[2])
        ret = ast.Return()
        ret.value = value
        p[0] = ret

    def p_yield_expr2(self, p):
        ''' yield_expr : YIELD testlist_star_expr '''
        value = ast_for_testlist(p[2])
        p[0] = ast.Yield(value=value, lineno=p.lineno(1))

    # This keyword argument needs to be asserted as a NAME, but using NAME
    # here causes ambiguity in the parse tables.
    def p_argument4(self, p):
        ''' argument : test COLONEQUAL test '''
        arg = p[1]
        if not isinstance(arg, ast.Name):
            msg = 'Keyword arg must be a Name.'
            tok = FakeToken(p.lexer.lexer, p.lineno(2))
            syntax_error(msg, tok)
        p[0] = ast.NamedExpr(target=ast.Name(arg.id, ctx=Store),
                                             value=p[3], lineno=p.lineno(2))

    def p_namedexpr_test2(self, p):
        ''' namedexpr_test : test COLONEQUAL test '''
        arg = p[1]
        if not isinstance(arg, ast.Name):
            msg = 'Keyword arg must be a Name.'
            tok = FakeToken(p.lexer.lexer, p.lineno(2))
            syntax_error(msg, tok)
        p[0] = ast.NamedExpr(target=ast.Name(arg.id, ctx=Store),
                             value=p[3], lineno=p.lineno(2))
