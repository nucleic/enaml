#------------------------------------------------------------------------------
# Copyright (c) 2013, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import ast

from .lexer2 import Python2EnamlLexer
from .base_parser import BaseEnamlParser, Store, FakeToken, syntax_error


class Python2EnamlParser(BaseEnamlParser):
    """Enaml parser supporting Python syntax.

    Main differences from base parser are :
    - support for print and exec statement
    - old style exception raising

    """

    parser_id = '2'

    lexer = Python2EnamlLexer

    def p_small_stmt1(self, p):
        ''' small_stmt : expr_stmt
                       | print_stmt
                       | del_stmt
                       | pass_stmt
                       | flow_stmt
                       | import_stmt
                       | global_stmt
                       | exec_stmt
                       | assert_stmt '''
        p[0] = p[1]

    def p_print_stmt1(self, p):
        ''' print_stmt : PRINT '''
        call = ast.Call()
        call.func = ast.Name(id='print', ctx=ast.Load())
        call.args = []
        call.keywords = []
        call.stargs = None
        call.kwargs = None
        expr = ast.Expr(value=call)
        expr.lineno = p.lineno(1)
        ast.fix_missing_locations(expr)
        p[0] = expr

    def p_print_stmt2(self, p):
        ''' print_stmt : PRINT test '''
        call = ast.Call()
        call.func = ast.Name(id='print', ctx=ast.Load())
        call.args = [p[2]]
        call.keywords = []
        call.stargs = None
        call.kwargs = None
        expr = ast.Expr(value=call)
        expr.lineno = p.lineno(1)
        ast.fix_missing_locations(expr)
        p[0] = expr

    def p_print_stmt3(self, p):
        ''' print_stmt : PRINT print_list '''
        call = ast.Call()
        call.func = ast.Name(id='print', ctx=ast.Load())

        all_values = p[2]
        good_values = [item for item in all_values if item is not None]
        call.args = good_values
        if all_values[-1] is not None:
            call.args.append(ast.Str('\n'))

        call.keywords = []
        call.stargs = None
        call.kwargs = None
        expr = ast.Expr(value=call)
        expr.lineno = p.lineno(1)
        ast.fix_missing_locations(expr)
        p[0] = expr

    def p_print_stmt4(self, p):
        ''' print_stmt : PRINT RIGHTSHIFT test '''
        raise NotImplementedError
        prnt = ast.Print()
        prnt.dest = p[3]
        prnt.values = []
        prnt.nl = True
        p[0] = prnt

    def p_print_stmt5(self, p):
        ''' print_stmt : PRINT RIGHTSHIFT test COMMA test '''
        raise NotImplementedError
        prnt = ast.Print()
        prnt.dest = p[3]
        prnt.values = [p[5]]
        prnt.nl = True
        p[0] = prnt

    def p_print_stmt6(self, p):
        ''' print_stmt : PRINT RIGHTSHIFT test COMMA print_list '''
        raise NotImplementedError
        prnt = ast.Print()
        all_values = p[5]
        good_values = [item for item in all_values if item is not None]
        if all_values[-1] is None:
            nl = False
        else:
            nl = True
        prnt.dest = p[3]
        prnt.values = good_values
        prnt.nl = nl
        p[0] = prnt

    def p_print_list1(self, p):
        ''' print_list : test COMMA '''
        p[0] = [p[1], None]

    def p_print_list2(self, p):
        ''' print_list : test print_list_list '''
        p[0] = [p[1]] + p[2]

    def p_print_list3(self, p):
        ''' print_list : test print_list_list COMMA '''
        p[0] = [p[1]] + p[2] + [None]

    def p_print_list_list1(self, p):
        ''' print_list_list : COMMA test '''
        p[0] = [p[2]]

    def p_print_list_list2(self, p):
        ''' print_list_list : print_list_list COMMA test '''
        p[0] = p[1] + [p[3]]

    def p_exec_stmt1(self, p):
        ''' exec_stmt : EXEC expr '''
        exec_stmt = ast.Exec()
        exec_stmt.body = p[2]
        exec_stmt.globals = None
        exec_stmt.locals = None
        p[0] = exec_stmt

    def p_exec_stmt2(self, p):
        ''' exec_stmt : EXEC expr IN test '''
        exec_stmt = ast.Exec()
        exec_stmt.body = p[2]
        exec_stmt.globals = p[4]
        exec_stmt.locals = None
        p[0] = exec_stmt

    def p_raise_stmt3(self, p):
        ''' raise_stmt : RAISE test COMMA test '''
        raise_stmt = ast.Raise()
        raise_stmt.type = p[2]
        raise_stmt.inst = p[4]
        raise_stmt.tback = None
        p[0] = raise_stmt

    def p_raise_stmt4(self, p):
        ''' raise_stmt : RAISE test COMMA test COMMA test '''
        raise_stmt = ast.Raise()
        raise_stmt.type = p[2]
        raise_stmt.inst = p[4]
        raise_stmt.tback = p[6]
        p[0] = raise_stmt

    # List maker and related are not necessary as even in Python 2
    # testlist_comp was equivalent

    def p_classdef3(self, p):
        ''' classdef : CLASS NAME LPAR testlist RPAR COLON suite '''
        classdef = ast.ClassDef(keywords=[])
        classdef.name = p[2]
        bases = p[4]
        if not isinstance(bases, list):
            bases = [bases]
        classdef.bases = bases
        classdef.body = p[7]
        classdef.decorator_list = []
        classdef.lineno = p.lineno(1)
        ast.fix_missing_locations(classdef)
        p[0] = classdef

    def _make_args(self, args, defaults=[], vararg=None, kwonlyargs=[],
                   kw_defaults=[], kwarg=None):
        """Build an ast node for function arguments.

        """
        if vararg is not None:
            if isinstance(vararg, ast.Name):
                vararg = vararg.id
            else:  # This is a tuple
                msg = "cannot use list as *arg"
                tok = FakeToken(self.lexer.lexer, vararg.lineno)
                syntax_error(msg, tok)

        if kwarg is not None:
            if isinstance(kwarg, ast.Name):
                kwarg = kwarg.id
            else:  # This is a tuple
                msg = "cannot use list as **kwarg"
                tok = FakeToken(self.lexer.lexer, kwarg.lineno)
                syntax_error(msg, tok)

        return ast.arguments(args=args, defaults=defaults, vararg=vararg,
                             kwarg=kwarg)

    def p_fpdef1(self, p):
        ''' fpdef : NAME '''
        p[0] = ast.Name(id=p[1], ctx=ast.Param(), lineno=p.lineno(1))

    def p_fpdef2(self, p):
        ''' fpdef : LPAR fplist RPAR '''
        # fplist will return a NAME or a TUPLE, so we don't need that
        # logic here.
        p[0] = p[2]

    def p_fplist1(self, p):
        ''' fplist : fpdef '''
        p[0] = p[1]

    def p_fplist2(self, p):
        ''' fplist : fpdef COMMA '''
        tup = ast.Tuple()
        tup.elts = [p[1]]
        self.set_context(tup, Store, p)
        p[0] = tup

    def p_fplist3(self, p):
        ''' fplist : fpdef fplist_list '''
        elts = [p[1]] + p[2]
        tup = ast.Tuple()
        tup.elts = elts
        self.set_context(tup, Store, p)
        p[0] = tup

    def p_fplist4(self, p):
        ''' fplist : fpdef fplist_list COMMA '''
        elts = [p[1]] + p[2]
        tup = ast.Tuple()
        tup.elts = elts
        self.set_context(tup, Store, p)
        p[0] = tup

    def p_fplist_list1(self, p):
        ''' fplist_list : COMMA fpdef '''
        p[0] = [p[2]]

    def p_fplist_list2(self, p):
        ''' fplist_list : fplist_list COMMA fpdef '''
        p[0] = p[1] + [p[3]]
