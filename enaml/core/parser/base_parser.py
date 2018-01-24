#------------------------------------------------------------------------------
# Copyright (c) 2013-2018, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#------------------------------------------------------------------------------
import ast
import os

import ply.yacc as yacc

from ...compat import IS_PY3
from .. import enaml_ast
from .base_lexer import (syntax_error, syntax_warning, BaseEnamlLexer,
                         ParsingError)

# -----------------------------------------------------------------------------
# Parsing Helpers
# -----------------------------------------------------------------------------
# Ast Context Singletons
Store = ast.Store()
Load = ast.Load()
Del = ast.Del()


# Python 2.6 compatibility. Transform set comprehension into set(generator)
try:
    SetComp = ast.SetComp
except AttributeError:
    def SetComp(elt, generators):
        gen = ast.GeneratorExp(elt=elt, generators=generators)
        call = ast.Call()
        call.func = ast.Name(id='set', ctx=Load)
        call.args = [gen]
        call.keywords = []
        call.starargs = None
        call.kwargs = None
        return call


# Python 2.6 compatibility. Transform dict comprehension into dict(generator)
try:
    DictComp = ast.DictComp
except AttributeError:
    def DictComp(key, value, generators):
        elt = ast.Tuple(elts=[key, value], ctx=Load)
        gen = ast.GeneratorExp(elt=elt, generators=generators)
        call = ast.Call()
        call.func = ast.Name(id='dict', ctx=Load)
        call.args = [gen]
        call.keywords = []
        call.starargs = None
        call.kwargs = None
        return call


# Python 2.6 compatibility. Transform set literal in set(list_literal)
try:
    Set = ast.Set
except AttributeError:
    def Set(elts):
        lst = ast.List(elts=elts, ctx=Load)
        call = ast.Call()
        call.func = ast.Name(id='set', ctx=Load)
        call.args = [lst]
        call.keywords = []
        call.starargs = None
        call.kwargs = None
        return call


class FakeToken(object):
    """ A fake token used to store the lexer before calling the
    syntax error functions.

    """
    def __init__(self, lexer, lineno):
        self.lexer = lexer
        self.lineno = lineno


def ast_for_testlist(testlist):
    """ If the testlist is a list, returns an ast.Tuple with a Load
    context, otherwise returns the orginal node.

    """
    if isinstance(testlist, list):
        value = ast.Tuple()
        value.elts = testlist
        value.ctx = Load
    else:
        value = testlist
    return value


def ast_for_dotted_name(dotted_name):
    parts = dotted_name.split('.')
    name = ast.Name(id=parts.pop(0), ctx=Load)
    res = name
    for part in parts:
        attr = ast.Attribute()
        attr.value = res
        attr.attr = part
        attr.ctx = Load
        res = attr
    return res


class CommaSeparatedList(object):
    """ A parsing helper to delineate a comma separated list.

    """
    def __init__(self, values=None):
        self.values = values or []


class GeneratorInfo(object):
    """ A parsing helper to delineate a generator body.

    """
    def __init__(self, elt=None, generators=None):
        self.elt = elt
        self.generators = generators or []


class Arguments(object):
    """ A parsing helper object to delineate call arguments.

    """
    def __init__(self, args=None, keywords=None, starargs=None, kwargs=None):
        self.args = args or []
        self.keywords = keywords or []
        self.starargs = starargs
        self.kwargs = kwargs


class BaseEnamlParser(object):
    """Base parser for enaml files.

    Handle the enaml syntax and the python syntax common to all versions.

    """
    # An id used to generate different parse table files per parser
    parser_id = ''

    # low to high
    precedence = tuple()

    # The allowed ast node types for ast.Store contexts
    context_allowed = set([
        ast.Attribute,
        ast.Subscript,
        ast.Name,
        ast.List,
        ast.Tuple,
    ])

    # The disallowed ast node types for ast.Store contexts and
    # the associated message tag for error reporting.
    context_disallowed = {
        ast.Lambda: 'lambda',
        ast.Call: 'function call',
        ast.BoolOp: 'operator',
        ast.BinOp: 'operator',
        ast.UnaryOp: 'operator',
        ast.GeneratorExp: 'generator expression',
        ast.Yield: 'yield expression',
        ast.ListComp: 'list comprehension',
        SetComp: 'set comprehension',
        DictComp: 'dict comprehension',
        ast.Dict: 'literal',
        Set: 'literal',
        ast.Num: 'literal',
        ast.Str: 'literal',
        ast.Ellipsis: 'Ellipsis',
        ast.Compare: 'comparison',
        ast.IfExp: 'conditional expression',
    }

    # The node types allowed in aug assignment
    aug_assign_allowed = set([
        ast.Name,
        ast.Attribute,
        ast.Subscript,
    ])

    # A mapping of aug assignment operators to ast types
    augassign_table = {
        '&=': ast.BitAnd(),
        '^=': ast.BitXor(),
        '//=': ast.FloorDiv(),
        '<<=': ast.LShift(),
        '-=': ast.Sub(),
        '%=': ast.Mod(),
        '+=': ast.Add(),
        '>>=': ast.RShift(),
        '/=': ast.Div(),
        '*=': ast.Mult(),
        '|=': ast.BitOr(),
        '**=': ast.Pow(),
    }

    lexer = BaseEnamlLexer

    def __init__(self):
        self.tokens = self.lexer().tokens
        # Get a save directory for the lex and parse tables
        parse_dir, parse_mod = self._tables_location()
        self.parser = yacc.yacc(
            method='LALR',
            module=self,
            start='enaml',
            tabmodule=parse_mod,
            outputdir=parse_dir,
            optimize=1,
            debug=0,
            errorlog=yacc.NullLogger())

    def write_tables(self):
        """Write the parser and lexer tables.

        """
        parse_dir, parse_mod = self._tables_location()
        # Using optimized = 0 force yacc to compare the parser signature to the
        # parse_tab signature and will update it if necessary.
        yacc.yacc(method='LALR',
                  module=self,
                  start='enaml',
                  tabmodule=parse_mod,
                  outputdir=parse_dir,
                  optimize=0,
                  debug=0,
                  errorlog=yacc.NullLogger())

    def _tables_location(self):
        parse_dir = os.path.join(os.path.dirname(__file__), 'parse_tab')
        parse_mod = 'enaml.core.parser.parse_tab.parsetab%s' % self.parser_id
        return parse_dir, parse_mod

    def parse(self, source, filename='Enaml'):
        """Parse source string and create abstract syntax tree (AST)."""
        try:
            lexer = self.lexer(filename)
            return self.parser.parse(source, debug=0, lexer=lexer)
        except ParsingError as parse_error:
            raise parse_error()

    def set_context(self, node, ctx, p):
        """ Recursively sets the context of the node to the given context
        which should be Store or Del. If the node is not one of the allowed
        types for the context, an erro is raised with an appropriate message.

        """
        # XXX passing the yacc production object to raise the error
        # message is a bit flakey and gets things wrong occasionally
        # when there are blank lines around the error. We can do better.
        items = None
        err_msg = ''
        node_type = type(node)
        if node_type in self.context_allowed:
            node.ctx = ctx
            if ctx == Store:
                if node_type == ast.Tuple:
                    if len(node.elts) == 0:
                        err_msg = '()'
                    else:
                        items = node.elts
                elif node_type == ast.List:
                    items = node.elts
        elif node_type in self.context_disallowed:
            err_msg = self.context_disallowed[node_type]
        else:
            msg = 'unexpected expression in assignment %d (line %d)'
            raise SystemError(msg % (node_type.__name__, node.lineno))

        if err_msg:
            m = 'assign to' if ctx == Store else 'delete'
            msg = "can't %s %s" % (m, err_msg)
            tok = FakeToken(p.lexer.lexer, p.lexer.lexer.lineno - 1)
            syntax_error(msg, tok)

        if items is not None:
            for item in items:
                self.set_context(item, ctx, p)

    def set_call_arguments(self, node, args):
        """Set the arguments for an ast.Call node.

        Parameters
        ----------
        node : ast.Call
            Node was arguments should be set.

        args : Arguments
            Arguments for the function call.

        """
        node.args = args.args
        node.keywords = args.keywords
        node.starargs = args.starargs
        node.kwargs = args.kwargs

    # =========================================================================
    # Begin Parsing Rules
    # =========================================================================

    # -------------------------------------------------------------------------
    # Enaml Module
    # -------------------------------------------------------------------------
    # These special rules to handle the variations of newline and endmarkers
    # are because of the various lexer states that deal with python blocks
    # and enaml code, as well as completely empty files.
    def p_enaml1(self, p):
        ''' enaml : enaml_module NEWLINE ENDMARKER
                  | enaml_module ENDMARKER '''
        p[0] = p[1]

    def p_enaml2(self, p):
        ''' enaml : NEWLINE ENDMARKER
                  | ENDMARKER '''
        p[0] = enaml_ast.Module()

    def p_enaml_module(self, p):
        ''' enaml_module : enaml_module_body '''
        body = []
        stmts = []
        for item in p[1]:
            if isinstance(item, (enaml_ast.EnamlDef, enaml_ast.Template)):
                if stmts:
                    mod = ast.Module(body=stmts)
                    python = enaml_ast.PythonModule(ast=mod,
                                                    lineno=stmts[0].lineno)
                    body.append(python)
                    stmts = []
                body.append(item)
            else:
                stmts.append(item)
        if stmts:
            mod = ast.Module(body=stmts)
            python = enaml_ast.PythonModule(ast=mod, lineno=stmts[0].lineno)
            body.append(python)
        p[0] = enaml_ast.Module(body=body)

    def p_enaml_module_body1(self, p):
        ''' enaml_module_body : enaml_module_body enaml_module_item '''
        items = p[2]  # a stmt can be a list
        if not isinstance(items, list):
            items = [items]
        p[0] = p[1] + items

    def p_enaml_module_body2(self, p):
        ''' enaml_module_body : enaml_module_item '''
        items = p[1]  # a stmt can be a list
        if not isinstance(items, list):
            items = [items]
        p[0] = items

    def p_enaml_module_item(self, p):
        ''' enaml_module_item : stmt
                              | enamldef
                              | template '''
        p[0] = p[1]

    # -------------------------------------------------------------------------
    # EnamlDef
    # -------------------------------------------------------------------------
    def _validate_enamldef(self, node, lexer):
        """ Validate the correctness of names in an enamldef definition.

        This function ensures that identifiers do not shadow one another.

        """
        ident_names = set()

        def check_id(name, node):
            if name in ident_names:
                msg = "redeclaration of identifier '%s'"
                msg += " (this will be an error in Enaml version 1.0)"
                syntax_warning(msg % name, FakeToken(lexer, node.lineno))
            ident_names.add(name)

        # validate the identifiers
        ChildDef = enaml_ast.ChildDef
        TemplateInst = enaml_ast.TemplateInst
        stack = list(reversed(node.body))
        while stack:
            node = stack.pop()
            if isinstance(node, ChildDef):
                if node.identifier:
                    check_id(node.identifier, node)
                stack.extend(reversed(node.body))
            elif isinstance(node, TemplateInst):
                idents = node.identifiers
                if idents is not None:
                    for name in idents.names:
                        check_id(name, idents)
                    if idents.starname:
                        check_id(idents.starname, idents)

    def p_enamldef1(self, p):
        ''' enamldef : enamldef_impl '''
        p[0] = p[1]

    def p_enamldef2(self, p):
        ''' enamldef : pragmas enamldef_impl '''
        node = p[2]
        node.pragmas = p[1]
        p[0] = node

    def p_enamldef_impl1(self, p):
        ''' enamldef_impl : ENAMLDEF NAME LPAR NAME RPAR COLON enamldef_suite '''
        doc, body = p[7]
        enamldef = enaml_ast.EnamlDef(
            typename=p[2], base=p[4], docstring=doc, body=body,
            lineno=p.lineno(1)
        )
        self._validate_enamldef(enamldef, p.lexer.lexer)
        p[0] = enamldef

    def p_enamldef_impl2(self, p):
        ''' enamldef_impl : ENAMLDEF NAME LPAR NAME RPAR COLON enamldef_simple_item '''
        body = [_f for _f in [p[7]] if _f]
        enamldef = enaml_ast.EnamlDef(
            typename=p[2], base=p[4], body=body, lineno=p.lineno(1)
        )
        self._validate_enamldef(enamldef, p.lexer.lexer)
        p[0] = enamldef

    def p_enamldef_impl3(self, p):
        ''' enamldef_impl : ENAMLDEF NAME LPAR NAME RPAR COLON NAME COLON enamldef_suite '''
        doc, body = p[9]
        enamldef = enaml_ast.EnamlDef(
            typename=p[2], base=p[4], identifier=p[7], docstring=doc,
            body=body, lineno=p.lineno(1)
        )
        self._validate_enamldef(enamldef, p.lexer.lexer)
        p[0] = enamldef

    def p_enamldef_impl4(self, p):
        ''' enamldef_impl : ENAMLDEF NAME LPAR NAME RPAR COLON NAME COLON enamldef_simple_item '''
        body = [_f for _f in [p[9]] if _f]
        enamldef = enaml_ast.EnamlDef(
            typename=p[2], base=p[4], identifier=p[7], body=body,
            lineno=p.lineno(1)
        )
        self._validate_enamldef(enamldef, p.lexer.lexer)
        p[0] = enamldef

    def p_enamldef_suite1(self, p):
        ''' enamldef_suite : NEWLINE INDENT enamldef_suite_items DEDENT '''
        # Filter out any pass statements
        items = [_f for _f in p[3] if _f]
        p[0] = ('', items)

    def p_enamldef_suite2(self, p):
        ''' enamldef_suite : NEWLINE INDENT STRING NEWLINE enamldef_suite_items DEDENT '''
        # Filter out any pass statements
        items = [_f for _f in p[5] if _f]
        p[0] = (p[3], items)

    def p_enamldef_suite_items1(self, p):
        ''' enamldef_suite_items : enamldef_suite_item '''
        p[0] = [p[1]]

    def p_enamldef_suite_items2(self, p):
        ''' enamldef_suite_items : enamldef_suite_items enamldef_suite_item '''
        p[0] = p[1] + [p[2]]

    def p_enamldef_suite_item(self, p):
        ''' enamldef_suite_item : enamldef_simple_item
                                | decl_funcdef
                                | child_def
                                | template_inst '''
        p[0] = p[1]

    def p_enamldef_simple_item1(self, p):
        ''' enamldef_simple_item : binding
                                 | ex_binding
                                 | alias_expr
                                 | storage_expr '''
        p[0] = p[1]

    def p_enamldef_simple_item2(self, p):
        ''' enamldef_simple_item : PASS NEWLINE '''
        p[0] = None

    # -------------------------------------------------------------------------
    # Pragmas
    # -------------------------------------------------------------------------
    def p_pragmas1(self, p):
        ''' pragmas : pragma pragmas '''
        p[0] = [p[1]] + p[2]

    def p_pragmas2(self, p):
        ''' pragmas : pragma '''
        p[0] = [p[1]]

    def p_pragma1(self, p):
        ''' pragma : PRAGMA NAME NEWLINE
                   | PRAGMA NAME LPAR RPAR NEWLINE '''
        node = enaml_ast.Pragma()
        node.lineno = p.lineno(1)
        node.command = p[2]
        p[0] = node

    def p_pragma2(self, p):
        ''' pragma : PRAGMA NAME LPAR pragma_args RPAR NEWLINE '''
        node = enaml_ast.Pragma()
        node.lineno = p.lineno(1)
        node.command = p[2]
        node.arguments = p[4]
        p[0] = node

    def p_pragma_args1(self, p):
        ''' pragma_args : pragma_arg COMMA pragma_args '''
        p[0] = [p[1]] + p[3]

    def p_pragma_args2(self, p):
        ''' pragma_args : pragma_arg '''
        p[0] = [p[1]]

    def p_pragma_arg(self, p):
        ''' pragma_arg : NAME '''
        p[0] = enaml_ast.PragmaArg(kind='token', value=p[1])

    def p_pragma_arg2(self, p):
        ''' pragma_arg : NUMBER '''
        p[0] = enaml_ast.PragmaArg(kind='number', value=p[1])

    def p_pragma_arg3(self, p):
        ''' pragma_arg : STRING '''
        p[0] = enaml_ast.PragmaArg(kind='string', value=p[1])

    # -------------------------------------------------------------------------
    # AliasExpr
    # -------------------------------------------------------------------------
    def p_alias_expr1(self, p):
        ''' alias_expr : ALIAS NAME NEWLINE '''
        node = enaml_ast.AliasExpr()
        node.lineno = p.lineno(1)
        node.name = p[2]
        node.target = p[2]
        p[0] = node

    def p_alias_expr2(self, p):
        ''' alias_expr : ALIAS NAME COLON NAME NEWLINE '''
        node = enaml_ast.AliasExpr()
        node.lineno = p.lineno(1)
        node.name = p[2]
        node.target = p[4]
        p[0] = node

    def p_alias_expr3(self, p):
        ''' alias_expr : ALIAS NAME COLON NAME ex_dotted_names NEWLINE '''
        node = enaml_ast.AliasExpr()
        node.lineno = p.lineno(1)
        node.name = p[2]
        node.target = p[4]
        node.chain = tuple(p[5])
        p[0] = node

    # -------------------------------------------------------------------------
    # ConstExpr
    # -------------------------------------------------------------------------
    def p_const_expr1(self, p):
        ''' const_expr : CONST NAME EQUAL test NEWLINE '''
        lineno = p.lineno(1)
        body = p[4]
        body.lineno = lineno
        ast.fix_missing_locations(body)
        expr = ast.Expression(body=body)
        python = enaml_ast.PythonExpression(ast=expr, lineno=lineno)
        node = enaml_ast.ConstExpr()
        node.lineno = lineno
        node.name = p[2]
        node.expr = python
        p[0] = node

    def p_const_expr2(self, p):
        ''' const_expr : CONST NAME COLON NAME EQUAL test NEWLINE '''
        lineno = p.lineno(1)
        body = p[6]
        body.lineno = lineno
        ast.fix_missing_locations(body)
        expr = ast.Expression(body=body)
        python = enaml_ast.PythonExpression(ast=expr, lineno=lineno)
        node = enaml_ast.ConstExpr()
        node.lineno = lineno
        node.name = p[2]
        node.typename = p[4]
        node.expr = python
        p[0] = node

    # -------------------------------------------------------------------------
    # StorageExpr
    # -------------------------------------------------------------------------
    def _validate_storage_expr(self, kind, lineno, lexer):
        if kind not in ('attr', 'event'):
            syntax_error('invalid syntax', FakeToken(lexer, lineno))

    def p_storage_expr1(self, p):
        ''' storage_expr : NAME NAME NEWLINE '''
        kind = p[1]
        lineno = p.lineno(1)
        self._validate_storage_expr(kind, lineno, p.lexer.lexer)
        node = enaml_ast.StorageExpr()
        node.lineno = lineno
        node.kind = kind
        node.name = p[2]
        p[0] = node

    def p_storage_expr2(self, p):
        ''' storage_expr : NAME NAME COLON NAME NEWLINE '''
        kind = p[1]
        lineno = p.lineno(1)
        self._validate_storage_expr(kind, lineno, p.lexer.lexer)
        node = enaml_ast.StorageExpr()
        node.lineno = lineno
        node.kind = kind
        node.name = p[2]
        node.typename = p[4]
        p[0] = node

    def p_storage_expr3(self, p):
        ''' storage_expr : NAME NAME operator_expr '''
        kind = p[1]
        lineno = p.lineno(1)
        self._validate_storage_expr(kind, lineno, p.lexer.lexer)
        node = enaml_ast.StorageExpr()
        node.lineno = lineno
        node.kind = kind
        node.name = p[2]
        node.expr = p[3]
        p[0] = node

    def p_storage_expr4(self, p):
        ''' storage_expr : NAME NAME COLON NAME operator_expr '''
        kind = p[1]
        lineno = p.lineno(1)
        self._validate_storage_expr(kind, lineno, p.lexer.lexer)
        node = enaml_ast.StorageExpr()
        node.lineno = lineno
        node.kind = kind
        node.name = p[2]
        node.typename = p[4]
        node.expr = p[5]
        p[0] = node

    # -------------------------------------------------------------------------
    # ChildDef
    # -------------------------------------------------------------------------
    def p_child_def1(self, p):
        ''' child_def : NAME COLON child_def_suite '''
        child_def = enaml_ast.ChildDef(
            typename=p[1], body=p[3], lineno=p.lineno(1)
        )
        p[0] = child_def

    def p_child_def2(self, p):
        ''' child_def : NAME COLON child_def_simple_item '''
        body = [_f for _f in [p[3]] if _f]
        p[0] = enaml_ast.ChildDef(typename=p[1], body=body, lineno=p.lineno(1))

    def p_child_def3(self, p):
        ''' child_def : NAME COLON NAME COLON child_def_suite '''
        child_def = enaml_ast.ChildDef(
            typename=p[1], identifier=p[3], body=p[5], lineno=p.lineno(1)
        )
        p[0] = child_def

    def p_child_def4(self, p):
        ''' child_def : NAME COLON NAME COLON child_def_simple_item  '''
        body = [_f for _f in [p[5]] if _f]
        child_def = enaml_ast.ChildDef(
            typename=p[1], identifier=p[3], body=body, lineno=p.lineno(1)
        )
        p[0] = child_def

    def p_child_def_suite(self, p):
        ''' child_def_suite : NEWLINE INDENT child_def_suite_items DEDENT '''
        # Filter out any pass statements
        items = [_f for _f in p[3] if _f]
        p[0] = items

    def p_child_def_suite_items1(self, p):
        ''' child_def_suite_items : child_def_suite_item '''
        p[0] = [p[1]]

    def p_child_def_suite_items2(self, p):
        ''' child_def_suite_items : child_def_suite_items child_def_suite_item '''
        p[0] = p[1] + [p[2]]

    def p_child_def_suite_item(self, p):
        ''' child_def_suite_item : child_def_simple_item
                                 | decl_funcdef
                                 | child_def
                                 | template_inst '''
        p[0] = p[1]

    def p_child_def_simple_item1(self, p):
        ''' child_def_simple_item : binding
                                  | ex_binding
                                  | alias_expr
                                  | storage_expr '''
        p[0] = p[1]

    def p_child_def_simple_item2(self, p):
        ''' child_def_simple_item : PASS NEWLINE '''
        p[0] = None

    # -------------------------------------------------------------------------
    # Binding
    # -------------------------------------------------------------------------
    def p_binding(self, p):
        ''' binding : NAME operator_expr '''
        p[0] = enaml_ast.Binding(name=p[1], expr=p[2], lineno=p.lineno(1))

    # -------------------------------------------------------------------------
    # ExBinding
    # -------------------------------------------------------------------------
    def p_ex_binding(self, p):
        ''' ex_binding : NAME ex_dotted_names operator_expr '''
        node = enaml_ast.ExBinding()
        node.lineno = p.lineno(1)
        node.chain = (p[1],) + tuple(p[2])
        node.expr = p[3]
        p[0] = node

    def p_ex_dotted_names1(self, p):
        ''' ex_dotted_names : DOT NAME '''
        p[0] = [p[2]]

    def p_ex_dotted_names2(self, p):
        ''' ex_dotted_names : DOT NAME ex_dotted_names '''
        p[0] = [p[2]] + p[3]

    # -------------------------------------------------------------------------
    # OperatorExpr
    # -------------------------------------------------------------------------
    def p_operator_expr1(self, p):
        ''' operator_expr : EQUAL test NEWLINE
                          | LEFTSHIFT test NEWLINE '''
        lineno = p.lineno(1)
        body = p[2]
        body.lineno = lineno
        ast.fix_missing_locations(body)
        expr = ast.Expression(body=body)
        python = enaml_ast.PythonExpression(ast=expr, lineno=lineno)
        p[0] = enaml_ast.OperatorExpr(operator=p[1], value=python,
                                      lineno=lineno)

    # The nodes which can be inverted to form an assignable expression.
    _INVERTABLE = (ast.Name, ast.Attribute, ast.Call, ast.Subscript)

    def p_operator_expr2(self, p):
        ''' operator_expr : COLONEQUAL test NEWLINE
                          | RIGHTSHIFT test NEWLINE '''
        lineno = p.lineno(1)
        body = p[2]
        if not isinstance(body, self._INVERTABLE):
            msg = "can't assign to expression of this form"
            syntax_error(msg, FakeToken(p.lexer.lexer, lineno))
        body.lineno = lineno
        ast.fix_missing_locations(body)
        expr = ast.Expression(body=body)
        python = enaml_ast.PythonExpression(ast=expr, lineno=lineno)
        p[0] = enaml_ast.OperatorExpr(operator=p[1], value=python,
                                      lineno=lineno)

    # The disallowed ast types on the rhs of a :: operator
    _NOTIFICATION_DISALLOWED = {
        ast.FunctionDef: 'function definition',
        ast.ClassDef: 'class definition',
        ast.Yield: 'yield statement',
        ast.Return: 'return statement',
    }

    def p_operator_expr3(self, p):
        ''' operator_expr : DOUBLECOLON suite '''
        lineno = p.lineno(1)

        for item in ast.walk(ast.Module(body=p[2])):
            if type(item) in self._NOTIFICATION_DISALLOWED:
                msg = '%s not allowed in a notification block'
                msg = msg % self._NOTIFICATION_DISALLOWED[type(item)]
                syntax_error(msg, FakeToken(p.lexer.lexer, item.lineno))

        func_node = ast.FunctionDef()
        func_node.name = 'f'
        func_node.args = self._make_args([])
        func_node.decorator_list = []
        if IS_PY3:
            func_node.returns = None
        func_node.body = p[2]
        func_node.lineno = lineno

        mod = ast.Module(body=[func_node])
        ast.fix_missing_locations(mod)

        python = enaml_ast.PythonModule(ast=mod, lineno=lineno)
        p[0] = enaml_ast.OperatorExpr(operator=p[1], value=python,
                                      lineno=lineno)

    # -------------------------------------------------------------------------
    # Declarative Function Definition
    # -------------------------------------------------------------------------
    # The disallowed ast types in the body of a declarative function
    _DECL_FUNCDEF_DISALLOWED = {
        ast.FunctionDef: 'function definition',
        ast.ClassDef: 'class definition',
        ast.Yield: 'yield statement',
        ast.GeneratorExp: 'generator expressions',
    }

    def _validate_decl_funcdef(self, funcdef, lexer):
        walker = ast.walk(funcdef)
        next(walker)  # discard toplevel funcdef
        for item in walker:
            if type(item) in self._DECL_FUNCDEF_DISALLOWED:
                msg = '%s not allowed in a declarative function block'
                msg = msg % self._DECL_FUNCDEF_DISALLOWED[type(item)]
                syntax_error(msg, FakeToken(lexer, item.lineno))

    def p_decl_funcdef1(self, p):
        ''' decl_funcdef : NAME NAME parameters COLON suite '''
        lineno = p.lineno(1)
        if p[1] != 'func':
            syntax_error('invalid syntax', FakeToken(p.lexer.lexer, lineno))
        funcdef = ast.FunctionDef()
        funcdef.name = p[2]
        funcdef.args = p[3]
        if IS_PY3:
            funcdef.returns = None
        funcdef.body = p[5]
        funcdef.decorator_list = []
        funcdef.lineno = lineno
        ast.fix_missing_locations(funcdef)
        self._validate_decl_funcdef(funcdef, p.lexer.lexer)
        decl_funcdef = enaml_ast.FuncDef()
        decl_funcdef.lineno = lineno
        decl_funcdef.funcdef = funcdef
        decl_funcdef.is_override = False
        p[0] = decl_funcdef

    def p_decl_funcdef2(self, p):
        ''' decl_funcdef : NAME RIGHTARROW parameters COLON suite '''
        lineno = p.lineno(1)
        funcdef = ast.FunctionDef()
        funcdef.name = p[1]
        funcdef.args = p[3]
        if IS_PY3:
            funcdef.returns = None
        funcdef.body = p[5]
        funcdef.decorator_list = []
        funcdef.lineno = lineno
        ast.fix_missing_locations(funcdef)
        self._validate_decl_funcdef(funcdef, p.lexer.lexer)
        decl_funcdef = enaml_ast.FuncDef()
        decl_funcdef.lineno = lineno
        decl_funcdef.funcdef = funcdef
        decl_funcdef.is_override = True
        p[0] = decl_funcdef

    # -------------------------------------------------------------------------
    # Template
    # -------------------------------------------------------------------------
    def _validate_template(self, node, lexer):
        """ Validate the correctness of names in a template definitions.

        This function ensures that parameters, const expressions, and
        identifiers do not shadow one another.

        """
        param_names = set()
        const_names = set()
        ident_names = set()

        def check_const(name, node):
            msg = None
            if name in param_names:
                msg = "declaration of 'const %s' shadows a parameter"
            elif name in const_names:
                msg = "redeclaration of 'const %s'"
            if msg is not None:
                syntax_error(msg % name, FakeToken(lexer, node.lineno))
            const_names.add(name)

        def check_id(name, node):
            msg = None
            if name in param_names:
                msg = "identifier '%s' shadows a parameter"
            elif name in const_names:
                msg = "identifier '%s' shadows a const expression"
            elif name in ident_names:
                msg = "redeclaration of identifier '%s'"
            if msg is not None:
                syntax_error(msg % name, FakeToken(lexer, node.lineno))
            ident_names.add(name)

        # collect the parameter names
        params = node.parameters
        for param in params.positional:
            param_names.add(param.name)
        for param in params.keywords:
            param_names.add(param.name)
        if params.starparam:
            param_names.add(params.starparam)

        # validate the const expressions
        ConstExpr = enaml_ast.ConstExpr
        for item in node.body:
            if isinstance(item, ConstExpr):
                check_const(item.name, item)

        # validate the identifiers
        ChildDef = enaml_ast.ChildDef
        TemplateInst = enaml_ast.TemplateInst
        stack = list(reversed(node.body))
        while stack:
            node = stack.pop()
            if isinstance(node, ChildDef):
                if node.identifier:
                    check_id(node.identifier, node)
                stack.extend(reversed(node.body))
            elif isinstance(node, TemplateInst):
                idents = node.identifiers
                if idents is not None:
                    for name in idents.names:
                        check_id(name, idents)
                    if idents.starname:
                        check_id(idents.starname, idents)

    def p_template1(self, p):
        ''' template : template_impl '''
        p[0] = p[1]

    def p_template2(self, p):
        ''' template : pragmas template_impl '''
        node = p[2]
        node.pragmas = p[1]
        p[0] = node

    def p_template_impl1(self, p):
        ''' template_impl : TEMPLATE NAME template_params COLON template_suite '''
        node = enaml_ast.Template()
        node.lineno = p.lineno(1)
        node.name = p[2]
        node.parameters = p[3]
        node.body = p[5]
        self._validate_template(node, p.lexer.lexer)
        p[0] = node

    def p_template_impl2(self, p):
        ''' template_impl : TEMPLATE NAME template_params COLON template_simple_item '''
        node = enaml_ast.Template()
        node.lineno = p.lineno(1)
        node.name = p[2]
        node.parameters = p[3]
        node.body = [_f for _f in [p[5]] if _f]
        self._validate_template(node, p.lexer.lexer)
        p[0] = node

    def p_template_impl3(self, p):
        ''' template_impl : TEMPLATE NAME template_params COLON template_doc_suite '''
        doc, body = p[5]
        node = enaml_ast.Template()
        node.lineno = p.lineno(1)
        node.name = p[2]
        node.parameters = p[3]
        node.docstring = doc
        node.body = body
        self._validate_template(node, p.lexer.lexer)
        p[0] = node

    def p_template_suite(self, p):
        ''' template_suite : NEWLINE INDENT template_suite_items DEDENT '''
        # Filter out any pass statements
        p[0] = [_f for _f in p[3] if _f]

    def p_template_doc_suite(self, p):
        ''' template_doc_suite : NEWLINE INDENT STRING NEWLINE template_suite_items DEDENT '''
        # Filter out any pass statements
        p[0] = (p[3], [_f for _f in p[5] if _f])

    def p_template_suite_items1(self, p):
        ''' template_suite_items : template_suite_item '''
        p[0] = [p[1]]

    def p_template_suite_items2(self, p):
        ''' template_suite_items : template_suite_items template_suite_item '''
        p[0] = p[1] + [p[2]]

    def p_template_suite_item(self, p):
        ''' template_suite_item : template_simple_item
                                | child_def
                                | template_inst '''
        p[0] = p[1]

    def p_template_simple_item1(self, p):
        ''' template_simple_item : const_expr '''
        p[0] = p[1]

    def p_template_simple_item2(self, p):
        ''' template_simple_item : PASS NEWLINE '''
        p[0] = None

    def p_template_params1(self, p):
        ''' template_params : LPAR RPAR '''
        node = enaml_ast.TemplateParameters()
        node.lineno = p.lineno(1)
        p[0] = node

    def _validate_template_paramlist(self, paramlist, starparam, lexer):
        keywords = []
        positional = []
        seen_params = set([starparam])
        for param in paramlist:
            if param.name in seen_params:
                msg = "duplicate argument '%s' in template definition"
                syntax_error(msg % param.name, FakeToken(lexer, param.lineno))
            seen_params.add(param.name)
            if isinstance(param, enaml_ast.KeywordParameter):
                keywords.append(param)
            elif keywords:
                msg = "non-default argument follows default argument"
                syntax_error(msg, FakeToken(lexer, param.lineno))
            else:
                positional.append(param)
        return positional, keywords

    def p_template_params2(self, p):
        ''' template_params : LPAR template_paramlist RPAR '''
        params, starparam = p[2]
        pos, kwds = self._validate_template_paramlist(params, starparam,
                                                      p.lexer.lexer)
        node = enaml_ast.TemplateParameters()
        node.positional = pos
        node.keywords = kwds
        node.starparam = starparam
        p[0] = node

    def p_template_paramlist1(self, p):
        ''' template_paramlist : template_param '''
        p[0] = ([p[1]], '')

    def p_template_paramlist2(self, p):
        ''' template_paramlist : STAR NAME '''
        p[0] = ([], p[2])

    def p_template_paramlist3(self, p):
        ''' template_paramlist : template_param template_paramlist_list '''
        p[0] = ([p[1]] + p[2], '')

    def p_template_paramlist4(self, p):
        ''' template_paramlist : template_param COMMA STAR NAME '''
        p[0] = ([p[1]], p[4])

    def p_template_paramlist5(self, p):
        ''' template_paramlist : template_param template_paramlist_list COMMA STAR NAME '''
        p[0] = ([p[1]] + p[2], p[5])

    def p_template_paramlist_list1(self, p):
        ''' template_paramlist_list : COMMA template_param '''
        p[0] = [p[2]]

    def p_template_paramlist_list2(self, p):
        ''' template_paramlist_list : template_paramlist_list COMMA template_param '''
        p[0] = p[1] + [p[3]]

    def p_template_param1(self, p):
        ''' template_param : NAME '''
        node = enaml_ast.PositionalParameter()
        node.lineno = p.lineno(1)
        node.name = p[1]
        p[0] = node

    def p_template_param2(self, p):
        ''' template_param : NAME COLON test '''
        lineno = p.lineno(1)
        node = enaml_ast.PositionalParameter()
        node.lineno = lineno
        node.name = p[1]
        body = p[3]
        body.lineno = lineno
        ast.fix_missing_locations(body)
        expr = ast.Expression(body=body)
        python = enaml_ast.PythonExpression(ast=expr, lineno=lineno)
        node.specialization = python
        p[0] = node

    def p_template_param3(self, p):
        ''' template_param : NAME EQUAL test '''
        lineno = p.lineno(1)
        node = enaml_ast.KeywordParameter()
        node.lineno = lineno
        node.name = p[1]
        body = p[3]
        body.lineno = lineno
        ast.fix_missing_locations(body)
        expr = ast.Expression(body=body)
        python = enaml_ast.PythonExpression(ast=expr, lineno=lineno)
        node.default = python
        p[0] = node

    # -------------------------------------------------------------------------
    # Template Instantiation
    # -------------------------------------------------------------------------
    def _validate_template_inst(self, node, lexer):
        """ Validate a template instantiation.

        This function ensures that the bindings on the instantiation refer
        to declared identifiers on the instantiation.

        """
        names = set()
        if node.identifiers:
            names.update(node.identifiers.names)
        for binding in node.body:
            if binding.name not in names:
                msg = "'%s' is not a valid template id reference"
                syntax_error(msg % binding.name,
                             FakeToken(lexer, binding.lineno))

    def p_template_inst1(self, p):
        ''' template_inst : template_inst_impl '''
        p[0] = p[1]

    def p_template_inst2(self, p):
        ''' template_inst : pragmas template_inst_impl '''
        node = p[2]
        node.pragmas = p[1]
        p[0] = node

    def p_template_inst_impl1(self, p):
        ''' template_inst_impl : NAME template_args COLON template_inst_suite_item '''
        node = enaml_ast.TemplateInst()
        node.lineno = p.lineno(1)
        node.name = p[1]
        node.arguments = p[2]
        node.body = [_f for _f in [p[4]] if _f]
        self._validate_template_inst(node, p.lexer.lexer)
        p[0] = node

    def p_template_inst_impl2(self, p):
        ''' template_inst_impl : NAME template_args COLON template_ids COLON template_inst_suite_item '''
        node = enaml_ast.TemplateInst()
        node.lineno = p.lineno(1)
        node.name = p[1]
        node.arguments = p[2]
        node.identifiers = p[4]
        node.body = [_f for _f in [p[6]] if _f]
        self._validate_template_inst(node, p.lexer.lexer)
        p[0] = node

    def p_template_inst_impl3(self, p):
        ''' template_inst_impl : NAME template_args COLON template_inst_suite '''
        node = enaml_ast.TemplateInst()
        node.lineno = p.lineno(1)
        node.name = p[1]
        node.arguments = p[2]
        node.body = [_f for _f in p[4] if _f]
        self._validate_template_inst(node, p.lexer.lexer)
        p[0] = node

    def p_template_inst_impl4(self, p):
        ''' template_inst_impl : NAME template_args COLON template_ids COLON template_inst_suite '''
        node = enaml_ast.TemplateInst()
        node.lineno = p.lineno(1)
        node.name = p[1]
        node.arguments = p[2]
        node.identifiers = p[4]
        node.body = [_f for _f in p[6] if _f]
        self._validate_template_inst(node, p.lexer.lexer)
        p[0] = node

    def p_template_args1(self, p):
        ''' template_args : LPAR RPAR '''
        node = enaml_ast.TemplateArguments()
        node.lineno = p.lineno(1)
        p[0] = node

    def _fixup_template_args(self, node):
        lineno = node.lineno
        for arg in node.args:
            if arg.lineno == -1:
                arg.lineno = lineno
            else:
                lineno = arg.lineno
            arg.ast.body.lineno = lineno
            ast.fix_missing_locations(arg.ast.body)

    def p_template_args2(self, p):
        ''' template_args : LPAR template_arglist RPAR '''
        args, stararg = p[2]
        node = enaml_ast.TemplateArguments()
        node.lineno = p.lineno(1)
        node.args = args
        node.stararg = stararg
        self._fixup_template_args(node)
        p[0] = node

    def p_template_arglist1(self, p):
        ''' template_arglist : template_argument '''
        p[0] = ([p[1]], None)

    def p_template_arglist2(self, p):
        ''' template_arglist : STAR test '''
        lineno = p.lineno(1)
        body = p[2]
        body.lineno = lineno
        ast.fix_missing_locations(body)
        expr = ast.Expression(body=body)
        node = enaml_ast.PythonExpression(ast=expr, lineno=lineno)
        p[0] = ([], node)

    def p_template_arglist3(self, p):
        ''' template_arglist : template_argument template_arglist_list '''
        p[0] = ([p[1]] + p[2], None)

    def p_template_arglist4(self, p):
        ''' template_arglist : template_argument COMMA STAR test '''
        lineno = p.lineno(3)
        body = p[4]
        body.lineno = lineno
        ast.fix_missing_locations(body)
        expr = ast.Expression(body=body)
        node = enaml_ast.PythonExpression(ast=expr, lineno=lineno)
        p[0] = ([p[1]], node)

    def p_template_arglist5(self, p):
        ''' template_arglist : template_argument template_arglist_list COMMA STAR test '''
        lineno = p.lineno(4)
        body = p[5]
        body.lineno = lineno
        ast.fix_missing_locations(body)
        expr = ast.Expression(body=body)
        node = enaml_ast.PythonExpression(ast=expr, lineno=lineno)
        p[0] = ([p[1]] + p[2], node)

    def p_template_arglist_list1(self, p):
        ''' template_arglist_list : COMMA template_argument '''
        arg = p[2]
        if arg.lineno == -1:
            arg.lineno = p.lineno(1)
        p[0] = [arg]

    def p_template_arglist_list2(self, p):
        ''' template_arglist_list : template_arglist_list COMMA template_argument '''
        arg = p[3]
        if arg.lineno == -1:
            arg.lineno = p.lineno(2)
        p[0] = p[1] + [arg]

    def p_template_argument1(self, p):
        ''' template_argument : test '''
        expr = ast.Expression(body=p[1])
        node = enaml_ast.PythonExpression(ast=expr)
        p[0] = node

    def p_template_argument2(self, p):
        ''' template_argument : test comp_for '''
        expr = ast.GeneratorExp(elt=p[1], generators=p[2])
        node = enaml_ast.PythonExpression(ast=expr)
        p[0] = node

    def p_template_ids1(self, p):
        ''' template_ids : NAME '''
        node = enaml_ast.TemplateIdentifiers()
        node.lineno = p.lineno(1)
        node.names = [p[1]]
        p[0] = node

    def p_template_ids2(self, p):
        ''' template_ids : template_id_list NAME '''
        node = enaml_ast.TemplateIdentifiers()
        node.lineno = p.lineno(2)
        node.names = p[1] + [p[2]]
        p[0] = node

    def p_template_ids3(self, p):
        ''' template_ids : STAR NAME '''
        node = enaml_ast.TemplateIdentifiers()
        node.lineno = p.lineno(1)
        node.starname = p[2]
        p[0] = node

    def p_template_ids4(self, p):
        ''' template_ids : template_id_list STAR NAME '''
        node = enaml_ast.TemplateIdentifiers()
        node.lineno = p.lineno(2)
        node.names = p[1]
        node.starname = p[3]
        p[0] = node

    def p_template_id_list1(self, p):
        ''' template_id_list : NAME COMMA '''
        p[0] = [p[1]]

    def p_template_id_list2(self, p):
        ''' template_id_list : template_id_list NAME COMMA '''
        p[0] = p[1] + [p[2]]

    def p_template_inst_suite(self, p):
        ''' template_inst_suite : NEWLINE INDENT template_inst_suite_items DEDENT '''
        p[0] = p[3]

    def p_template_inst_suite_items1(self, p):
        ''' template_inst_suite_items : template_inst_suite_items template_inst_suite_item '''
        p[0] = p[1] + [p[2]]

    def p_template_inst_suite_items2(self, p):
        ''' template_inst_suite_items : template_inst_suite_item '''
        p[0] = [p[1]]

    def p_template_inst_suite_item1(self, p):
        ''' template_inst_suite_item : template_inst_binding '''
        p[0] = p[1]

    def p_template_inst_suite_item2(self, p):
        ''' template_inst_suite_item : PASS NEWLINE '''
        p[0] = None

    def p_template_inst_binding(self, p):
        ''' template_inst_binding : NAME ex_dotted_names operator_expr '''
        node = enaml_ast.TemplateInstBinding()
        node.lineno = p.lineno(1)
        node.name = p[1]
        node.chain = tuple(p[2])
        node.expr = p[3]
        p[0] = node

    # -------------------------------------------------------------------------
    # Python Grammar
    # -------------------------------------------------------------------------
    def p_suite1(self, p):
        ''' suite : simple_stmt '''
        # stmt may be a list of simple_stmt due to this piece of grammar:
        # simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE
        stmt = p[1]
        if isinstance(stmt, list):
            res = stmt
        else:
            res = [stmt]
        p[0] = res

    def p_suite2(self, p):
        ''' suite : NEWLINE INDENT stmt_list DEDENT '''
        p[0] = p[3]

    def p_stmt_list1(self, p):
        ''' stmt_list : stmt stmt_list '''
        # stmt may be a list of simple_stmt due to this piece of grammar:
        # simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE
        stmt = p[1]
        if isinstance(stmt, list):
            res = stmt + p[2]
        else:
            res = [stmt] + p[2]
        p[0] = res

    def p_stmt_list2(self, p):
        ''' stmt_list : stmt '''
        # stmt may be a list of simple_stmt due to this piece of grammar:
        # simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE
        stmt = p[1]
        if isinstance(stmt, list):
            res = stmt
        else:
            res = [stmt]
        p[0] = res

    def p_stmt(self, p):
        ''' stmt : simple_stmt
                 | compound_stmt '''
        p[0] = p[1]

    def p_simple_stmt1(self, p):
        ''' simple_stmt : small_stmt NEWLINE '''
        stmt = p[1]
        stmt.lineno = p.lineno(2)
        ast.fix_missing_locations(stmt)
        p[0] = stmt

    def p_simple_stmt2(self, p):
        ''' simple_stmt : small_stmt_list NEWLINE '''
        lineno = p.lineno(2)
        stmts = p[1]
        for stmt in stmts:
            stmt.lineno = lineno
            ast.fix_missing_locations(stmt)
        p[0] = stmts

    def p_small_stmt_list1(self, p):
        ''' small_stmt_list : small_stmt SEMI '''
        p[0] = [p[1]]

    def p_small_stmt_list2(self, p):
        ''' small_stmt_list : small_stmt small_stmt_list_list '''
        p[0] = [p[1]] + p[2]

    def p_small_stmt_list3(self, p):
        ''' small_stmt_list : small_stmt small_stmt_list_list SEMI '''
        p[0] = [p[1]] + p[2]

    def p_small_stmt_list_list1(self, p):
        ''' small_stmt_list_list : SEMI small_stmt '''
        p[0] = [p[2]]

    def p_small_stmt_list_list2(self, p):
        ''' small_stmt_list_list : small_stmt_list_list SEMI small_stmt '''
        p[0] = p[1] + [p[3]]

    def p_small_stmt1(self, p):
        ''' small_stmt : expr_stmt
                       | del_stmt
                       | pass_stmt
                       | flow_stmt
                       | import_stmt
                       | global_stmt
                       | assert_stmt '''
        p[0] = p[1]

    def p_del_stmt(self, p):
        ''' del_stmt : DEL exprlist '''
        exprlist = p[2]
        self.set_context(exprlist, Del, p)
        del_stmt = ast.Delete()
        del_stmt.targets = [exprlist]
        p[0] = del_stmt

    def p_pass_stmt(self, p):
        ''' pass_stmt : PASS '''
        pass_stmt = ast.Pass()
        pass_stmt.lineno = p.lineno(1)
        p[0] = pass_stmt

    def p_flow_stmt(self, p):
        ''' flow_stmt : break_stmt
                      | continue_stmt
                      | return_stmt
                      | raise_stmt
                      | yield_stmt '''
        p[0] = p[1]

    def p_break_stmt(self, p):
        ''' break_stmt : BREAK '''
        break_stmt = ast.Break()
        break_stmt.lineno = p.lineno(1)
        p[0] = break_stmt

    def p_continue_stmt(self, p):
        ''' continue_stmt : CONTINUE '''
        continue_stmt = ast.Continue()
        continue_stmt.lineno = p.lineno(1)
        p[0] = continue_stmt

    def p_return_stmt1(self, p):
        ''' return_stmt : RETURN '''
        ret = ast.Return()
        ret.value = None
        p[0] = ret

    def p_return_stmt2(self, p):
        ''' return_stmt : RETURN testlist '''
        value = ast_for_testlist(p[2])
        ret = ast.Return()
        ret.value = value
        p[0] = ret

    def p_raise_stmt1(self, p):
        ''' raise_stmt : RAISE '''
        raise_stmt = ast.Raise()
        if IS_PY3:
            raise_stmt.exc = None
            raise_stmt.cause = None
        else:
            raise_stmt.type = None
            raise_stmt.inst = None
            raise_stmt.tback = None
        p[0] = raise_stmt

    def p_raise_stmt2(self, p):
        ''' raise_stmt : RAISE test '''
        raise_stmt = ast.Raise()
        if IS_PY3:
            raise_stmt.exc = p[2]
            raise_stmt.cause = None
        else:
            raise_stmt.type = p[2]
            raise_stmt.inst = None
            raise_stmt.tback = None
        p[0] = raise_stmt

    def p_yield_stmt(self, p):
        ''' yield_stmt : yield_expr '''
        p[0] = ast.Expr(value=p[1])

    def p_yield_expr1(self, p):
        ''' yield_expr : YIELD '''
        p[0] = ast.Yield(value=None, lineno=p.lineno(1))

    def p_yield_expr2(self, p):
        ''' yield_expr : YIELD testlist '''
        value = ast_for_testlist(p[2])
        p[0] = ast.Yield(value=value, lineno=p.lineno(1))

    def p_global_stmt1(self, p):
        ''' global_stmt : GLOBAL NAME '''
        global_stmt = ast.Global()
        global_stmt.names = [p[2]]
        global_stmt.lineno = p.lineno(1)
        p[0] = global_stmt

    def p_global_stmt2(self, p):
        ''' global_stmt : GLOBAL NAME globals_list '''
        global_stmt = ast.Global()
        global_stmt.names = [p[2]] + p[3]
        global_stmt.lineno = p.lineno(1)
        p[0] = global_stmt

    def p_globals_list1(self, p):
        ''' globals_list : COMMA NAME globals_list '''
        p[0] = [p[2]] + p[3]

    def p_globals_list2(self, p):
        ''' globals_list : COMMA NAME '''
        p[0] = [p[2]]

    def p_assert_stmt1(self, p):
        ''' assert_stmt : ASSERT test '''
        assert_stmt = ast.Assert()
        assert_stmt.test = p[2]
        assert_stmt.msg = None
        p[0] = assert_stmt

    def p_assert_stmt2(self, p):
        ''' assert_stmt : ASSERT test COMMA test '''
        assert_stmt = ast.Assert()
        assert_stmt.test = p[2]
        assert_stmt.msg = p[4]
        p[0] = assert_stmt

    def p_expr_stmt1(self, p):
        ''' expr_stmt : testlist_star_expr '''
        expr = ast.Expr()
        expr.value = ast_for_testlist(p[1])
        p[0] = expr

    def p_expr_stmt2(self, p):
        ''' expr_stmt : testlist_star_expr augassign testlist
                      | testlist_star_expr augassign yield_expr '''
        op, lineno = p[2]
        lhs = ast_for_testlist(p[1])
        rhs = ast_for_testlist(p[3])
        self.set_context(lhs, Store, p)
        if type(lhs) not in self.aug_assign_allowed:
            msg = 'illegal expression for augmented assignment'
            syntax_error(msg, FakeToken(p.lexer.lexer, lineno))
        aug = ast.AugAssign()
        aug.target = lhs
        aug.value = rhs
        aug.op = op
        p[0] = aug

    def p_expr_stmt3(self, p):
        ''' expr_stmt : testlist_star_expr equal_list '''
        all_items = [p[1]] + p[2]
        targets = list(map(ast_for_testlist, all_items))
        value = targets.pop()
        for item in targets:
            if type(item) == ast.Yield:
                msg = "assignment to yield expression not possible"
                syntax_error(msg, FakeToken(p.lexer.lexer, item.lineno))
            self.set_context(item, Store, p)
        assg = ast.Assign()
        assg.targets = targets
        assg.value = value
        p[0] = assg

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
                      | VBAREQUAL '''
        lineno = p.lineno(1)
        op = self.augassign_table[p[1]]
        p[0] = (op, lineno)

    def p_equal_list1(self, p):
        ''' equal_list : EQUAL testlist_star_expr
                       | EQUAL yield_expr '''
        p[0] = [p[2]]

    def p_equal_list2(self, p):
        ''' equal_list : EQUAL testlist_star_expr equal_list
                       | EQUAL yield_expr equal_list '''
        p[0] = [p[2]] + p[3]

    def p_testlist1(self, p):
        ''' testlist : test '''
        p[0] = p[1]

    def p_testlist2(self, p):
        ''' testlist : test COMMA '''
        p[0] = [p[1]]

    def p_testlist3(self, p):
        ''' testlist : test testlist_list '''
        p[0] = [p[1]] + p[2]

    def p_testlist4(self, p):
        ''' testlist : test testlist_list COMMA '''
        p[0] = [p[1]] + p[2]

    def p_testlist_list1(self, p):
        ''' testlist_list : COMMA test '''
        p[0] = [p[2]]

    def p_testlist_list2(self, p):
        ''' testlist_list : testlist_list COMMA test '''
        p[0] = p[1] + [p[3]]

    # Star expr does not exist before Python 3 but to avoid redefining many
    # rules we take it into account here and add the star_expr rule only under
    # Python 3
    def p_test_or_star1(self, p):
        ''' test_or_star : test '''
        p[0] = p[1]

    # Under Python 3.5 star expr can occur in new places
    def p_test_or_star_new1(self, p):
        ''' test_or_star_new : test '''
        p[0] = p[1]

    def p_testlist_star_expr1(self, p):
        ''' testlist_star_expr : test_or_star '''
        p[0] = p[1]

    def p_test_list_star_expr2(self, p):
        ''' testlist_star_expr : test_or_star COMMA '''
        p[0] = [p[1]]

    def p_test_list_star_expr3(self, p):
        ''' testlist_star_expr : test_or_star testlist_star_expr_list '''
        p[0] = [p[1]] + p[2]

    def p_test_list_star_expr4(self, p):
        ''' testlist_star_expr : test_or_star testlist_star_expr_list COMMA '''
        p[0] = [p[1]] + p[2]

    def p_test_list_star_expr_list1(self, p):
        ''' testlist_star_expr_list : COMMA test_or_star '''
        p[0] = [p[2]]

    def p_test_list_star_expr_list2(self, p):
        ''' testlist_star_expr_list : testlist_star_expr_list COMMA test_or_star '''
        p[0] = p[1] + [p[3]]

    def p_compound_stmt(self, p):
        ''' compound_stmt : if_stmt
                          | while_stmt
                          | for_stmt
                          | try_stmt
                          | with_stmt
                          | funcdef
                          | classdef
                          | decorated '''
        p[0] = p[1]

    def p_if_stmt1(self, p):
        ''' if_stmt : IF test COLON suite '''
        if_stmt = ast.If()
        if_stmt.test = p[2]
        if_stmt.body = p[4]
        if_stmt.lineno = p.lineno(1)
        ast.fix_missing_locations(if_stmt)
        if_stmt.orelse = []
        p[0] = if_stmt

    def p_if_stmt2(self, p):
        ''' if_stmt : IF test COLON suite elif_stmts '''
        if_stmt = ast.If()
        if_stmt.test = p[2]
        if_stmt.body = p[4]
        if_stmt.lineno = p.lineno(1)
        if_stmt.orelse = [p[5]]
        ast.fix_missing_locations(if_stmt)
        p[0] = if_stmt

    def p_if_stmt3(self, p):
        ''' if_stmt : IF test COLON suite else_stmt '''
        if_stmt = ast.If()
        if_stmt.test = p[2]
        if_stmt.body = p[4]
        if_stmt.lineno = p.lineno(1)
        if_stmt.orelse = p[5]
        ast.fix_missing_locations(if_stmt)
        p[0] = if_stmt

    def p_if_stmt4(self, p):
        ''' if_stmt : IF test COLON suite elif_stmts else_stmt '''
        if_stmt = ast.If()
        if_stmt.test = p[2]
        if_stmt.body = p[4]
        if_stmt.lineno = p.lineno(1)
        elif_stmt = p[5]
        if_stmt.orelse = [elif_stmt]
        else_stmt = p[6]
        while elif_stmt.orelse:
            elif_stmt = elif_stmt.orelse[0]
        elif_stmt.orelse = else_stmt
        ast.fix_missing_locations(if_stmt)
        p[0] = if_stmt

    def p_elif_stmts1(self, p):
        ''' elif_stmts : elif_stmt elif_stmts '''
        elif_stmt = p[1]
        elif_stmt.orelse = [p[2]]
        p[0] = elif_stmt

    def p_elif_stmts2(self, p):
        ''' elif_stmts : elif_stmt '''
        p[0] = p[1]

    def p_elif_stmt(self, p):
        ''' elif_stmt : ELIF test COLON suite '''
        if_stmt = ast.If()
        if_stmt.test = p[2]
        if_stmt.body = p[4]
        if_stmt.lineno = p.lineno(1)
        if_stmt.orelse = []
        ast.fix_missing_locations(if_stmt)
        p[0] = if_stmt

    def p_else_stmt(self, p):
        ''' else_stmt : ELSE COLON suite '''
        p[0] = p[3]

    def p_while_stmt1(self, p):
        ''' while_stmt : WHILE test COLON suite '''
        while_stmt = ast.While()
        while_stmt.test = p[2]
        while_stmt.body = p[4]
        while_stmt.orelse = []
        while_stmt.lineno = p.lineno(1)
        ast.fix_missing_locations(while_stmt)
        p[0] = while_stmt

    def p_while_stmt2(self, p):
        ''' while_stmt : WHILE test COLON suite ELSE COLON suite '''
        while_stmt = ast.While()
        while_stmt.test = p[2]
        while_stmt.body = p[4]
        while_stmt.orelse = p[7]
        while_stmt.lineno = p.lineno(1)
        ast.fix_missing_locations(while_stmt)
        p[0] = while_stmt

    def p_for_stmt1(self, p):
        ''' for_stmt : FOR exprlist IN testlist COLON suite '''
        for_stmt = ast.For()
        target = p[2]
        self.set_context(target, Store, p)
        for_stmt.target = target
        for_stmt.iter = ast_for_testlist(p[4])
        for_stmt.body = p[6]
        for_stmt.orelse = []
        for_stmt.lineno = p.lineno(1)
        ast.fix_missing_locations(for_stmt)
        p[0] = for_stmt

    def p_for_stmt2(self, p):
        ''' for_stmt : FOR exprlist IN testlist COLON suite ELSE COLON suite '''
        for_stmt = ast.For()
        target = p[2]
        self.set_context(target, Store, p)
        for_stmt.target = target
        for_stmt.iter = ast_for_testlist(p[4])
        for_stmt.body = p[6]
        for_stmt.orelse = p[9]
        for_stmt.lineno = p.lineno(1)
        ast.fix_missing_locations(for_stmt)
        p[0] = for_stmt

    def p_try_stmt1(self, p):
        ''' try_stmt : TRY COLON suite FINALLY COLON suite '''
        if IS_PY3:
            try_finally = ast.Try()
            try_finally.handlers = []
            try_finally.orelse = []
        else:
            try_finally = ast.TryFinally()
        try_finally.body = p[3]
        try_finally.finalbody = p[6]
        try_finally.lineno = p.lineno(1)
        ast.fix_missing_locations(try_finally)
        p[0] = try_finally

    def p_try_stmt2(self, p):
        ''' try_stmt : TRY COLON suite except_clauses '''
        if IS_PY3:
            try_stmt = ast.Try()
            try_stmt.finalbody = []
        else:
            try_stmt = ast.TryExcept()
        try_stmt.body = p[3]
        try_stmt.handlers = p[4]
        try_stmt.orelse = []
        try_stmt.lineno = p.lineno(1)
        ast.fix_missing_locations(try_stmt)
        p[0] = try_stmt

    def p_try_stmt3(self, p):
        ''' try_stmt : TRY COLON suite except_clauses ELSE COLON suite '''
        if IS_PY3:
            try_stmt = ast.Try()
            try_stmt.finalbody = []
        else:
            try_stmt = ast.TryExcept()
        try_stmt.body = p[3]
        try_stmt.handlers = p[4]
        try_stmt.orelse = p[7]
        try_stmt.lineno = p.lineno(1)
        ast.fix_missing_locations(try_stmt)
        p[0] = try_stmt

    def p_try_stmt4(self, p):
        ''' try_stmt : TRY COLON suite except_clauses FINALLY COLON suite '''
        lineno = p.lineno(1)
        if IS_PY3:
            try_finally = ast.Try()
            try_stmt = try_finally
        else:
            try_finally = ast.TryFinally()
            try_stmt = ast.TryExcept()
            try_stmt.lineno = lineno
        try_stmt.body = p[3]
        try_stmt.handlers = p[4]
        try_stmt.orelse = []
        if not IS_PY3:
            ast.fix_missing_locations(try_stmt)
            try_finally.body = [try_stmt]
        try_finally.finalbody = p[7]
        try_finally.lineno = lineno
        ast.fix_missing_locations(try_finally)
        p[0] = try_finally

    def p_try_stmt5(self, p):
        ''' try_stmt : TRY COLON suite except_clauses ELSE COLON suite FINALLY COLON suite '''
        lineno = p.lineno(1)
        if IS_PY3:
            try_finally = ast.Try()
            try_stmt = try_finally
        else:
            try_finally = ast.TryFinally()
            try_stmt = ast.TryExcept()
            try_stmt.lineno = lineno
        try_stmt.body = p[3]
        try_stmt.handlers = p[4]
        try_stmt.orelse = p[7]
        if not IS_PY3:
            try_stmt.lineno = lineno
            ast.fix_missing_locations(try_stmt)
            try_finally.body = [try_stmt]
        try_finally.finalbody = p[10]
        try_finally.lineno = lineno
        ast.fix_missing_locations(try_finally)
        p[0] = try_finally

    def p_except_clauses1(self, p):
        ''' except_clauses : except_clause except_clauses '''
        p[0] = [p[1]] + p[2]

    def p_except_clauses2(self, p):
        ''' except_clauses : except_clause '''
        p[0] = [p[1]]

    def p_except_clause1(self, p):
        ''' except_clause : EXCEPT COLON suite '''
        excpt = ast.ExceptHandler()
        excpt.type = None
        excpt.name = None
        excpt.body = p[3]
        excpt.lineno = p.lineno(1)
        ast.fix_missing_locations(excpt)
        p[0] = excpt

    def p_except_clause2(self, p):
        ''' except_clause : EXCEPT test COLON suite '''
        excpt = ast.ExceptHandler()
        excpt.type = p[2]
        excpt.name = None
        excpt.body = p[4]
        excpt.lineno = p.lineno(1)
        ast.fix_missing_locations(excpt)
        p[0] = excpt

    def p_except_clause3(self, p):
        ''' except_clause : EXCEPT test AS test COLON suite
                          | EXCEPT test COMMA test COLON suite '''
        excpt = ast.ExceptHandler()
        excpt.type = p[2]
        if IS_PY3:
            name = p[4].id
        else:
            name = p[4]
            self.set_context(name, Store, p)
        excpt.name = name
        excpt.body = p[6]
        excpt.lineno = p.lineno(1)
        ast.fix_missing_locations(excpt)
        p[0] = excpt

    def p_with_stmt1(self, p):
        ''' with_stmt : WITH with_item COLON suite '''
        with_stmt = ast.With()
        ctxt, opt_vars = p[2]
        if IS_PY3:
            with_stmt.items = [ast.withitem(context_expr=ctxt,
                                            optional_vars=opt_vars)]
        else:
            with_stmt.context_expr = ctxt
            with_stmt.optional_vars = opt_vars
        with_stmt.body = p[4]
        with_stmt.lineno = p.lineno(1)
        ast.fix_missing_locations(with_stmt)
        p[0] = with_stmt

    def p_with_stmt2(self, p):
        ''' with_stmt : WITH with_item with_item_list COLON suite '''
        with_stmt = ast.With()
        if IS_PY3:
            items = list()
            ctxt, opt_vars = p[2]
            items.append(ast.withitem(context_expr=ctxt,
                                      optional_vars=opt_vars))
            for ctxt, opt_vars in p[3]:
                items.append(ast.withitem(context_expr=ctxt,
                                          optional_vars=opt_vars))

            with_stmt.items = items
        else:
            ctxt, opt_vars = p[2]
            with_stmt.context_expr = ctxt
            with_stmt.optional_vars = opt_vars
            last = with_stmt
            for ctxt, opt_vars in p[3]:
                with_stmt = ast.With()
                with_stmt.context_expr = ctxt
                with_stmt.optional_vars = opt_vars
                last.body = [with_stmt]
                last = with_stmt
        with_stmt.body = p[5]
        with_stmt.lineno = p.lineno(1)
        ast.fix_missing_locations(with_stmt)
        p[0] = with_stmt

    def p_with_item1(self, p):
        ''' with_item : test '''
        p[0] = (p[1], None)

    def p_with_item2(self, p):
        ''' with_item : test AS expr '''
        expr = p[3]
        self.set_context(expr, Store, p)
        p[0] = (p[1], expr)

    def p_with_item_list1(self, p):
        ''' with_item_list : COMMA with_item with_item_list '''
        p[0] = [p[2]] + p[3]

    def p_with_item_list2(self, p):
        ''' with_item_list : COMMA with_item '''
        p[0] = [p[2]]

    def p_funcdef(self, p):
        ''' funcdef : DEF NAME parameters COLON suite '''
        funcdef = ast.FunctionDef()
        funcdef.name = p[2]
        funcdef.args = p[3]
        if IS_PY3:
            funcdef.returns = None
        funcdef.body = p[5]
        funcdef.decorator_list = []
        funcdef.lineno = p.lineno(1)
        ast.fix_missing_locations(funcdef)
        p[0] = funcdef

    def p_parameters1(self, p):
        ''' parameters : LPAR RPAR '''
        p[0] = self._make_args([])

    def p_parameters2(self, p):
        ''' parameters : LPAR varargslist RPAR '''
        p[0] = p[2]

    def p_classdef1(self, p):
        ''' classdef : CLASS NAME COLON suite '''
        classdef = ast.ClassDef(keywords=[])
        classdef.name = p[2]
        classdef.bases = []
        classdef.body = p[4]
        classdef.decorator_list = []
        classdef.lineno = p.lineno(1)
        ast.fix_missing_locations(classdef)
        p[0] = classdef

    def p_classdef2(self, p):
        ''' classdef : CLASS NAME LPAR RPAR COLON suite '''
        classdef = ast.ClassDef(keywords=[])
        classdef.name = p[2]
        classdef.bases = []
        classdef.body = p[6]
        classdef.decorator_list = []
        classdef.lineno = p.lineno(1)
        ast.fix_missing_locations(classdef)
        p[0] = classdef

    def p_decorated(self, p):
        ''' decorated : decorators funcdef
                      | decorators classdef '''
        decs = p[1]
        target = p[2]
        target.decorator_list = decs
        p[0] = target

    def p_decorators1(self, p):
        ''' decorators : decorator decorators '''
        p[0] = [p[1]] + p[2]

    def p_decorators2(self, p):
        ''' decorators : decorator '''
        p[0] = [p[1]]

    def p_decorator1(self, p):
        ''' decorator : AT dotted_name NEWLINE '''
        name = ast_for_dotted_name(p[2])
        name.lineno = p.lineno(1)
        ast.fix_missing_locations(name)
        p[0] = name

    def p_decorator2(self, p):
        ''' decorator : AT dotted_name LPAR RPAR NEWLINE '''
        call = ast.Call()
        call.func = ast_for_dotted_name(p[2])
        self.set_call_arguments(call, Arguments())
        call.lineno = p.lineno(1)
        ast.fix_missing_locations(call)
        p[0] = call

    def p_decorator3(self, p):
        ''' decorator : AT dotted_name LPAR arglist RPAR NEWLINE '''
        args = p[4]
        call = ast.Call()
        call.func = ast_for_dotted_name(p[2])
        self.set_call_arguments(call, args)
        call.lineno = p.lineno(1)
        ast.fix_missing_locations(call)
        p[0] = call

    def p_import_stmt1(self, p):
        ''' import_stmt : import_name '''
        p[0] = p[1]

    def p_import_stmt2(self, p):
        ''' import_stmt : import_from '''
        p[0] = p[1]

    def p_import_name(self, p):
        ''' import_name : IMPORT dotted_as_names '''
        imprt = ast.Import(names=p[2])
        imprt.col_offset = 0
        p[0] = imprt

    def p_import_from1(self, p):
        ''' import_from : FROM dotted_name IMPORT STAR '''
        alias = ast.alias(name=p[4], asname=None)
        imprt = ast.ImportFrom(module=p[2], names=[alias], level=0)
        imprt.col_offset = 0
        p[0] = imprt

    def p_import_from2(self, p):
        ''' import_from : FROM dotted_name IMPORT import_as_names '''
        imprt = ast.ImportFrom(module=p[2], names=p[4], level=0)
        imprt.col_offset = 0
        p[0] = imprt

    def p_import_from3(self, p):
        ''' import_from : FROM dotted_name IMPORT LPAR import_as_names RPAR '''
        imprt = ast.ImportFrom(module=p[2], names=p[5], level=0)
        imprt.col_offset = 0
        p[0] = imprt

    def p_import_from4(self, p):
        ''' import_from : FROM import_from_dots dotted_name IMPORT STAR '''
        alias = ast.alias(name=p[5], asname=None)
        imprt = ast.ImportFrom(module=p[3], names=[alias], level=len(p[2]))
        imprt.col_offset = 0
        p[0] = imprt

    def p_import_from5(self, p):
        ''' import_from : FROM import_from_dots dotted_name IMPORT import_as_names '''
        imprt = ast.ImportFrom(module=p[3], names=p[5], level=len(p[2]))
        imprt.col_offset = 0
        p[0] = imprt

    def p_import_from6(self, p):
        ''' import_from : FROM import_from_dots dotted_name IMPORT LPAR import_as_names RPAR '''
        imprt = ast.ImportFrom(module=p[3], names=p[6], level=len(p[2]))
        imprt.col_offset = 0
        p[0] = imprt

    def p_import_from7(self, p):
        ''' import_from : FROM import_from_dots IMPORT STAR '''
        alias = ast.alias(name=p[4], asname=None)
        imprt = ast.ImportFrom(module=None, names=[alias], level=len(p[2]))
        imprt.col_offset = 0
        p[0] = imprt

    def p_import_from8(self, p):
        ''' import_from : FROM import_from_dots IMPORT import_as_names '''
        imprt = ast.ImportFrom(module=None, names=p[4], level=len(p[2]))
        imprt.col_offset = 0
        p[0] = imprt

    def p_import_from9(self, p):
        ''' import_from : FROM import_from_dots IMPORT LPAR import_as_names RPAR '''
        imprt = ast.ImportFrom(module=None, names=p[5], level=len(p[2]))
        imprt.col_offset = 0
        p[0] = imprt

    def p_import_from_dots1(self, p):
        ''' import_from_dots : DOT '''
        p[0] = [p[1]]

    def p_import_from_dots2(self, p):
        ''' import_from_dots : import_from_dots DOT '''
        p[0] = p[1] + [p[2]]

    def p_import_from_dots3(self, p):
        ''' import_from_dots : ELLIPSIS '''
        p[0] = ['.', '.', '.']

    def p_import_from_dots4(self, p):
        ''' import_from_dots : import_from_dots ELLIPSIS '''
        p[0] = p[1] + ['.', '.', '.']

    def p_import_as_name1(self, p):
        ''' import_as_name : NAME '''
        p[0] = ast.alias(name=p[1], asname=None)

    def p_import_as_name2(self, p):
        ''' import_as_name : NAME AS NAME '''
        p[0] = ast.alias(name=p[1], asname=p[3])

    def p_dotted_as_name1(self, p):
        ''' dotted_as_name : dotted_name '''
        alias = ast.alias(name=p[1], asname=None)
        p[0] = alias

    def p_dotted_as_name2(self, p):
        ''' dotted_as_name : dotted_name AS NAME '''
        alias = ast.alias(name=p[1], asname=p[3])
        p[0] = alias

    def p_import_as_names1(self, p):
        ''' import_as_names : import_as_name '''
        p[0] = [p[1]]

    def p_import_as_names2(self, p):
        ''' import_as_names : import_as_name COMMA '''
        p[0] = [p[1]]

    def p_import_as_names3(self, p):
        ''' import_as_names : import_as_name import_as_names_list '''
        p[0] = [p[1]] + p[2]

    def p_import_as_names4(self, p):
        ''' import_as_names : import_as_name import_as_names_list COMMA '''
        p[0] = [p[1]] + p[2]

    def p_import_as_names_list1(self, p):
        ''' import_as_names_list : COMMA import_as_name '''
        p[0] = [p[2]]

    def p_import_as_names_list2(self, p):
        ''' import_as_names_list : import_as_names_list COMMA import_as_name '''
        p[0] = p[1] + [p[3]]

    def p_dotted_as_names1(self, p):
        ''' dotted_as_names : dotted_as_name '''
        p[0] = [p[1]]

    def p_dotted_as_names2(self, p):
        ''' dotted_as_names : dotted_as_name dotted_as_names_list '''
        p[0] = [p[1]] + p[2]

    def p_dotted_as_names_list1(self, p):
        ''' dotted_as_names_list : COMMA dotted_as_name '''
        p[0] = [p[2]]

    def p_dotted_as_names_star_list2(self, p):
        ''' dotted_as_names_list : dotted_as_names_list COMMA dotted_as_name '''
        p[0] = p[1] + [p[3]]

    def p_dotted_name1(self, p):
        ''' dotted_name : NAME '''
        p[0] = p[1]

    def p_dotted_name2(self, p):
        ''' dotted_name : NAME dotted_name_list '''
        p[0] = p[1] + p[2]

    def p_dotted_name_list1(self, p):
        ''' dotted_name_list : DOT NAME '''
        p[0] = p[1] + p[2]

    def p_dotted_name_list2(self, p):
        ''' dotted_name_list : dotted_name_list DOT NAME '''
        p[0] = p[1] + p[2] + p[3]

    def p_test1(self, p):
        ''' test : or_test '''
        p[0] = p[1]

    def p_test2(self, p):
        ''' test : or_test IF or_test ELSE test '''
        ifexp = ast.IfExp(body=p[1], test=p[3], orelse=p[5])
        p[0] = ifexp

    def p_test3(self, p):
        ''' test : lambdef '''
        p[0] = p[1]

    def p_or_test1(self, p):
        ''' or_test : and_test '''
        p[0] = p[1]

    def p_or_test2(self, p):
        ''' or_test : and_test or_test_list '''
        values = [p[1]] + p[2]
        or_node = ast.BoolOp(op=ast.Or(), values=values)
        p[0] = or_node

    def p_or_test_list1(self, p):
        ''' or_test_list : OR and_test '''
        p[0] = [p[2]]

    def p_or_test_list2(self, p):
        ''' or_test_list : or_test_list OR and_test '''
        p[0] = p[1] + [p[3]]

    def p_and_test1(self, p):
        ''' and_test : not_test '''
        p[0] = p[1]

    def p_and_test2(self, p):
        ''' and_test : not_test and_test_list '''
        values = [p[1]] + p[2]
        and_node = ast.BoolOp(op=ast.And(), values=values)
        p[0] = and_node

    def p_and_test_list1(self, p):
        ''' and_test_list : AND not_test '''
        p[0] = [p[2]]

    def p_and_test_list2(self, p):
        ''' and_test_list : and_test_list AND not_test '''
        p[0] = p[1] + [p[3]]

    def p_not_test(self, p):
        ''' not_test : comparison '''
        p[0] = p[1]

    def p_not_test2(self, p):
        ''' not_test : NOT not_test '''
        un_node = ast.UnaryOp(op=ast.Not(), operand=p[2])
        p[0] = un_node

    def p_comparison1(self, p):
        ''' comparison : expr '''
        p[0] = p[1]

    def p_comparison2(self, p):
        ''' comparison : expr comparison_list '''
        left = p[1]
        ops, comparators = list(zip(*p[2]))
        cmpr = ast.Compare(left=left, ops=list(ops),
                           comparators=list(comparators))
        p[0] = cmpr

    def p_comparison_list1(self, p):
        ''' comparison_list : comp_op expr '''
        p[0] = [[p[1], p[2]]]

    def p_comparison_list2(self, p):
        ''' comparison_list : comparison_list comp_op expr '''
        p[0] = p[1] + [[p[2], p[3]]]

    def p_comp_op1(self, p):
        ''' comp_op : LESS '''
        p[0] = ast.Lt()

    def p_comp_op2(self, p):
        ''' comp_op : GREATER '''
        p[0] = ast.Gt()

    def p_comp_op3(self, p):
        ''' comp_op : EQEQUAL '''
        p[0] = ast.Eq()

    def p_comp_op4(self, p):
        ''' comp_op : GREATEREQUAL '''
        p[0] = ast.GtE()

    def p_comp_op5(self, p):
        ''' comp_op : LESSEQUAL '''
        p[0] = ast.LtE()

    def p_comp_op6(self, p):
        ''' comp_op : NOTEQUAL '''
        p[0] = ast.NotEq()

    def p_comp_op7(self, p):
        ''' comp_op : IN '''
        p[0] = ast.In()

    def p_comp_op8(self, p):
        ''' comp_op : NOT IN '''
        p[0] = ast.NotIn()

    def p_comp_op9(self, p):
        ''' comp_op : IS '''
        p[0] = ast.Is()

    def p_comp_op10(self, p):
        ''' comp_op : IS NOT '''
        p[0] = ast.IsNot()

    def p_expr1(self, p):
        ''' expr : xor_expr '''
        p[0] = p[1]

    def p_expr2(self, p):
        ''' expr : xor_expr expr_list '''
        node = p[1]
        for op, right in p[2]:
            node = ast.BinOp(left=node, op=op, right=right)
        p[0] = node

    def p_expr_list1(self, p):
        ''' expr_list : VBAR xor_expr '''
        p[0] = [[ast.BitOr(), p[2]]]

    def p_expr_list2(self, p):
        ''' expr_list : expr_list VBAR xor_expr '''
        p[0] = p[1] + [[ast.BitOr(), p[3]]]

    def p_xor_expr1(self, p):
        ''' xor_expr : and_expr '''
        p[0] = p[1]

    def p_xor_expr2(self, p):
        ''' xor_expr : and_expr xor_expr_list '''
        node = p[1]
        for op, right in p[2]:
            node = ast.BinOp(left=node, op=op, right=right)
        p[0] = node

    def p_xor_expr_list1(self, p):
        ''' xor_expr_list : CIRCUMFLEX and_expr '''
        p[0] = [[ast.BitXor(), p[2]]]

    def p_xor_expr_list2(self, p):
        ''' xor_expr_list : xor_expr_list CIRCUMFLEX and_expr '''
        p[0] = p[1] + [[ast.BitXor(), p[3]]]

    def p_and_expr1(self, p):
        ''' and_expr : shift_expr '''
        p[0] = p[1]

    def p_and_expr2(self, p):
        ''' and_expr : shift_expr and_expr_list '''
        node = p[1]
        for op, right in p[2]:
            node = ast.BinOp(left=node, op=op, right=right)
        p[0] = node

    def p_and_expr_list1(self, p):
        ''' and_expr_list : AMPER shift_expr '''
        p[0] = [[ast.BitAnd(), p[2]]]

    def p_and_expr_list2(self, p):
        ''' and_expr_list : and_expr_list AMPER shift_expr '''
        p[0] = p[1] + [[ast.BitAnd(), p[3]]]

    def p_shift_expr1(self, p):
        ''' shift_expr : arith_expr '''
        p[0] = p[1]

    def p_shift_expr2(self, p):
        ''' shift_expr : arith_expr shift_list '''
        node = p[1]
        for op, right in p[2]:
            node = ast.BinOp(left=node, op=op, right=right)
        p[0] = node

    def p_shift_list1(self, p):
        ''' shift_list : shift_op '''
        p[0] = [p[1]]

    def p_shift_list2(self, p):
        ''' shift_list : shift_list shift_op '''
        p[0] = p[1] + [p[2]]

    def p_shift_op1(self, p):
        ''' shift_op : LEFTSHIFT arith_expr '''
        p[0] = [ast.LShift(), p[2]]

    def p_shift_op2(self, p):
        ''' shift_op : RIGHTSHIFT arith_expr '''
        p[0] = [ast.RShift(), p[2]]

    def p_arith_expr1(self, p):
        ''' arith_expr : term '''
        p[0] = p[1]

    def p_arith_expr2(self, p):
        ''' arith_expr : term arith_expr_list '''
        node = p[1]
        for op, right in p[2]:
            node = ast.BinOp(left=node, op=op, right=right)
        p[0] = node

    def p_arith_expr_list1(self, p):
        ''' arith_expr_list : arith_op '''
        p[0] = [p[1]]

    def p_arith_expr_list2(self, p):
        ''' arith_expr_list : arith_expr_list arith_op '''
        p[0] = p[1] + [p[2]]

    def p_arith_op1(self, p):
        ''' arith_op : PLUS term '''
        node = ast.Add()
        p[0] = [node, p[2]]

    def p_arith_op2(self, p):
        ''' arith_op : MINUS term '''
        p[0] = [ast.Sub(), p[2]]

    def p_term1(self, p):
        ''' term : factor '''
        p[0] = p[1]

    def p_term2(self, p):
        ''' term : factor term_list '''
        node = p[1]
        for op, right in p[2]:
            node = ast.BinOp(left=node, op=op, right=right)
        p[0] = node

    def p_term_list1(self, p):
        ''' term_list : term_op '''
        p[0] = [p[1]]

    def p_term_list2(self, p):
        ''' term_list : term_list term_op '''
        p[0] = p[1] + [p[2]]

    def p_term_op1(self, p):
        ''' term_op : STAR factor '''
        p[0] = [ast.Mult(), p[2]]

    def p_term_op2(self, p):
        ''' term_op : SLASH factor '''
        p[0] = [ast.Div(), p[2]]

    def p_term_op3(self, p):
        ''' term_op : PERCENT factor '''
        p[0] = [ast.Mod(), p[2]]

    def p_term_op4(self, p):
        ''' term_op : DOUBLESLASH factor '''
        p[0] = [ast.FloorDiv(), p[2]]

    def p_factor1(self, p):
        ''' factor : power '''
        p[0] = p[1]

    def p_factor2(self, p):
        ''' factor : PLUS factor '''
        op = ast.UAdd()
        operand = p[2]
        node = ast.UnaryOp(op=op, operand=operand)
        p[0] = node

    def p_factor3(self, p):
        ''' factor : MINUS factor '''
        op = ast.USub()
        operand = p[2]
        node = ast.UnaryOp(op=op, operand=operand)
        p[0] = node

    def p_factor4(self, p):
        ''' factor : TILDE factor '''
        op = ast.Invert()
        operand = p[2]
        node = ast.UnaryOp(op=op, operand=operand)
        p[0] = node

    def p_power1(self, p):
        ''' power : atom_expr '''
        p[0] = p[1]

    def p_power2(self, p):
        ''' power : atom_expr DOUBLESTAR factor '''
        node = ast.BinOp(left=p[1], op=ast.Pow(), right=p[3])
        p[0] = node

    def p_atom_expr1(self, p):
        ''' atom_expr : atom '''
        p[0] = p[1]

    def p_atom_expr2(self, p):
        ''' atom_expr : atom trailer_list '''
        root = p[1]
        for node in p[2]:
            if isinstance(node, ast.Call):
                node.func = root
            elif isinstance(node, ast.Attribute):
                node.value = root
            elif isinstance(node, ast.Subscript):
                node.value = root
            else:
                raise TypeError('Unexpected trailer node: %s' % node)
            root = node
        p[0] = node

    def p_trailer_list1(self, p):
        ''' trailer_list : trailer '''
        p[0] = [p[1]]

    def p_trailer_list2(self, p):
        ''' trailer_list : trailer_list trailer '''
        p[0] = p[1] + [p[2]]

    def p_atom1(self, p):
        ''' atom : LPAR RPAR '''
        p[0] = ast.Tuple(elts=[], ctx=Load)

    def p_atom2(self, p):
        ''' atom : LPAR yield_expr RPAR '''
        p[0] = p[2]

    def p_atom3(self, p):
        ''' atom : LPAR testlist_comp RPAR '''
        info = p[2]
        if isinstance(info, CommaSeparatedList):
            node = ast.Tuple(elts=info.values, ctx=Load)
        elif isinstance(info, GeneratorInfo):
            node = ast.GeneratorExp(elt=info.elt, generators=info.generators)
        else:
            # We have a test node by itself in parenthesis controlling
            # order of operations, so just return the node.
            node = info
        p[0] = node

    def p_atom4(self, p):
        ''' atom : LSQB RSQB '''
        p[0] = ast.List(elts=[], ctx=Load)

    def p_atom5(self, p):
        ''' atom : LSQB testlist_comp RSQB '''
        info = p[2]
        if isinstance(info, CommaSeparatedList):
            node = ast.List(elts=info.values, ctx=Load)
        elif isinstance(info, GeneratorInfo):
            node = ast.ListComp(elt=info.elt, generators=info.generators)
        else:
            node = ast.List(elts=[info], ctx=Load)
        p[0] = node

    def p_atom6(self, p):
        ''' atom : LBRACE RBRACE '''
        p[0] = ast.Dict(keys=[], values=[])

    def p_atom7(self, p):
        ''' atom : LBRACE dictorsetmaker RBRACE '''
        info = p[2]
        if isinstance(info, GeneratorInfo):
            if isinstance(info.elt, tuple):
                key, value = info.elt
                generators = info.generators
                node = DictComp(key=key, value=value, generators=generators)
            else:
                node = SetComp(elt=info.elt, generators=info.generators)
        elif isinstance(info, CommaSeparatedList):
            if isinstance(info.values[0], tuple):
                keys, values = list(zip(*info.values))
                node = ast.Dict(keys=list(keys), values=list(values))
            else:
                node = Set(elts=info.values)
        else:
            raise TypeError('Unexpected node for dictorsetmaker: %s' % info)
        p[0] = node

    def p_atom8(self, p):
        ''' atom : NAME '''
        p[0] = ast.Name(id=p[1], ctx=Load, lineno=p.lineno(1))

    def p_atom9(self, p):
        ''' atom : NUMBER '''
        n = ast.Num(n=eval(p[1]))
        p[0] = n

    def p_atom10(self, p):
        ''' atom : atom_string_list '''
        s = ast.Str(s=p[1])
        p[0] = s

    def p_atom_string_list1(self, p):
        ''' atom_string_list : STRING '''
        p[0] = p[1]

    def p_atom_string_list2(self, p):
        ''' atom_string_list : atom_string_list STRING '''
        p[0] = p[1] + p[2]

    # We dont' allow the backquote atom from standard Python. Just
    # use repr(...). This simplifies the grammar since we don't have
    # to define a testlist1.

    def p_testlist_comp1(self, p):
        ''' testlist_comp : test_or_star comp_for '''
        p[0] = GeneratorInfo(elt=p[1], generators=p[2])

    def p_testlist_comp2(self, p):
        ''' testlist_comp : test_or_star '''
        p[0] = p[1]

    def p_testlist_comp3(self, p):
        ''' testlist_comp : test_or_star COMMA '''
        p[0] = CommaSeparatedList(values=[p[1]])

    def p_testlist_comp4(self, p):
        ''' testlist_comp : test_or_star testlist_comp_list '''
        values = [p[1]] + p[2]
        p[0] = CommaSeparatedList(values=values)

    def p_testlist_comp5(self, p):
        ''' testlist_comp : test_or_star testlist_comp_list COMMA '''
        values = [p[1]] + p[2]
        p[0] = CommaSeparatedList(values=values)

    def p_testlist_comp_list1(self, p):
        ''' testlist_comp_list : COMMA test_or_star '''
        p[0] = [p[2]]

    def p_testlist_comp_list2(self, p):
        ''' testlist_comp_list : testlist_comp_list COMMA test_or_star '''
        p[0] = p[1] + [p[3]]

    def p_trailer1(self, p):
        ''' trailer : LPAR RPAR '''
        p[0] = ast.Call(args=[], keywords=[], starargs=None, kwargs=None)

    def p_trailer2(self, p):
        ''' trailer : LPAR arglist RPAR '''
        args = p[2]
        call = ast.Call()
        self.set_call_arguments(call, args)
        p[0] = call

    def p_trailer3(self, p):
        ''' trailer : LSQB subscriptlist RSQB '''
        p[0] = ast.Subscript(slice=p[2], ctx=Load)

    def p_trailer4(self, p):
        ''' trailer : DOT NAME '''
        p[0] = ast.Attribute(attr=p[2], ctx=Load, lineno=p.lineno(2))

    def p_subscriptlist1(self, p):
        ''' subscriptlist : subscript '''
        p[0] = p[1]

    def p_subscriptlist2(self, p):
        ''' subscriptlist : subscript COMMA '''
        dims = [p[1]]
        p[0] = ast.ExtSlice(dims=dims)

    def p_subscriptlist3(self, p):
        ''' subscriptlist : subscript subscriptlist_list '''
        dims = [p[1]] + p[2]
        p[0] = ast.ExtSlice(dims=dims)

    def p_subscriptlist4(self, p):
        ''' subscriptlist : subscript subscriptlist_list COMMA '''
        dims = [p[1]] + p[2]
        p[0] = ast.ExtSlice(dims=dims)

    def p_subscriptlist_list1(self, p):
        ''' subscriptlist_list : COMMA subscript '''
        p[0] = [p[2]]

    def p_subscript_list2(self, p):
        ''' subscriptlist_list : subscriptlist_list COMMA subscript '''
        p[0] = p[1] + [p[3]]

    def p_subscript1(self, p):
        ''' subscript : ELLIPSIS '''
        p[0] = ast.Ellipsis()

    def p_subcript2(self, p):
        ''' subscript : test '''
        p[0] = ast.Index(value=p[1])

    def p_subscript3(self, p):
        ''' subscript : COLON '''
        p[0] = ast.Slice(lower=None, upper=None, step=None)

    def p_subscript4(self, p):
        ''' subscript : DOUBLECOLON '''
        name = ast.Name(id='None', ctx=Load)
        p[0] = ast.Slice(lower=None, upper=None, step=name)

    def p_subscript5(self, p):
        ''' subscript : test COLON '''
        p[0] = ast.Slice(lower=p[1], uppper=None, step=None)

    def p_subscrip6(self, p):
        ''' subscript : test DOUBLECOLON '''
        name = ast.Name(id='None', ctx=Load)
        p[0] = ast.Slice(lower=p[1], upper=None, step=name)

    def p_subscript7(self, p):
        ''' subscript : COLON test '''
        p[0] = ast.Slice(lower=None, upper=p[2], step=None)

    def p_subscript8(self, p):
        ''' subscript : COLON test COLON '''
        name = ast.Name(id='None', ctx=Load)
        p[0] = ast.Slice(lower=None, upper=p[2], step=name)

    def p_subscript9(self, p):
        ''' subscript : DOUBLECOLON test '''
        p[0] = ast.Slice(lower=None, upper=None, step=p[2])

    def p_subscript10(self, p):
        ''' subscript : test COLON test '''
        p[0] = ast.Slice(lower=p[1], upper=p[3], step=None)

    def p_subscript11(self, p):
        ''' subscript : test COLON test COLON '''
        name = ast.Name(id='None', ctx=Load)
        p[0] = ast.Slice(lower=p[1], upper=p[3], step=name)

    def p_subscript12(self, p):
        ''' subscript : COLON test COLON test '''
        p[0] = ast.Slice(lower=None, upper=p[2], step=p[4])

    def p_subscript13(self, p):
        ''' subscript : test COLON test COLON test '''
        p[0] = ast.Slice(lower=p[1], upper=p[3], step=p[5])

    def p_subscript14(self, p):
        ''' subscript : test DOUBLECOLON test '''
        p[0] = ast.Slice(lower=p[1], upper=None, step=p[3])

    def p_exprlist1(self, p):
        ''' exprlist : expr '''
        p[0] = p[1]

    def p_exprlist2(self, p):
        ''' exprlist : expr COMMA '''
        tup = ast.Tuple()
        tup.elts = [p[1]]
        p[0] = tup

    def p_exprlist3(self, p):
        ''' exprlist : expr exprlist_list '''
        tup = ast.Tuple()
        tup.elts = [p[1]] + p[2]
        p[0] = tup

    def p_exprlist4(self, p):
        ''' exprlist : expr exprlist_list COMMA '''
        tup = ast.Tuple()
        tup.elts = [p[1]] + p[2]
        p[0] = tup

    def p_exprlist_list1(self, p):
        ''' exprlist_list : COMMA expr '''
        p[0] = [p[2]]

    def p_exprlist_list2(self, p):
        ''' exprlist_list : exprlist_list COMMA expr '''
        p[0] = p[1] + [p[3]]

    def p_dictorsetmaker1(self, p):
        ''' dictorsetmaker : dosm_colon comp_for '''
        p[0] = GeneratorInfo(elt=p[1], generators=p[2])

    def p_dictorsetmaker2(self, p):
        ''' dictorsetmaker : dosm_colon '''
        values = [p[1]]
        p[0] = CommaSeparatedList(values=values)

    def p_dictorsetmaker3(self, p):
        ''' dictorsetmaker : dosm_colon COMMA '''
        p[0] = CommaSeparatedList(values=[p[1]])

    def p_dictorsetmaker4(self, p):
        ''' dictorsetmaker : dosm_colon dosm_colon_list '''
        values = [p[1]] + p[2]
        p[0] = CommaSeparatedList(values=values)

    def p_dictorsetmaker5(self, p):
        ''' dictorsetmaker : dosm_colon dosm_colon_list COMMA '''
        values = [p[1]] + p[2]
        p[0] = CommaSeparatedList(values=values)

    def p_dictorsetmaker6(self, p):
        ''' dictorsetmaker : test_or_star_new comp_for '''
        p[0] = GeneratorInfo(elt=p[1], generators=p[2])

    def p_dictorsetmaker7(self, p):
        ''' dictorsetmaker : test_or_star_new COMMA '''
        values = [p[1]]
        p[0] = CommaSeparatedList(values=values)

    def p_dictorsetmaker8(self, p):
        ''' dictorsetmaker : test_or_star_new dosm_comma_list '''
        values = [p[1]] + p[2]
        p[0] = CommaSeparatedList(values=values)

    def p_dictorsetmaker9(self, p):
        ''' dictorsetmaker : test_or_star_new dosm_comma_list COMMA '''
        values = [p[1]] + p[2]
        p[0] = CommaSeparatedList(values=values)

    def p_dosm_colon1(self, p):
        ''' dosm_colon : test COLON test '''
        p[0] = (p[1], p[3])

    def p_dosm_colon_list1(self, p):
        ''' dosm_colon_list : COMMA dosm_colon '''
        p[0] = [p[2]]

    def p_dosm_colon_list2(self, p):
        ''' dosm_colon_list : dosm_colon_list COMMA dosm_colon '''
        p[0] = p[1] + [p[3]]

    def p_dosm_comma_list1(self, p):
        ''' dosm_comma_list : COMMA test '''
        p[0] = [p[2]]

    def p_dosm_comma_list2(self, p):
        ''' dosm_comma_list : dosm_comma_list COMMA test '''
        p[0] = p[1] + [p[3]]

    def p_arglist1(self, p):
        ''' arglist : argument '''
        if isinstance(p[1], ast.keyword):
            p[0] = Arguments(keywords=[p[1]])
        else:
            p[0] = Arguments(args=[p[1]])

    def p_arglist2(self, p):
        ''' arglist : argument COMMA '''
        if isinstance(p[1], ast.keyword):
            p[0] = Arguments(keywords=[p[1]])
        else:
            p[0] = Arguments(args=[p[1]])

    def p_arglist3(self, p):
        ''' arglist : STAR test '''
        p[0] = Arguments(starargs=p[2])

    def p_arglist4(self, p):
        ''' arglist : STAR test COMMA DOUBLESTAR test '''
        p[0] = Arguments(starargs=p[2], kwargs=p[5])

    def p_arglist5(self, p):
        ''' arglist : DOUBLESTAR test '''
        p[0] = Arguments(kwargs=p[2])

    def _validate_arglist_list(self, items, lexer):
        kwnames = set()
        saw_kw = False
        for item in items:
            if isinstance(item, ast.keyword):
                saw_kw = True
                if item.arg in kwnames:
                    msg = 'keyword argument repeated'
                    tok = FakeToken(lexer, item.lineno)
                    syntax_error(msg, tok)
                kwnames.add(item.arg)
            elif saw_kw:
                msg = 'non-keyword arg after keyword arg'
                tok = FakeToken(lexer, item.lineno)
                syntax_error(msg, tok)

    def p_arglist6(self, p):
        ''' arglist : arglist_list argument '''
        args = []
        kws = []
        arglist = p[1]
        arg = p[2]
        # TODO get the proper linenumber for the argument
        arg.lineno = arglist[-1].lineno
        items = arglist + [arg]
        self._validate_arglist_list(items, p.lexer.lexer)
        for arg in items:
            if isinstance(arg, ast.keyword):
                kws.append(arg)
            else:
                args.append(arg)
        p[0] = Arguments(args=args, keywords=kws)

    def p_arglist7(self, p):
        ''' arglist : arglist_list argument COMMA '''
        args = []
        kws = []
        arglist = p[1]
        arg = p[2]
        arg.lineno = p.lineno(3)
        items = arglist + [arg]
        self._validate_arglist_list(items, p.lexer.lexer)
        for arg in items:
            if isinstance(arg, ast.keyword):
                kws.append(arg)
            else:
                args.append(arg)
        p[0] = Arguments(args=args, keywords=kws)

    def p_arglist8(self, p):
        ''' arglist : arglist_list STAR test '''
        args = []
        kws = []
        items = p[1]
        self._validate_arglist_list(items, p.lexer.lexer)
        for arg in items:
            if isinstance(arg, ast.keyword):
                kws.append(arg)
            else:
                args.append(arg)
        p[0] = Arguments(args=args, keywords=kws, starargs=p[3])

    def p_arglist9(self, p):
        ''' arglist : arglist_list STAR test COMMA DOUBLESTAR test '''
        args = []
        kws = []
        items = p[1]
        self._validate_arglist_list(items, p.lexer.lexer)
        for arg in items:
            if isinstance(arg, ast.keyword):
                kws.append(arg)
            else:
                args.append(arg)
        p[0] = Arguments(args=args, keywords=kws, starargs=p[3], kwargs=p[6])

    def p_arglist10(self, p):
        ''' arglist : arglist_list DOUBLESTAR test '''
        args = []
        kws = []
        items = p[1]
        self._validate_arglist_list(items, p.lexer.lexer)
        for arg in items:
            if isinstance(arg, ast.keyword):
                kws.append(arg)
            else:
                args.append(arg)
        p[0] = Arguments(args=args, keywords=kws, kwargs=p[3])

    def p_arglist11(self, p):
        ''' arglist : STAR test COMMA argument '''
        keyword = p[4]
        if isinstance(keyword, ast.keyword):
            p[0] = Arguments(keywords=[keyword], starargs=p[2])
        else:
            msg = 'only named arguments may follow *expression'
            tok = FakeToken(p.lexer.lexer, p.lineno(1))
            syntax_error(msg, tok)

    def p_arglist12(self, p):
        ''' arglist : STAR test COMMA argument COMMA DOUBLESTAR test '''
        keyword = p[4]
        if isinstance(keyword, ast.keyword):
            p[0] = Arguments(keywords=[keyword], starargs=p[2], kwargs=p[7])
        else:
            msg = 'only named arguments may follow *expression'
            tok = FakeToken(p.lexer.lexer, p.lineno(1))
            syntax_error(msg, tok)

    def p_arglist13(self, p):
        ''' arglist : STAR test COMMA arglist_list argument '''
        kwnames = set()
        keywords = p[4] + [p[5]]
        for kw in keywords:
            if not isinstance(kw, ast.keyword):
                msg = 'only named arguments may follow *expression'
                tok = FakeToken(p.lexer.lexer, p.lineno(1))
                syntax_error(msg, tok)
            if kw.arg in kwnames:
                msg = 'keyword argument repeated'
                tok = FakeToken(p.lexer.lexer, kw.lineno)
                syntax_error(msg, tok)
            kwnames.add(kw.arg)
        p[0] = Arguments(keywords=keywords, starargs=p[2])

    def p_arglist14(self, p):
        ''' arglist : STAR test COMMA arglist_list argument COMMA DOUBLESTAR test '''
        kwnames = set()
        keywords = p[4] + [p[5]]
        for kw in keywords:
            if not isinstance(kw, ast.keyword):
                msg = 'only named arguments may follow *expression'
                tok = FakeToken(p.lexer.lexer, p.lineno(1))
                syntax_error(msg, tok)
            if kw.arg in kwnames:
                msg = 'keyword argument repeated'
                tok = FakeToken(p.lexer.lexer, kw.lineno)
                syntax_error(msg, tok)
            kwnames.add(kw.arg)
        p[0] = Arguments(keywords=keywords, starargs=p[2], kwargs=p[8])

    def _validate_arglist_and_kwlist(self, p, items, keywords):
        """Validate arguments and keywords arguments.

        Assume that the second token is a STAR.

        """
        kwnames = set()
        args = []
        kws = []
        self._validate_arglist_list(items, p.lexer.lexer)
        for arg in items:
            if isinstance(arg, ast.keyword):
                kws.append(arg)
                kwnames.add(arg.arg)
            else:
                args.append(arg)
        for kw in keywords:
            if not isinstance(kw, ast.keyword):
                msg = 'only named arguments may follow *expression'
                tok = FakeToken(p.lexer.lexer, p.lineno(2))
                syntax_error(msg, tok)
            if kw.arg in kwnames:
                msg = 'keyword argument repeated'
                tok = FakeToken(p.lexer.lexer, kw.lineno)
                syntax_error(msg, tok)
            kwnames.add(kw.arg)
        kws.extend(keywords)

        return args, kws

    def p_arglist15(self, p):
        ''' arglist : arglist_list STAR test COMMA argument'''
        args, kwargs = self._validate_arglist_and_kwlist(p, p[1], [p[5]])
        p[0] = Arguments(args=args, keywords=kwargs, starargs=p[3])

    def p_arglist16(self, p):
        ''' arglist : arglist_list STAR test COMMA arglist_list argument'''
        args, kwargs = self._validate_arglist_and_kwlist(p, p[1],
                                                         p[5] + [p[6]])
        p[0] = Arguments(args=args, keywords=kwargs, starargs=p[3])

    def p_arglist17(self, p):
        ''' arglist : arglist_list STAR test COMMA argument COMMA DOUBLESTAR test '''
        args, kwargs = self._validate_arglist_and_kwlist(p, p[1], [p[5]])
        p[0] = Arguments(args=args, keywords=kwargs, starargs=p[3],
                         kwargs=p[8])

    def p_arglist18(self, p):
        ''' arglist : arglist_list STAR test COMMA arglist_list argument COMMA DOUBLESTAR test '''
        args, kwargs = self._validate_arglist_and_kwlist(p, p[1],
                                                         p[5] + [p[6]])
        p[0] = Arguments(args=args, keywords=kwargs, starargs=p[3],
                         kwargs=p[9])

    def p_arglist_list1(self, p):
        ''' arglist_list : argument COMMA '''
        arg = p[1]
        arg.lineno = p.lineno(2)
        p[0] = [arg]

    def p_arglist_list2(self, p):
        ''' arglist_list : arglist_list argument COMMA '''
        arg = p[2]
        arg.lineno = p.lineno(3)
        p[0] = p[1] + [arg]

    def p_argument1(self, p):
        ''' argument : test '''
        p[0] = p[1]

    def p_argument2(self, p):
        ''' argument : test comp_for '''
        p[0] = ast.GeneratorExp(elt=p[1], generators=p[2])

    # This keyword argument needs to be asserted as a NAME, but using NAME
    # here causes ambiguity in the parse tables.
    def p_argument3(self, p):
        ''' argument : test EQUAL test '''
        arg = p[1]
        if not isinstance(arg, ast.Name):
            msg = 'Keyword arg must be a Name.'
            tok = FakeToken(p.lexer.lexer, p.lineno(2))
            syntax_error(msg, tok)
        value = p[3]
        p[0] = ast.keyword(arg=arg.id, value=value, lineno=p.lineno(2))

    def p_comp_for1(self, p):
        ''' comp_for : FOR exprlist IN or_test '''
        target = p[2]
        self.set_context(target, Store, p)
        p[0] = [ast.comprehension(target=target, iter=p[4], ifs=[])]

    def p_comp_for2(self, p):
        ''' comp_for : FOR exprlist IN or_test comp_iter '''
        target = p[2]
        self.set_context(target, Store, p)
        gens = []
        gens.append(ast.comprehension(target=target, iter=p[4], ifs=[]))
        for item in p[5]:
            if isinstance(item, ast.comprehension):
                gens.append(item)
            else:
                gens[-1].ifs.append(item)
        p[0] = gens

    def p_comp_iter1(self, p):
        ''' comp_iter : comp_for '''
        p[0] = p[1]

    def p_comp_iter2(self, p):
        ''' comp_iter : comp_if '''
        p[0] = p[1]

    def p_comp_if1(self, p):
        ''' comp_if : IF old_test '''
        p[0] = [p[2]]

    def p_comp_if2(self, p):
        ''' comp_if : IF old_test comp_iter '''
        p[0] = [p[2]] + p[3]

    def p_old_test1(self, p):
        ''' old_test : or_test '''
        p[0] = p[1]

    def p_old_test2(self, p):
        ''' old_test : old_lambdef '''
        p[0] = p[1]

    def p_old_lambdef1(self, p):
        ''' old_lambdef : LAMBDA COLON old_test '''
        args = self._make_args([])
        body = p[3]
        p[0] = ast.Lambda(args=args, body=body)

    def p_old_lambdef2(self, p):
        ''' old_lambdef : LAMBDA varargslist COLON old_test '''
        args = p[2]
        body = p[4]
        p[0] = ast.Lambda(args=args, body=body)

    def p_lambdef1(self, p):
        ''' lambdef : LAMBDA COLON test '''
        args = self._make_args([])
        body = p[3]
        p[0] = ast.Lambda(args=args, body=body)

    def p_lambdef2(self, p):
        ''' lambdef : LAMBDA varargslist COLON test '''
        args = p[2]
        body = p[4]
        p[0] = ast.Lambda(args=args, body=body)

    def _make_args(self, args, defaults=[], vararg=None, kwonlyargs=[],
                   kw_defaults=[], kwarg=None):
        """Build an ast node for function arguments.

        """
        # On Python 2 convert vararg and kwarg to raw name, raise error using
        # lineno stored on the node and lexer from self.
        # On Python 3.3 extract name and annotation
        # After should be straight forward
        raise NotImplementedError()

    # We use fpdef everywhere here to re-use more easily those rules on
    # Python 3 and be able to generate the typedargslist rules directly from
    # them.
    # This means however that we need to unpack the name on Python 2 for vararg
    # and kwarg and ensure that we do not get a list.
    # Note the comments of the rules below take into account the possibility
    # to unpack a tuple in a function signature in Python 2.

    def p_varargslist1(self, p):
        ''' varargslist : fpdef COMMA STAR fpdef '''
        # def f(a, *args): pass
        # def f((a, b), *args): pass
        p[0] = self._make_args([p[1]], vararg=p[4])

    def p_varargslist2(self, p):
        ''' varargslist : fpdef COMMA STAR fpdef COMMA DOUBLESTAR fpdef '''
        # def f(a, *args, **kwargs): pass
        # def f((a, b), *args, **kwargs): pass
        p[0] = self._make_args([p[1]], vararg=p[4], kwarg=p[7])

    def p_varargslist3(self, p):
        ''' varargslist : fpdef COMMA DOUBLESTAR fpdef '''
        # def f(a, **kwargs): pass
        # def f((a, b), **kwargs): pass
        p[0] = self._make_args([p[1]], kwarg=p[4])

    def p_varargslist4(self, p):
        ''' varargslist : fpdef '''
        # def f(a): pass
        # def f((a, b)): pass
        p[0] = self._make_args([p[1]])

    def p_varargslist5(self, p):
        ''' varargslist : fpdef COMMA '''
        # def f(a,): pass
        # def f((a,b),): pass
        p[0] = self._make_args([p[1]])

    def p_varargslist6(self, p):
        ''' varargslist : fpdef varargslist_list COMMA STAR fpdef '''
        # def f((a, b), c, *args): pass
        # def f((a, b), c, d=4, *args): pass
        list_args, defaults = p[2]
        args = [p[1]] + list_args
        p[0] = self._make_args(args=args, defaults=defaults, vararg=p[5])

    def p_varargslist7(self, p):
        ''' varargslist : fpdef varargslist_list COMMA STAR fpdef COMMA DOUBLESTAR fpdef '''
        # def f((a, b), c, *args, **kwargs): pass
        # def f((a, b), c, d=4, *args, **kwargs): pass
        list_args, defaults = p[2]
        args = [p[1]] + list_args
        p[0] = self._make_args(args=args, defaults=defaults, vararg=p[5],
                               kwarg=p[8])

    def p_varargslist8(self, p):
        ''' varargslist : fpdef varargslist_list COMMA DOUBLESTAR fpdef '''
        # def f((a, b), c, **kwargs): pass
        # def f((a, b), c, d=4, **kwargs): pass
        list_args, defaults = p[2]
        args = [p[1]] + list_args
        p[0] = self._make_args(args=args, defaults=defaults, kwarg=p[5])

    def p_varargslist9(self, p):
        ''' varargslist : fpdef varargslist_list '''
        # def f((a, b), c): pass
        # def f((a, b), c, d=4): pass
        list_args, defaults = p[2]
        args = [p[1]] + list_args
        p[0] = self._make_args(args, defaults=defaults)

    def p_varargslist10(self, p):
        ''' varargslist : fpdef varargslist_list COMMA '''
        # def f((a, b), c,): pass
        # def f((a, b), c, d=4,): pass
        list_args, defaults = p[2]
        args = [p[1]] + list_args
        p[0] = self._make_args(args, defaults=defaults)

    def p_varargslist11(self, p):
        ''' varargslist : fpdef EQUAL test COMMA STAR fpdef '''
        # def f(a=1, *args): pass
        # def f((a,b)=(1,2), *args): pass
        p[0] = self._make_args([p[1]], defaults=[p[3]], vararg=p[6])

    def p_varargslist12(self, p):
        ''' varargslist : fpdef EQUAL test COMMA STAR fpdef COMMA DOUBLESTAR fpdef '''
        # def f(a=1, *args, **kwargs): pass
        # def f((a,b)=(1,2), *args, **kwargs): pass
        p[0] = self._make_args([p[1]], defaults=[p[3]], vararg=p[6],
                               kwarg=p[9])

    def p_varargslist13(self, p):
        ''' varargslist : fpdef EQUAL test COMMA DOUBLESTAR fpdef '''
        # def f(a=1, **kwargs): pass
        # def f((a,b)=(1,2), **kwargs): pass
        p[0] = self._make_args(args=[p[1]], defaults=[p[3]], kwarg=p[6])

    def p_varargslist14(self, p):
        ''' varargslist : fpdef EQUAL test '''
        # def f(a=1): pass
        # def f((a,b)=(1,2)): pass
        p[0] = self._make_args(args=[p[1]], defaults=[p[3]])

    def p_varargslist15(self, p):
        ''' varargslist : fpdef EQUAL test COMMA '''
        # def f(a=1,): pass
        # def f((a,b)=(1,2),): pass
        p[0] = self._make_args(args=[p[1]], defaults=[p[3]])

    def p_varargslist16(self, p):
        ''' varargslist : fpdef EQUAL test varargslist_list COMMA STAR fpdef '''
        # def f(a=1, b=2, *args): pass
        list_args, list_defaults = p[4]
        if len(list_args) != len(list_defaults):
            msg = 'non-default argument follows default argument.'
            tok = FakeToken(p.lexer.lexer, p.lineno(2))
            syntax_error(msg, tok)
        args = [p[1]] + list_args
        defaults = [p[3]] + list_defaults
        p[0] = self._make_args(args, defaults=defaults, vararg=p[7])

    def p_varargslist17(self, p):
        ''' varargslist : fpdef EQUAL test varargslist_list COMMA STAR fpdef COMMA DOUBLESTAR fpdef '''
        # def f(a=1, b=2, *args, **kwargs)
        list_args, list_defaults = p[4]
        if len(list_args) != len(list_defaults):
            msg = 'non-default argument follows default argument.'
            tok = FakeToken(p.lexer.lexer, p.lineno(2))
            syntax_error(msg, tok)
        args = [p[1]] + list_args
        defaults = [p[3]] + list_defaults
        p[0] = self._make_args(args, defaults=defaults, vararg=p[7],
                               kwarg=p[10])

    def p_varargslist18(self, p):
        ''' varargslist : fpdef EQUAL test varargslist_list COMMA DOUBLESTAR fpdef '''
        # def f(a=1, b=2, **kwargs): pass
        list_args, list_defaults = p[4]
        if len(list_args) != len(list_defaults):
            msg = 'non-default argument follows default argument.'
            tok = FakeToken(p.lexer.lexer, p.lineno(2))
            syntax_error(msg, tok)
        args = [p[1]] + list_args
        defaults = [p[3]] + list_defaults
        p[0] = self._make_args(args, defaults=defaults, kwarg=p[7])

    def p_varargslist19(self, p):
        ''' varargslist : fpdef EQUAL test varargslist_list '''
        # def f(a=1, b=2): pass
        list_args, list_defaults = p[4]
        if len(list_args) != len(list_defaults):
            msg = 'non-default argument follows default argument.'
            tok = FakeToken(p.lexer.lexer, p.lineno(2))
            syntax_error(msg, tok)
        args = [p[1]] + list_args
        defaults = [p[3]] + list_defaults
        p[0] = self._make_args(args, defaults=defaults)

    def p_varargslist20(self, p):
        ''' varargslist : fpdef EQUAL test varargslist_list COMMA '''
        # def f(a=1, b=2,): pass
        list_args, list_defaults = p[4]
        if len(list_args) != len(list_defaults):
            msg = 'non-default argument follows default argument.'
            tok = FakeToken(p.lexer.lexer, p.lineno(2))
            syntax_error(msg, tok)
        args = [p[1]] + list_args
        defaults = [p[3]] + list_defaults
        p[0] = self._make_args(args, defaults=defaults)

    def p_varargslist21(self, p):
        ''' varargslist : STAR fpdef '''
        # def f(*args): pass
        p[0] = self._make_args([], vararg=p[2])

    def p_varargslist22(self, p):
        ''' varargslist : STAR fpdef COMMA DOUBLESTAR fpdef '''
        # def f(*args, **kwargs): pass
        p[0] = self._make_args(args=[], vararg=p[2], kwarg=p[5])

    def p_varargslist23(self, p):
        ''' varargslist : DOUBLESTAR fpdef '''
        # def f(**kwargs): pass
        p[0] = self._make_args([], kwarg=p[2])

    # The varargslist_list handlers return a 2-tuple of (args, defaults) lists
    def p_varargslist_list1(self, p):
        ''' varargslist_list : COMMA fpdef '''
        p[0] = ([p[2]], [])

    def p_varargslist_list2(self, p):
        ''' varargslist_list : COMMA fpdef EQUAL test '''
        p[0] = ([p[2]], [p[4]])

    def p_varargslist_list3(self, p):
        ''' varargslist_list : varargslist_list COMMA fpdef '''
        list_args, list_defaults = p[1]
        if list_defaults:
            msg = 'non-default argument follows default argument.'
            tok = FakeToken(p.lexer.lexer, p.lineno(2))
            syntax_error(msg, tok)
        args = list_args + [p[3]]
        p[0] = (args, list_defaults)

    def p_varargslist_list4(self, p):
        ''' varargslist_list : varargslist_list COMMA fpdef EQUAL test '''
        list_args, list_defaults = p[1]
        args = list_args + [p[3]]
        defaults = list_defaults + [p[5]]
        p[0] = (args, defaults)

    def p_error(self, t):
        msg = 'invalid syntax'
        lexer = t.lexer
        # Ply has a weird thing where sometimes we get the EnamlLexer and
        # other times we get the Ply lexer
        if isinstance(lexer, self.lexer):
            lexer = lexer.lexer
        syntax_error(msg, FakeToken(lexer, t.lineno))

    # =========================================================================
    # End Parsing Rules
    # =========================================================================
