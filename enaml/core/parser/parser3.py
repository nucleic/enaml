#------------------------------------------------------------------------------
# Copyright (c) 2013-2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import ast
from types import FunctionType

from .. import enaml_ast
from .base_lexer import syntax_error
from .base_parser import BaseEnamlParser, FakeToken, ast_for_testlist, Load
from .lexer3 import Python3EnamlLexer


class Python3EnamlParser(BaseEnamlParser):
    """Enaml parser supporting Python syntax.

    Main differences from base parser are :

    - support for annotation in function declaration
    - support for raise from syntax
    - support for yield from syntax

    """
    parser_id = '3'

    lexer = Python3EnamlLexer

    context_allowed = set(list(BaseEnamlParser.context_allowed) +
                          [ast.Starred])

    def set_context(self, node, ctx, p):
        """Properly set the context of ast.Starred.

        """
        super(Python3EnamlParser, self).set_context(node, ctx, p)
        if( isinstance(node, ast.Starred) and
                type(node.value) in self.context_allowed):
            self.set_context(node.value, ctx, p)

    def p_decl_funcdef3(self, p):
        ''' decl_funcdef : NAME NAME parameters RETURNARROW test COLON suite '''
        lineno = p.lineno(1)
        if p[1] != 'func':
            syntax_error('invalid syntax', FakeToken(p.lexer.lexer, lineno))
        funcdef = ast.FunctionDef()
        funcdef.name = p[2]
        funcdef.args = p[3]
        funcdef.returns = p[5]
        funcdef.body = p[7]
        funcdef.decorator_list = []
        funcdef.lineno = lineno
        ast.fix_missing_locations(funcdef)
        self._validate_decl_funcdef(funcdef, p.lexer.lexer)
        decl_funcdef = enaml_ast.FuncDef()
        decl_funcdef.lineno = lineno
        decl_funcdef.funcdef = funcdef
        decl_funcdef.is_override = False
        p[0] = decl_funcdef

    def p_small_stmt1(self, p):
        ''' small_stmt : expr_stmt
                       | del_stmt
                       | pass_stmt
                       | flow_stmt
                       | import_stmt
                       | global_stmt
                       | assert_stmt
                       | nonlocal_stmt'''
        p[0] = p[1]

    def p_nonlocal_stmt1(self, p):
        ''' nonlocal_stmt : NONLOCAL NAME'''
        nonlocal_stmt = ast.Nonlocal()
        nonlocal_stmt.names = [p[2]]
        nonlocal_stmt.lineno = p.lineno(1)
        p[0] = nonlocal_stmt

    def p_nonlocal_stmt2(self, p):
        ''' global_stmt : NONLOCAL NAME globals_list '''
        nonlocal_stmt = ast.NonLocal()
        nonlocal_stmt.names = [p[2]] + p[3]
        nonlocal_stmt.lineno = p.lineno(1)
        p[0] = nonlocal_stmt

    def p_raise_stmt3(self, p):
        ''' raise_stmt : RAISE test FROM test '''
        raise_stmt = ast.Raise()
        raise_stmt.exc = p[1]
        raise_stmt.cause = p[4]
        p[0] = raise_stmt

    def p_test_or_star2(self, p):
        ''' test_or_star : star_expr '''
        p[0] = p[1]

    def p_star_expr(self, p):
        ''' star_expr : STAR expr '''
        # We can assume Load as we will explicitely set Store
        p[0] = ast.Starred(value=p[2], ctx=Load)

    def p_yield_expr3(self, p):
        ''' yield_expr : YIELD FROM testlist '''
        value = ast_for_testlist(p[2])
        p[0] = ast.Yield(value=value, lineno=p.lineno(1))

    def p_funcdef2(self, p):
        ''' funcdef : DEF NAME parameters RETURNARROW test COLON suite '''
        funcdef = ast.FunctionDef()
        funcdef.name = p[2]
        funcdef.args = p[3]
        funcdef.returns = p[5]
        funcdef.body = p[7]
        funcdef.decorator_list = []
        funcdef.lineno = p.lineno(1)
        ast.fix_missing_locations(funcdef)
        p[0] = funcdef

    def p_parameters2(self, p):
        ''' parameters : LPAR typedargslist RPAR '''
        p[0] = p[2]

    def p_classdef3(self, p):
        ''' classdef : CLASS NAME LPAR arglist RPAR COLON suite '''
        classdef = ast.ClassDef(keywords=[])
        classdef.name = p[2]

        args = p[4]  # This is an Arguments instance
        classdef.bases = args.args
        classdef.keywords = args.keywords
        classdef.starargs = args.starargs
        classdef.kwargs = args.kwargs

        classdef.body = p[7]
        classdef.decorator_list = []
        classdef.lineno = p.lineno(1)
        ast.fix_missing_locations(classdef)
        p[0] = classdef

    def p_atom11(self, p):
        ''' atom : ELLIPSIS '''
        p[0] = ast.Ellipsis()

    def p_atom12(self, p):
        ''' atom : atom_bytes_list '''
        s = ast.Bytes(s=p[1])
        p[0] = s

    def p_atom_bytes_list1(self, p):
        ''' atom_bytes_list : BYTES '''
        p[0] = p[1]

    def p_atom_bytes_list2(self, p):
        ''' atom_bytes_list : atom_bytes_list BYTES '''
        p[0] = p[1] + p[2]

    def _make_args(self, args, defaults=[], vararg=None, kwonlyargs=[],
                   kw_defaults=[], kwarg=None):
        """Build an ast node for function arguments.

        """
        # This is valid only for Python 3.3
        va = vararg.annotation if vararg else None
        vararg = vararg.arg if vararg else None
        ka = kwarg.annotation if kwarg else None
        kwarg = kwarg.arg if kwarg else None

        return ast.arguments(args=args, defaults=defaults, vararg=vararg,
                             varargannotation=va, kwonlyargs=kwonlyargs,
                             kw_defaults=kw_defaults, kwarg=kwarg,
                             kwargannotation=ka)

    def p_varargslist24(self, p):
        ''' varargslist : fpdef COMMA STAR fpdef kwargslist_list'''
        # def f(a, *args, e, b=1): pass
        klist_args, kdefaults = p[5]
        p[0] = self._make_args([p[1]], vararg=p[4], kwonlyargs=klist_args,
                               kw_defaults=kdefaults)

    def p_varargslist25(self, p):
        ''' varargslist : fpdef COMMA STAR kwargslist_list'''
        # def f(a, *, e, b=1): pass
        klist_args, kdefaults = p[4]
        p[0] = self._make_args([p[1]], kwonlyargs=klist_args,
                               kw_defaults=kdefaults)

    def p_varargslist26(self, p):
        ''' varargslist : fpdef COMMA STAR fpdef kwargslist_list COMMA DOUBLESTAR fpdef '''
        # def f(a, *args, e, b=1, **kwargs): pass
        klist_args, kdefaults = p[5]
        p[0] = self._make_args([p[1]], vararg=p[4], kwonlyargs=klist_args,
                               kw_defaults=kdefaults, kwarg=p[8])

    def p_varargslist27(self, p):
        ''' varargslist : fpdef COMMA STAR kwargslist_list COMMA DOUBLESTAR fpdef '''
        # def f(a, *, e, b=1, **kwargs): pass
        klist_args, kdefaults = p[4]
        p[0] = self._make_args([p[1]], kwonlyargs=klist_args,
                               kw_defaults=kdefaults,  kwarg=p[7])

    def p_varargslist28(self, p):
        ''' varargslist : fpdef varargslist_list COMMA STAR fpdef kwargslist_list '''
        # def f(a, c, d=4, *args, e, b=1): pass
        list_args, defaults = p[2]
        args = [p[1]] + list_args
        klist_args, kdefaults = p[6]
        p[0] = self._make_args(args=args, defaults=defaults, vararg=p[5],
                               kwonlyargs=klist_args, kw_defaults=kdefaults)

    def p_varargslist29(self, p):
        ''' varargslist : fpdef varargslist_list COMMA STAR kwargslist_list '''
        # def f(a, c, d=4, *args, e, b=1): pass
        list_args, defaults = p[2]
        args = [p[1]] + list_args
        klist_args, kdefaults = p[5]
        p[0] = self._make_args(args=args, defaults=defaults,
                               kwonlyargs=klist_args, kw_defaults=kdefaults)

    def p_varargslist30(self, p):
        ''' varargslist : fpdef varargslist_list COMMA STAR fpdef kwargslist_list COMMA DOUBLESTAR fpdef '''
        # def f(a, c, *args, e, b=1, **kwargs): pass
        list_args, defaults = p[2]
        args = [p[1]] + list_args
        klist_args, kdefaults = p[6]
        p[0] = self._make_args(args=args, defaults=defaults, vararg=p[5],
                               kwonlyargs=klist_args, kw_defaults=kdefaults,
                               kwarg=p[9])

    def p_varargslist31(self, p):
        ''' varargslist : fpdef varargslist_list COMMA STAR kwargslist_list COMMA DOUBLESTAR fpdef '''
        # def f(a, c, *, e, b=1, **kwargs): pass
        list_args, defaults = p[2]
        args = [p[1]] + list_args
        klist_args, kdefaults = p[5]
        p[0] = self._make_args(args=args, defaults=defaults,
                               kwonlyargs=klist_args, kw_defaults=kdefaults,
                               kwarg=p[8])

    def p_varargslist32(self, p):
        ''' varargslist : fpdef EQUAL test COMMA STAR fpdef kwargslist_list'''
        # def f(a=1, *args, e, b=1): pass
        klist_args, kdefaults = p[7]
        p[0] = self._make_args([p[1]], defaults=[p[3]], vararg=p[6],
                               kwonlyargs=klist_args, kw_defaults=kdefaults)

    def p_varargslist33(self, p):
        ''' varargslist : fpdef EQUAL test COMMA STAR kwargslist_list'''
        # def f(a=1, *args, e, b=1): pass
        klist_args, kdefaults = p[6]
        p[0] = self._make_args([p[1]], defaults=[p[3]],
                               kwonlyargs=klist_args, kw_defaults=kdefaults)

    def p_varargslist34(self, p):
        ''' varargslist : fpdef EQUAL test COMMA STAR fpdef kwargslist_list COMMA DOUBLESTAR fpdef '''
        # def f(a=1, *args, e, b=1, **kwargs): pass
        klist_args, kdefaults = p[7]
        p[0] = self._make_args([p[1]], defaults=[p[3]], vararg=p[6],
                               kwonlyargs=klist_args, kw_defaults=kdefaults,
                               kwarg=p[10])

    def p_varargslist35(self, p):
        ''' varargslist : fpdef EQUAL test COMMA STAR kwargslist_list COMMA DOUBLESTAR fpdef '''
        # def f(a=1, *, e, b=1, **kwargs): pass
        klist_args, kdefaults = p[6]
        p[0] = self._make_args([p[1]], defaults=[p[3]],
                               kwonlyargs=klist_args, kw_defaults=kdefaults,
                               kwarg=p[9])

    def p_varargslist36(self, p):
        ''' varargslist : fpdef EQUAL test varargslist_list COMMA STAR fpdef kwargslist_list'''
        # def f(a=1, b=2, *args, e, b=1): pass
        list_args, list_defaults = p[4]
        if len(list_args) != len(list_defaults):
            msg = 'non-default argument follows default argument.'
            tok = FakeToken(p.lexer.lexer, p.lineno(2))
            syntax_error(msg, tok)
        klist_args, kdefaults = p[8]
        args = [p[1]] + list_args
        defaults = [p[3]] + list_defaults
        p[0] = self._make_args(args, defaults=defaults, vararg=p[7],
                               kwonlyargs=klist_args, kw_defaults=kdefaults)

    def p_varargslist37(self, p):
        ''' varargslist : fpdef EQUAL test varargslist_list COMMA STAR kwargslist_list'''
        # def f(a=1, b=2, *, e, b=1): pass
        list_args, list_defaults = p[4]
        if len(list_args) != len(list_defaults):
            msg = 'non-default argument follows default argument.'
            tok = FakeToken(p.lexer.lexer, p.lineno(2))
            syntax_error(msg, tok)
        klist_args, kdefaults = p[7]
        args = [p[1]] + list_args
        defaults = [p[3]] + list_defaults
        p[0] = self._make_args(args, defaults=defaults,
                               kwonlyargs=klist_args, kw_defaults=kdefaults)

    def p_varargslist38(self, p):
        ''' varargslist : fpdef EQUAL test varargslist_list COMMA STAR fpdef kwargslist_list COMMA DOUBLESTAR fpdef '''
        # def f(a=1, b=2, *args, e, b=1, **kwargs)
        list_args, list_defaults = p[4]
        if len(list_args) != len(list_defaults):
            msg = 'non-default argument follows default argument.'
            tok = FakeToken(p.lexer.lexer, p.lineno(2))
            syntax_error(msg, tok)
        klist_args, kdefaults = p[8]
        args = [p[1]] + list_args
        defaults = [p[3]] + list_defaults
        p[0] = self._make_args(args, defaults=defaults, vararg=p[7],
                               kwonlyargs=klist_args, kw_defaults=kdefaults,
                               kwarg=p[11])

    def p_varargslist39(self, p):
        ''' varargslist : fpdef EQUAL test varargslist_list COMMA STAR kwargslist_list COMMA DOUBLESTAR fpdef '''
        # def f(a=1, b=2, *, e, b=1, **kwargs)
        list_args, list_defaults = p[4]
        if len(list_args) != len(list_defaults):
            msg = 'non-default argument follows default argument.'
            tok = FakeToken(p.lexer.lexer, p.lineno(2))
            syntax_error(msg, tok)
        klist_args, kdefaults = p[7]
        args = [p[1]] + list_args
        defaults = [p[3]] + list_defaults
        p[0] = self._make_args(args, defaults=defaults,
                               kwonlyargs=klist_args, kw_defaults=kdefaults,
                               kwarg=p[10])

    def p_varargslist40(self, p):
        ''' varargslist : STAR fpdef kwargslist_list '''
        # def f(*args, e, b=1): pass
        klist_args, kdefaults = p[3]
        p[0] = self._make_args([], vararg=p[2],
                               kwonlyargs=klist_args, kw_defaults=kdefaults)

    def p_varargslist41(self, p):
        ''' varargslist : STAR kwargslist_list '''
        # def f(*, e, b=1): pass
        klist_args, kdefaults = p[2]
        p[0] = self._make_args([], kwonlyargs=klist_args,
                               kw_defaults=kdefaults)

    def p_varargslist42(self, p):
        ''' varargslist : STAR fpdef kwargslist_list COMMA DOUBLESTAR fpdef '''
        # def f(*args, e, b=1, **kwargs): pass
        klist_args, kdefaults = p[3]
        p[0] = self._make_args(args=[], vararg=p[2], kwarg=p[6],
                               kwonlyargs=klist_args, kw_defaults=kdefaults)

    def p_varargslist43(self, p):
        ''' varargslist : STAR kwargslist_list COMMA DOUBLESTAR fpdef '''
        # def f(*, e, b=1,  **kwargs): pass
        klist_args, kdefaults = p[2]
        p[0] = self._make_args(args=[], kwarg=p[5],
                               kwonlyargs=klist_args, kw_defaults=kdefaults)

    # The kwargslist_list handlers return a 2-tuple of (args, defaults) lists
    def p_kwargslist_list1(self, p):
        ''' kwargslist_list : COMMA fpdef '''
        p[0] = ([p[2]], [None])

    def p_kwargslist_list2(self, p):
        ''' kwargslist_list : COMMA fpdef EQUAL test '''
        p[0] = ([p[2]], [p[4]])

    def p_kwargslist_list3(self, p):
        ''' kwargslist_list : kwargslist_list COMMA fpdef '''
        list_args, list_defaults = p[1]
        args = list_args + [p[3]]
        defaults = list_defaults + [None]
        p[0] = (args, defaults)

    def p_kwargslist_list4(self, p):
        ''' kwargslist_list : kwargslist_list COMMA fpdef EQUAL test '''
        list_args, list_defaults = p[1]
        args = list_args + [p[3]]
        defaults = list_defaults + [p[5]]
        p[0] = (args, defaults)

    def p_fpdef(self, p):
        ''' fpdef : NAME '''
        p[0] = ast.arg(arg=p[1], annotation=None)

    def p_tfpdef1(self, p):
        ''' tfpdef : NAME '''
        p[0] = ast.arg(arg=p[1], annotation=None)

    def p_tfpdef2(self, p):
        ''' tfpdef : NAME COLON test'''
        p[0] = ast.arg(arg=p[1], annotation=p[3])


def _make_typedarg_rule(f, f_name):
    """Copy a rule and allow for annotations.

    """
    rule = FunctionType(f.__code__, f.__globals__, f_name,
                        f.__defaults__, f.__closure__)

    new_doc = f.__doc__.replace('fpdef', 'tfpdef')
    new_doc = new_doc.replace('varargslist', 'typedargslist')
    rule.__doc__ = new_doc.replace('kwargslist', 'typedkwargslist')
    return rule


for f in (x for x in dir(Python3EnamlParser)
          if ('varargslist' in x) | ('kwargslist' in x)):
    if 'varargslist' in f:
        name = f.replace('varargslist', 'typedargslist')
    else:
        name = f.replace('kwargslist', 'typedkwargslist')
    setattr(Python3EnamlParser, name,
            _make_typedarg_rule(getattr(Python3EnamlParser, f), name))
