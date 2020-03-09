#------------------------------------------------------------------------------
# Copyright (c) 2013-2017, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#------------------------------------------------------------------------------
import ast

from .base_lexer import syntax_error
from .lexer3 import Python36EnamlLexer
from .base_parser import Store, ast_for_testlist, syntax_error, FakeToken
from .parser35 import Python35EnamlParser


class Python36EnamlParser(Python35EnamlParser):
    """Enaml parser supporting Python 3.5 syntax.

    Main differences from 3.5 parser are :

    - support for asynchronous comprehension
    - support for variables annotations (names surrounded by parenthesis are
      considered simple name and not expression as the Python parser does).

    """
    parser_id = '36'

    lexer = Python36EnamlLexer

    def p_comp_for1(self, p):
        ''' comp_for : FOR exprlist IN or_test '''
        super(Python36EnamlParser, self).p_comp_for1(p)
        p[0][0].is_async = 0

    def p_comp_for2(self, p):
        ''' comp_for : FOR exprlist IN or_test comp_iter '''
        super(Python36EnamlParser, self).p_comp_for2(p)
        for g in p[0]:
            g.is_async = 0

    def p_comp_async_for1(self, p):
        ''' comp_for : ASYNC FOR exprlist IN or_test '''
        target = p[3]
        self.set_context(target, Store, p)
        p[0] = [ast.comprehension(target=target, iter=p[5], ifs=[],
                                  is_async=1)]

    def p_comp_async_for2(self, p):
        ''' comp_for : ASYNC FOR exprlist IN or_test comp_iter '''
        target = p[3]
        self.set_context(target, Store, p)
        gens = []
        gens.append(ast.comprehension(target=target, iter=p[5], ifs=[],
                                      is_async=1))
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

    # To avoid re-inventing the parsing of f-strings, we build a list of the
    # multiple strings making the complete string and then re-create pseudo
    # source code that we parse using the ast.parse function of the stdlib.
    # We need to join the different string using spaces to respect the fact
    # that in "(f'{a}' '{r}')" we must not format r.
    def p_atom10(self, p):
        ''' atom : atom_string_list '''
        err_msg = ''
        try:
            m = ast.parse('(' + ' '.join([s for s, _ in p[1]]) + ')')
        except SyntaxError as e:
            err_msg = e.args[0]
            # Identify the line at which the error occurred to get a more
            # accurate line number
            for s, lineno in p[1]:
                try:
                    m = ast.parse(s)
                except SyntaxError:
                    break

        # Avoid getting a triple nesting in the error report that does not
        # bring anything relevant to the traceback.
        if err_msg:
            syntax_error(err_msg, FakeToken(p.lexer.lexer, lineno))

        p[0] = m.body[0].value

    def p_atom_string_list1(self, p):
        ''' atom_string_list : STRING '''
        p[0] = [(repr(p[1]), p.lineno(1))]

    def p_atom_string_list2(self, p):
        ''' atom_string_list : atom_string_list STRING '''
        p[0] = p[1] + [(repr(p[2]), p.lineno(2))]

    def p_atom_string_list3(self, p):
        ''' atom_string_list : FSTRING '''
        p[0] = [('f' + repr(p[1]), p.lineno(1))]

    def p_atom_string_list4(self, p):
        ''' atom_string_list : atom_string_list FSTRING '''
        p[0] = p[1] + [('f' + repr(p[2]), p.lineno(2))]
