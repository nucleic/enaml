#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import ast

from .lexer3 import Python36EnamlLexer
from .base_parser import Store, ast_for_testlist, syntax_error, FakeToken
from .parser35 import Python35EnamlParser


class Python36EnamlParser(Python35EnamlParser):
    """Enaml parser supporting Python 3.5 syntax.

    Main differences from 3.5 parser are :

    - support for asynchronous comprehension
    - support for variables annotations (names surrounded by parenthesis are
      considered simple name and not expression as the Python parser does).

    f-strings as added by PEP 498 are not supported in enaml file for the time
    being.

    """
    parser_id = '36'

    lexer = Python36EnamlLexer

    def p_comp_for1(self, p):
        ''' comp_for : FOR exprlist IN or_test '''
        super(Python36EnamlParser, self).p_comp_for1(p)
        p[0][0].is_async = False

    def p_comp_for2(self, p):
        ''' comp_for : FOR exprlist IN or_test comp_iter '''
        super(Python36EnamlParser, self).p_comp_for2(p)
        for g in p[0]:
            g.is_async = False

    def p_comp_async_for1(self, p):
        ''' comp_for : ASYNC FOR exprlist IN or_test '''
        target = p[3]
        self.set_context(target, Store, p)
        p[0] = [ast.comprehension(target=target, iter=p[5], ifs=[],
                                  is_async=True)]

    def p_comp_async_for2(self, p):
        ''' comp_for : ASYNC FOR exprlist IN or_test comp_iter '''
        target = p[3]
        self.set_context(target, Store, p)
        gens = []
        gens.append(ast.comprehension(target=target, iter=p[5], ifs=[],
                                      is_async=True))
        for item in p[6]:
            if isinstance(item, ast.comprehension):
                gens.append(item)
            else:
                gens[-1].ifs.append(item)
        p[0] = gens

    def p_expr_stmt4(self, p):
        ''' expr_stmt : testlist_star_expr annassign '''
        target = ast_for_testlist(p[1])
        if isinstance(target, ast.Name):
            simple = 1
        elif isinstance(target, (ast.Attribute, ast.Subscript)):
            simple = 0
        elif isinstance(target, (ast.Tuple, ast.List)):
            msg = "only single target (not tuple/list) can be annotated"
            syntax_error(msg, FakeToken(p.lexer.lexer, target.lineno))
        else:
            msg = "illegal target for annotation"
            syntax_error(msg, FakeToken(p.lexer.lexer, target.lineno))
        self.set_context(target, Store, p)
        assg = ast.AnnAssign()
        assg.target = target
        assg.annotation, assg.value = p[2]
        # simple is set to 1 for simple names (without parentheses) and is used
        # to know if the annotation should be stored on module or class. As
        # this analysis is painful we consider all ast.Name nodes as simple.
        assg.simple = simple
        p[0] = assg

    def p_annassign1(self, p):
        ''' annassign : COLON test '''
        p[0] = (p[2], None)

    def p_annassign(self, p):
        ''' annassign : COLON test EQUAL test '''
        p[0] = (p[2], p[4])
