
#---------------------------------------------------------------------------------------
# Copyright (c) 2021-2022, Nucleic Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
#---------------------------------------------------------------------------------------
# NOTE This file was generated using enaml/core/parser/generate_enaml_parser.py
# DO NOT EDIT DIRECTLY
import ast
import itertools
from typing import Any, List, NoReturn, Optional, Tuple, TypeVar, Union

from enaml.core import enaml_ast
from pegen.parser import Parser, logger, memoize, memoize_left_rec

from .base_enaml_parser import BaseEnamlParser as Parser

# Singleton ast nodes, created once for efficiency
Load = ast.Load()
Store = ast.Store()
Del = ast.Del()
# Keywords and soft keywords are listed at the end of the parser definition.
class EnamlParser(Parser):

    @memoize
    def start(self) -> Optional[enaml_ast . Module]:
        # start: enaml_item* NEWLINE? $
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self._loop0_1(),)
            and
            (opt := self.expect('NEWLINE'),)
            and
            (_endmarker := self.expect('ENDMARKER'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . create_enaml_module ( a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def enaml_item(self) -> Optional[ast . AST]:
        # enaml_item: statement | enamldef | template
        mark = self._mark()
        if (
            (statement := self.statement())
        ):
            return statement
        self._reset(mark)
        if (
            (enamldef := self.enamldef())
        ):
            return enamldef
        self._reset(mark)
        if (
            (template := self.template())
        ):
            return template
        self._reset(mark)
        return None

    @memoize
    def enamldef(self) -> Optional[enaml_ast . EnamlDef]:
        # enamldef: pragma* "enamldef" NAME '(' NAME ')' [':' NAME] &&':' enamldef_body
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (p := self._loop0_2(),)
            and
            (literal := self.expect("enamldef"))
            and
            (a := self.name())
            and
            (literal_1 := self.expect('('))
            and
            (b := self.name())
            and
            (literal_2 := self.expect(')'))
            and
            (c := self._tmp_3(),)
            and
            (forced := self.expect_forced(self.expect(':'), "':'"))
            and
            (d := self.enamldef_body())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . validate_enamldef ( enaml_ast . EnamlDef ( typename = a , base = b , identifier = c , docstring = d [0] , body = d [1] , pragmas = p , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) )
        self._reset(mark)
        return None

    @memoize
    def enamldef_body(self) -> Optional[Tuple [str , list]]:
        # enamldef_body: NEWLINE INDENT STRING NEWLINE enamldef_item+ DEDENT | NEWLINE INDENT enamldef_item+ DEDENT | enamldef_simple_item | invalid_block
        mark = self._mark()
        if (
            (_newline := self.expect('NEWLINE'))
            and
            (_indent := self.expect('INDENT'))
            and
            (a := self.string())
            and
            (_newline_1 := self.expect('NEWLINE'))
            and
            (b := self._loop1_4())
            and
            (_dedent := self.expect('DEDENT'))
        ):
            return a , [x for x in b if x]
        self._reset(mark)
        if (
            (_newline := self.expect('NEWLINE'))
            and
            (_indent := self.expect('INDENT'))
            and
            (b := self._loop1_5())
            and
            (_dedent := self.expect('DEDENT'))
        ):
            return "" , [x for x in b if x]
        self._reset(mark)
        if (
            (a := self.enamldef_simple_item())
        ):
            return "" , [a]
        self._reset(mark)
        if (
            (invalid_block := self.invalid_block())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def enamldef_item(self) -> Optional[Any]:
        # enamldef_item: enamldef_simple_item | decl_funcdef | child_def | template_inst
        mark = self._mark()
        if (
            (enamldef_simple_item := self.enamldef_simple_item())
        ):
            return enamldef_simple_item
        self._reset(mark)
        if (
            (decl_funcdef := self.decl_funcdef())
        ):
            return decl_funcdef
        self._reset(mark)
        if (
            (child_def := self.child_def())
        ):
            return child_def
        self._reset(mark)
        if (
            (template_inst := self.template_inst())
        ):
            return template_inst
        self._reset(mark)
        return None

    @memoize
    def enamldef_simple_item(self) -> Optional[Any]:
        # enamldef_simple_item: binding | ex_binding | storage_alias_const_expr | 'pass' NEWLINE
        mark = self._mark()
        if (
            (binding := self.binding())
        ):
            return binding
        self._reset(mark)
        if (
            (ex_binding := self.ex_binding())
        ):
            return ex_binding
        self._reset(mark)
        if (
            (storage_alias_const_expr := self.storage_alias_const_expr())
        ):
            return storage_alias_const_expr
        self._reset(mark)
        if (
            (literal := self.expect('pass'))
            and
            (_newline := self.expect('NEWLINE'))
        ):
            return None
        self._reset(mark)
        return None

    @memoize
    def pragmas(self) -> Optional[List [enaml_ast . Pragma]]:
        # pragmas: pragma+
        mark = self._mark()
        if (
            (_loop1_6 := self._loop1_6())
        ):
            return _loop1_6
        self._reset(mark)
        return None

    @memoize
    def pragma(self) -> Optional[enaml_ast . Pragma]:
        # pragma: "pragma" NAME ['(' ','.pragma_arg+ ')'] NEWLINE
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect("pragma"))
            and
            (a := self.name())
            and
            (opt := self._tmp_7(),)
            and
            (_newline := self.expect('NEWLINE'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . Pragma ( command = a , arguments = b or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def pragma_arg(self) -> Optional[enaml_ast . PragmaArg]:
        # pragma_arg: NAME | NUMBER | STRING
        mark = self._mark()
        if (
            (a := self.name())
        ):
            return enaml_ast . PragmaArg ( kind = "token" , value = a )
        self._reset(mark)
        if (
            (a := self.number())
        ):
            return enaml_ast . PragmaArg ( kind = "number" , value = a )
        self._reset(mark)
        if (
            (a := self.string())
        ):
            return enaml_ast . PragmaArg ( kind = "string" , value = a )
        self._reset(mark)
        return None

    @memoize
    def storage_alias_const_expr(self) -> Optional[Any]:
        # storage_alias_const_expr: alias_expr | const_expr | storage_expr
        mark = self._mark()
        if (
            (alias_expr := self.alias_expr())
        ):
            return alias_expr
        self._reset(mark)
        if (
            (const_expr := self.const_expr())
        ):
            return const_expr
        self._reset(mark)
        if (
            (storage_expr := self.storage_expr())
        ):
            return storage_expr
        self._reset(mark)
        return None

    @memoize
    def alias_expr(self) -> Optional[enaml_ast . AliasExpr]:
        # alias_expr: "alias" NAME [':' '.'.NAME+] NEWLINE
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect("alias"))
            and
            (a := self.name())
            and
            (b := self._tmp_8(),)
            and
            (_newline := self.expect('NEWLINE'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . AliasExpr ( name = a , target = b [0] if b else "" , chain = b [1 :] if b else [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def const_expr(self) -> Optional[enaml_ast . ConstExpr]:
        # const_expr: "const" NAME [':' dec_primary] &'=' operator_expr
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect("const"))
            and
            (a := self.name())
            and
            (b := self._tmp_9(),)
            and
            self.positive_lookahead(self.expect, '=')
            and
            (d := self.operator_expr())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . ConstExpr ( name = a , typename = b , expr = d . value , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def storage_expr(self) -> Optional[enaml_ast . StorageExpr]:
        # storage_expr: ("attr" | "event") NAME [':' dec_primary] NEWLINE | ("attr" | "event") NAME [':' dec_primary] operator_expr
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self._tmp_10())
            and
            (b := self.name())
            and
            (c := self._tmp_11(),)
            and
            (_newline := self.expect('NEWLINE'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . StorageExpr ( name = b , kind = a , typename = c , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self._tmp_12())
            and
            (b := self.name())
            and
            (c := self._tmp_13(),)
            and
            (e := self.operator_expr())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . StorageExpr ( name = b , kind = a , typename = c , expr = e , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def child_def(self) -> Optional[enaml_ast . ChildDef]:
        # child_def: NAME [':' NAME] ':' child_def_body
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
            and
            (b := self._tmp_14(),)
            and
            (literal := self.expect(':'))
            and
            (c := self.child_def_body())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . ChildDef ( typename = a , identifier = b . string if b else "" , body = [x for x in c if x] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def child_def_body(self) -> Optional[list]:
        # child_def_body: NEWLINE INDENT child_def_item+ DEDENT | child_def_simple_item | invalid_block
        mark = self._mark()
        if (
            (_newline := self.expect('NEWLINE'))
            and
            (_indent := self.expect('INDENT'))
            and
            (a := self._loop1_15())
            and
            (_dedent := self.expect('DEDENT'))
        ):
            return a
        self._reset(mark)
        if (
            (a := self.child_def_simple_item())
        ):
            return [a]
        self._reset(mark)
        if (
            (invalid_block := self.invalid_block())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize_left_rec
    def child_def_item(self) -> Optional[Any]:
        # child_def_item: child_def_item | decl_funcdef | child_def | template_inst
        mark = self._mark()
        if (
            (child_def_item := self.child_def_item())
        ):
            return child_def_item
        self._reset(mark)
        if (
            (decl_funcdef := self.decl_funcdef())
        ):
            return decl_funcdef
        self._reset(mark)
        if (
            (child_def := self.child_def())
        ):
            return child_def
        self._reset(mark)
        if (
            (template_inst := self.template_inst())
        ):
            return template_inst
        self._reset(mark)
        return None

    @memoize
    def child_def_simple_item(self) -> Optional[Any]:
        # child_def_simple_item: binding | ex_binding | alias_expr | storage_expr | 'pass' NEWLINE
        mark = self._mark()
        if (
            (binding := self.binding())
        ):
            return binding
        self._reset(mark)
        if (
            (ex_binding := self.ex_binding())
        ):
            return ex_binding
        self._reset(mark)
        if (
            (alias_expr := self.alias_expr())
        ):
            return alias_expr
        self._reset(mark)
        if (
            (storage_expr := self.storage_expr())
        ):
            return storage_expr
        self._reset(mark)
        if (
            (literal := self.expect('pass'))
            and
            (_newline := self.expect('NEWLINE'))
        ):
            return None
        self._reset(mark)
        return None

    @memoize
    def binding(self) -> Optional[enaml_ast . Binding]:
        # binding: NAME operator_expr
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
            and
            (b := self.operator_expr())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . Binding ( name = a . value , expr = operator_expr , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def ex_binding(self) -> Optional[enaml_ast . ExBinding]:
        # ex_binding: '.'.NAME+ operator_expr
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self._gather_16())
            and
            (b := self.operator_expr())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . ExBinding ( chain = tuple ( a ) , expr = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def operator_expr(self) -> Optional[Any]:
        # operator_expr: ('=' | '<<') py_expr NEWLINE | ('>>' | ':=') py_expr NEWLINE | ':' ':' block | '<<' block
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self._tmp_18())
            and
            (b := self.py_expr())
            and
            (_newline := self.expect('NEWLINE'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . OperatorExpr ( operator = a , value = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self._tmp_19())
            and
            (b := self.py_expr())
            and
            (_newline := self.expect('NEWLINE'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . OperatorExpr ( operator = a , value = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if isintance ( b , self . INVERTABLE ) else self . raise_syntax_error_known_location ( "can't assign to expression of this form" , b )
        self._reset(mark)
        if (
            (a := self.expect(':'))
            and
            (b := self.expect(':'))
            and
            (c := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . OperatorExpr ( operator = '::' , value = self . create_python_func_for_operator ( block , self . NOTIFICATION_DISALLOWED , '%s not allowed in a notification block' ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if a . end_col_offset == b . col_offset else self . raise_syntax_error_known_range ( "invalid syntax. Did you mean '::' ?" , a , b )
        self._reset(mark)
        if (
            (literal := self.expect('<<'))
            and
            (block := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . OperatorExpr ( operator = '<<' , value = self . create_python_func_for_operator ( block , self . SUBSCRIPTION_DISALLOWED , '%s not allowed in a subscription block' ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def py_expr(self) -> Optional[enaml_ast . PythonExpression]:
        # py_expr: expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . PythonExpression ( expr = ast . Expression ( body = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def decl_funcdef(self) -> Optional[Any]:
        # decl_funcdef: "func" NAME parameters ['->' expression] &&':' block | NAME '=' '>' parameters ['->' expression] &&':' block
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect("func"))
            and
            (a := self.name())
            and
            (b := self.parameters())
            and
            (r := self._tmp_20(),)
            and
            (forced := self.expect_forced(self.expect(':'), "':'"))
            and
            (c := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . FuncDef ( funcdef = ast . FunctionDef ( name = a , args = b , returns = r , body = self . validate_decl_func_body ( c ) , decorator_list = [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) , is_override = False , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.name())
            and
            (x := self.expect('='))
            and
            (y := self.expect('>'))
            and
            (b := self.parameters())
            and
            (r := self._tmp_21(),)
            and
            (forced := self.expect_forced(self.expect(':'), "':'"))
            and
            (c := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . FuncDef ( funcdef = ast . FunctionDef ( name = a , args = b , returns = r , body = self . validate_decl_func_body ( c ) , decorator_list = [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) , is_override = True , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def template(self) -> Optional[enaml_ast . Template]:
        # template: pragmas? "template" NAME '(' template_params ')' &&':' template_body
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.pragmas(),)
            and
            (literal := self.expect("template"))
            and
            (b := self.name())
            and
            (literal_1 := self.expect('('))
            and
            (c := self.template_params())
            and
            (literal_2 := self.expect(')'))
            and
            (forced := self.expect_forced(self.expect(':'), "':'"))
            and
            (d := self.template_body())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . validate_template ( enaml_ast . Template ( name = b , parameters = c , docstring = d [0] , body = d [1] , pragmas = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) )
        self._reset(mark)
        return None

    @memoize
    def template_body(self) -> Optional[Tuple [str , list]]:
        # template_body: NEWLINE INDENT template_item+ DEDENT | NEWLINE INDENT STRING NEWLINE template_item+ DEDENT | template_simple_item | invalid_block
        mark = self._mark()
        if (
            (_newline := self.expect('NEWLINE'))
            and
            (_indent := self.expect('INDENT'))
            and
            (a := self._loop1_22())
            and
            (_dedent := self.expect('DEDENT'))
        ):
            return "" , a
        self._reset(mark)
        if (
            (_newline := self.expect('NEWLINE'))
            and
            (_indent := self.expect('INDENT'))
            and
            (d := self.string())
            and
            (_newline_1 := self.expect('NEWLINE'))
            and
            (a := self._loop1_23())
            and
            (_dedent := self.expect('DEDENT'))
        ):
            return d , a
        self._reset(mark)
        if (
            (a := self.template_simple_item())
        ):
            return "" , [a]
        self._reset(mark)
        if (
            (invalid_block := self.invalid_block())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def template_item(self) -> Optional[Any]:
        # template_item: template_simple_item | child_def | template_inst
        mark = self._mark()
        if (
            (template_simple_item := self.template_simple_item())
        ):
            return template_simple_item
        self._reset(mark)
        if (
            (child_def := self.child_def())
        ):
            return child_def
        self._reset(mark)
        if (
            (template_inst := self.template_inst())
        ):
            return template_inst
        self._reset(mark)
        return None

    @memoize
    def template_simple_item(self) -> Optional[Any]:
        # template_simple_item: alias_expr | storage_expr | 'pass' NEWLINE
        mark = self._mark()
        if (
            (alias_expr := self.alias_expr())
        ):
            return alias_expr
        self._reset(mark)
        if (
            (storage_expr := self.storage_expr())
        ):
            return storage_expr
        self._reset(mark)
        if (
            (literal := self.expect('pass'))
            and
            (_newline := self.expect('NEWLINE'))
        ):
            return None
        self._reset(mark)
        return None

    @memoize
    def template_params(self) -> Optional[Any]:
        # template_params: ','.template_param+ [',' '*' NAME] | '*' NAME
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self._gather_24())
            and
            (b := self._tmp_26(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . TemplateParameters ( ** self . validate_template_paramlist ( a , b ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , )
        self._reset(mark)
        if (
            (literal := self.expect('*'))
            and
            (b := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . TemplateParameters ( ** self . validate_template_paramlist ( [] , b ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , )
        self._reset(mark)
        return None

    @memoize
    def template_param(self) -> Optional[Any]:
        # template_param: NAME ':' expression | NAME '=' expression | NAME
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
            and
            (literal := self.expect(':'))
            and
            (b := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . PositionalParameter ( name = a , specialization = enaml_ast . PythonExpression ( ast = ast . Expression ( body = b ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , )
        self._reset(mark)
        if (
            (a := self.name())
            and
            (literal := self.expect('='))
            and
            (b := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . KeywordParameter ( name = a , default = enaml_ast . PythonExpression ( ast = ast . Expression ( body = b ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , )
        self._reset(mark)
        if (
            (a := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . PositionalParameter ( name = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def template_inst(self) -> Optional[Any]:
        # template_inst: pragmas? NAME '(' template_args ')' [':' template_ids] ':' template_inst_body
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.pragmas(),)
            and
            (b := self.name())
            and
            (literal := self.expect('('))
            and
            (c := self.template_args())
            and
            (literal_1 := self.expect(')'))
            and
            (d := self._tmp_27(),)
            and
            (literal_2 := self.expect(':'))
            and
            (e := self.template_inst_body())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . validate_template_inst ( enaml_ast . TemplateInst ( name = b , arguments = c , identifiers = d , pragmas = a , body = [tib for tib in e if tib] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) )
        self._reset(mark)
        return None

    @memoize
    def template_args(self) -> Optional[Any]:
        # template_args: ','.template_argument+ [',' '*' NAME] | '*' NAME
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self._gather_28())
            and
            (b := self._tmp_30(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . TemplateArguments ( args = a , stararg = enaml_ast . PythonExpression ( ast = ast . Expression ( body = b ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , )
        self._reset(mark)
        if (
            (literal := self.expect('*'))
            and
            (b := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . TemplateArguments ( args = [] , stararg = enaml_ast . PythonExpression ( ast = ast . Expression ( body = b ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , )
        self._reset(mark)
        return None

    @memoize
    def template_argument(self) -> Optional[Any]:
        # template_argument: expression | expression for_if_clauses
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . PythonExpression ( ast = ast . Expression ( body = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , )
        self._reset(mark)
        if (
            (a := self.expression())
            and
            (b := self.for_if_clauses())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . PythonExpression ( ast . GeneratorExp ( elt = a , generators = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , )
        self._reset(mark)
        return None

    @memoize
    def template_ids(self) -> Optional[Any]:
        # template_ids: ','.NAME+ [',' '*' NAME] | '*' NAME
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self._gather_31())
            and
            (b := self._tmp_33(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . TemplateIdentifiers ( names = a , starname = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('*'))
            and
            (b := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . TemplateIdentifiers ( names = [] , starname = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def template_inst_body(self) -> Optional[Any]:
        # template_inst_body: NEWLINE INDENT template_inst_item+ DEDENT | template_inst_item | invalid_block
        mark = self._mark()
        if (
            (_newline := self.expect('NEWLINE'))
            and
            (_indent := self.expect('INDENT'))
            and
            (a := self._loop1_34())
            and
            (_dedent := self.expect('DEDENT'))
        ):
            return a
        self._reset(mark)
        if (
            (a := self.template_inst_item())
        ):
            return a
        self._reset(mark)
        if (
            (invalid_block := self.invalid_block())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def template_inst_item(self) -> Optional[Any]:
        # template_inst_item: dec_primary operator_expr | 'pass' NEWLINE
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.dec_primary())
            and
            (b := self.operator_expr())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return enaml_ast . TemplateInstBinding ( name = a , exp = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , )
        self._reset(mark)
        if (
            (literal := self.expect('pass'))
            and
            (_newline := self.expect('NEWLINE'))
        ):
            return None
        self._reset(mark)
        return None

    @memoize
    def type_expressions(self) -> Optional[list]:
        # type_expressions: ','.expression+ ',' '*' expression ',' '**' expression | ','.expression+ ',' '*' expression | ','.expression+ ',' '**' expression | '*' expression ',' '**' expression | '*' expression | '**' expression | ','.expression+
        mark = self._mark()
        if (
            (a := self._gather_35())
            and
            (literal := self.expect(','))
            and
            (literal_1 := self.expect('*'))
            and
            (b := self.expression())
            and
            (literal_2 := self.expect(','))
            and
            (literal_3 := self.expect('**'))
            and
            (c := self.expression())
        ):
            return a + [b , c]
        self._reset(mark)
        if (
            (a := self._gather_37())
            and
            (literal := self.expect(','))
            and
            (literal_1 := self.expect('*'))
            and
            (b := self.expression())
        ):
            return a + [b]
        self._reset(mark)
        if (
            (a := self._gather_39())
            and
            (literal := self.expect(','))
            and
            (literal_1 := self.expect('**'))
            and
            (b := self.expression())
        ):
            return a + [b]
        self._reset(mark)
        if (
            (literal := self.expect('*'))
            and
            (a := self.expression())
            and
            (literal_1 := self.expect(','))
            and
            (literal_2 := self.expect('**'))
            and
            (b := self.expression())
        ):
            return [a , b]
        self._reset(mark)
        if (
            (literal := self.expect('*'))
            and
            (a := self.expression())
        ):
            return [a]
        self._reset(mark)
        if (
            (literal := self.expect('**'))
            and
            (a := self.expression())
        ):
            return [a]
        self._reset(mark)
        if (
            (a := self._gather_41())
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def statements(self) -> Optional[list]:
        # statements: statement+
        mark = self._mark()
        if (
            (a := self._loop1_43())
        ):
            return list ( itertools . chain ( * a ) )
        self._reset(mark)
        return None

    @memoize
    def statement(self) -> Optional[list]:
        # statement: compound_stmt | simple_stmts
        mark = self._mark()
        if (
            (a := self.compound_stmt())
        ):
            return [a]
        self._reset(mark)
        if (
            (a := self.simple_stmts())
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def statement_newline(self) -> Optional[list]:
        # statement_newline: compound_stmt NEWLINE | simple_stmts | NEWLINE | $
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.compound_stmt())
            and
            (_newline := self.expect('NEWLINE'))
        ):
            return [a]
        self._reset(mark)
        if (
            (simple_stmts := self.simple_stmts())
        ):
            return simple_stmts
        self._reset(mark)
        if (
            (_newline := self.expect('NEWLINE'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return [ast . Pass ( lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )]
        self._reset(mark)
        if (
            (_endmarker := self.expect('ENDMARKER'))
        ):
            return None
        self._reset(mark)
        return None

    @memoize
    def simple_stmts(self) -> Optional[list]:
        # simple_stmts: simple_stmt !';' NEWLINE | ';'.simple_stmt+ ';'? NEWLINE
        mark = self._mark()
        if (
            (a := self.simple_stmt())
            and
            self.negative_lookahead(self.expect, ';')
            and
            (_newline := self.expect('NEWLINE'))
        ):
            return [a]
        self._reset(mark)
        if (
            (a := self._gather_44())
            and
            (opt := self.expect(';'),)
            and
            (_newline := self.expect('NEWLINE'))
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def simple_stmt(self) -> Optional[Any]:
        # simple_stmt: assignment | star_expressions | &'return' return_stmt | &('import' | 'from') import_stmt | &'raise' raise_stmt | 'pass' | &'del' del_stmt | &'yield' yield_stmt | &'assert' assert_stmt | 'break' | 'continue' | &'global' global_stmt | &'nonlocal' nonlocal_stmt
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (assignment := self.assignment())
        ):
            return assignment
        self._reset(mark)
        if (
            (e := self.star_expressions())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Expr ( value = e , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            self.positive_lookahead(self.expect, 'return')
            and
            (return_stmt := self.return_stmt())
        ):
            return return_stmt
        self._reset(mark)
        if (
            self.positive_lookahead(self._tmp_46, )
            and
            (import_stmt := self.import_stmt())
        ):
            return import_stmt
        self._reset(mark)
        if (
            self.positive_lookahead(self.expect, 'raise')
            and
            (raise_stmt := self.raise_stmt())
        ):
            return raise_stmt
        self._reset(mark)
        if (
            (literal := self.expect('pass'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Pass ( lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            self.positive_lookahead(self.expect, 'del')
            and
            (del_stmt := self.del_stmt())
        ):
            return del_stmt
        self._reset(mark)
        if (
            self.positive_lookahead(self.expect, 'yield')
            and
            (yield_stmt := self.yield_stmt())
        ):
            return yield_stmt
        self._reset(mark)
        if (
            self.positive_lookahead(self.expect, 'assert')
            and
            (assert_stmt := self.assert_stmt())
        ):
            return assert_stmt
        self._reset(mark)
        if (
            (literal := self.expect('break'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Break ( lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('continue'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Continue ( lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            self.positive_lookahead(self.expect, 'global')
            and
            (global_stmt := self.global_stmt())
        ):
            return global_stmt
        self._reset(mark)
        if (
            self.positive_lookahead(self.expect, 'nonlocal')
            and
            (nonlocal_stmt := self.nonlocal_stmt())
        ):
            return nonlocal_stmt
        self._reset(mark)
        return None

    @memoize
    def compound_stmt(self) -> Optional[Any]:
        # compound_stmt: &('def' | '@' | 'async') function_def | &'if' if_stmt | &('class' | '@') class_def | &('with' | 'async') with_stmt | &('for' | 'async') for_stmt | &'try' try_stmt | &'while' while_stmt | match_stmt
        mark = self._mark()
        if (
            self.positive_lookahead(self._tmp_47, )
            and
            (function_def := self.function_def())
        ):
            return function_def
        self._reset(mark)
        if (
            self.positive_lookahead(self.expect, 'if')
            and
            (if_stmt := self.if_stmt())
        ):
            return if_stmt
        self._reset(mark)
        if (
            self.positive_lookahead(self._tmp_48, )
            and
            (class_def := self.class_def())
        ):
            return class_def
        self._reset(mark)
        if (
            self.positive_lookahead(self._tmp_49, )
            and
            (with_stmt := self.with_stmt())
        ):
            return with_stmt
        self._reset(mark)
        if (
            self.positive_lookahead(self._tmp_50, )
            and
            (for_stmt := self.for_stmt())
        ):
            return for_stmt
        self._reset(mark)
        if (
            self.positive_lookahead(self.expect, 'try')
            and
            (try_stmt := self.try_stmt())
        ):
            return try_stmt
        self._reset(mark)
        if (
            self.positive_lookahead(self.expect, 'while')
            and
            (while_stmt := self.while_stmt())
        ):
            return while_stmt
        self._reset(mark)
        if (
            (match_stmt := self.match_stmt())
        ):
            return match_stmt
        self._reset(mark)
        return None

    @memoize
    def assignment(self) -> Optional[Any]:
        # assignment: NAME ':' expression ['=' annotated_rhs] | ('(' single_target ')' | single_subscript_attribute_target) ':' expression ['=' annotated_rhs] | ((star_targets '='))+ (yield_expr | star_expressions) !'=' TYPE_COMMENT? | single_target augassign ~ (yield_expr | star_expressions) | invalid_assignment
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
            and
            (literal := self.expect(':'))
            and
            (b := self.expression())
            and
            (c := self._tmp_51(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 6 ) , "Variable annotation syntax is" , ast . AnnAssign ( target = ast . Name ( id = a . string , ctx = Store , lineno = a . start [0] , col_offset = a . start [1] , end_lineno = a . end [0] , end_col_offset = a . end [1] , ) , annotation = b , value = c , simple = 1 , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) )
        self._reset(mark)
        if (
            (a := self._tmp_52())
            and
            (literal := self.expect(':'))
            and
            (b := self.expression())
            and
            (c := self._tmp_53(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 6 ) , "Variable annotation syntax is" , ast . AnnAssign ( target = a , annotation = b , value = c , simple = 0 , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) )
        self._reset(mark)
        if (
            (a := self._loop1_54())
            and
            (b := self._tmp_55())
            and
            self.negative_lookahead(self.expect, '=')
            and
            (tc := self.type_comment(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Assign ( targets = a , value = b , type_comment = tc , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        cut = False
        if (
            (a := self.single_target())
            and
            (b := self.augassign())
            and
            (cut := True)
            and
            (c := self._tmp_56())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . AugAssign ( target = a , op = b , value = c , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if cut: return None
        if (
            (invalid_assignment := self.invalid_assignment())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def augassign(self) -> Optional[Any]:
        # augassign: '+=' | '-=' | '*=' | '@=' | '/=' | '%=' | '&=' | '|=' | '^=' | '<<=' | '>>=' | '**=' | '//='
        mark = self._mark()
        if (
            (literal := self.expect('+='))
        ):
            return ast . Add ( )
        self._reset(mark)
        if (
            (literal := self.expect('-='))
        ):
            return ast . Sub ( )
        self._reset(mark)
        if (
            (literal := self.expect('*='))
        ):
            return ast . Mult ( )
        self._reset(mark)
        if (
            (literal := self.expect('@='))
        ):
            return self . check_version ( ( 3 , 5 ) , "The '@' operator is" , ast . MatMult ( ) )
        self._reset(mark)
        if (
            (literal := self.expect('/='))
        ):
            return ast . Div ( )
        self._reset(mark)
        if (
            (literal := self.expect('%='))
        ):
            return ast . Mod ( )
        self._reset(mark)
        if (
            (literal := self.expect('&='))
        ):
            return ast . BitAnd ( )
        self._reset(mark)
        if (
            (literal := self.expect('|='))
        ):
            return ast . BitOr ( )
        self._reset(mark)
        if (
            (literal := self.expect('^='))
        ):
            return ast . BitXor ( )
        self._reset(mark)
        if (
            (literal := self.expect('<<='))
        ):
            return ast . LShift ( )
        self._reset(mark)
        if (
            (literal := self.expect('>>='))
        ):
            return ast . RShift ( )
        self._reset(mark)
        if (
            (literal := self.expect('**='))
        ):
            return ast . Pow ( )
        self._reset(mark)
        if (
            (literal := self.expect('//='))
        ):
            return ast . FloorDiv ( )
        self._reset(mark)
        return None

    @memoize
    def global_stmt(self) -> Optional[ast . Global]:
        # global_stmt: 'global' ','.NAME+
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('global'))
            and
            (a := self._gather_57())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Global ( names = [n . string for n in a] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def nonlocal_stmt(self) -> Optional[ast . Nonlocal]:
        # nonlocal_stmt: 'nonlocal' ','.NAME+
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('nonlocal'))
            and
            (a := self._gather_59())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Nonlocal ( names = [n . string for n in a] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def yield_stmt(self) -> Optional[ast . Expr]:
        # yield_stmt: yield_expr
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (y := self.yield_expr())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Expr ( value = y , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def assert_stmt(self) -> Optional[ast . Assert]:
        # assert_stmt: 'assert' expression [',' expression]
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('assert'))
            and
            (a := self.expression())
            and
            (b := self._tmp_61(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Assert ( test = a , msg = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def del_stmt(self) -> Optional[ast . Delete]:
        # del_stmt: 'del' del_targets &(';' | NEWLINE) | invalid_del_stmt
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('del'))
            and
            (a := self.del_targets())
            and
            self.positive_lookahead(self._tmp_62, )
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Delete ( targets = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (invalid_del_stmt := self.invalid_del_stmt())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def import_stmt(self) -> Optional[ast . Import]:
        # import_stmt: import_name | import_from
        mark = self._mark()
        if (
            (import_name := self.import_name())
        ):
            return import_name
        self._reset(mark)
        if (
            (import_from := self.import_from())
        ):
            return import_from
        self._reset(mark)
        return None

    @memoize
    def import_name(self) -> Optional[ast . Import]:
        # import_name: 'import' dotted_as_names
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('import'))
            and
            (a := self.dotted_as_names())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Import ( names = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def import_from(self) -> Optional[ast . ImportFrom]:
        # import_from: 'from' (('.' | '...'))* dotted_name 'import' import_from_targets | 'from' (('.' | '...'))+ 'import' import_from_targets
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('from'))
            and
            (a := self._loop0_63(),)
            and
            (b := self.dotted_name())
            and
            (literal_1 := self.expect('import'))
            and
            (c := self.import_from_targets())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . ImportFrom ( module = b , names = c , level = self . extract_import_level ( a ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('from'))
            and
            (a := self._loop1_64())
            and
            (literal_1 := self.expect('import'))
            and
            (b := self.import_from_targets())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . ImportFrom ( names = b , level = self . extract_import_level ( a ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def import_from_targets(self) -> Optional[List [ast . alias]]:
        # import_from_targets: '(' import_from_as_names ','? ')' | import_from_as_names !',' | '*' | invalid_import_from_targets
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('('))
            and
            (a := self.import_from_as_names())
            and
            (opt := self.expect(','),)
            and
            (literal_1 := self.expect(')'))
        ):
            return a
        self._reset(mark)
        if (
            (import_from_as_names := self.import_from_as_names())
            and
            self.negative_lookahead(self.expect, ',')
        ):
            return import_from_as_names
        self._reset(mark)
        if (
            (literal := self.expect('*'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return [ast . alias ( name = "*" , asname = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )]
        self._reset(mark)
        if (
            (invalid_import_from_targets := self.invalid_import_from_targets())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def import_from_as_names(self) -> Optional[List [ast . alias]]:
        # import_from_as_names: ','.import_from_as_name+
        mark = self._mark()
        if (
            (a := self._gather_65())
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def import_from_as_name(self) -> Optional[ast . alias]:
        # import_from_as_name: NAME ['as' NAME]
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
            and
            (b := self._tmp_67(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . alias ( name = a . string , asname = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def dotted_as_names(self) -> Optional[List [ast . alias]]:
        # dotted_as_names: ','.dotted_as_name+
        mark = self._mark()
        if (
            (a := self._gather_68())
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def dotted_as_name(self) -> Optional[ast . alias]:
        # dotted_as_name: dotted_name ['as' NAME]
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.dotted_name())
            and
            (b := self._tmp_70(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . alias ( name = a , asname = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize_left_rec
    def dotted_name(self) -> Optional[str]:
        # dotted_name: dotted_name '.' NAME | NAME
        mark = self._mark()
        if (
            (a := self.dotted_name())
            and
            (literal := self.expect('.'))
            and
            (b := self.name())
        ):
            return a + "." + b . string
        self._reset(mark)
        if (
            (a := self.name())
        ):
            return a . string
        self._reset(mark)
        return None

    @memoize
    def if_stmt(self) -> Optional[ast . If]:
        # if_stmt: invalid_if_stmt | 'if' named_expression ':' block elif_stmt | 'if' named_expression ':' block else_block?
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (invalid_if_stmt := self.invalid_if_stmt())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (literal := self.expect('if'))
            and
            (a := self.named_expression())
            and
            (literal_1 := self.expect(':'))
            and
            (b := self.block())
            and
            (c := self.elif_stmt())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . If ( test = a , body = b , orelse = c or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('if'))
            and
            (a := self.named_expression())
            and
            (literal_1 := self.expect(':'))
            and
            (b := self.block())
            and
            (c := self.else_block(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . If ( test = a , body = b , orelse = c or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def elif_stmt(self) -> Optional[List [ast . If]]:
        # elif_stmt: invalid_elif_stmt | 'elif' named_expression ':' block elif_stmt | 'elif' named_expression ':' block else_block?
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (invalid_elif_stmt := self.invalid_elif_stmt())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (literal := self.expect('elif'))
            and
            (a := self.named_expression())
            and
            (literal_1 := self.expect(':'))
            and
            (b := self.block())
            and
            (c := self.elif_stmt())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return [ast . If ( test = a , body = b , orelse = c , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )]
        self._reset(mark)
        if (
            (literal := self.expect('elif'))
            and
            (a := self.named_expression())
            and
            (literal_1 := self.expect(':'))
            and
            (b := self.block())
            and
            (c := self.else_block(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return [ast . If ( test = a , body = b , orelse = c or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )]
        self._reset(mark)
        return None

    @memoize
    def else_block(self) -> Optional[list]:
        # else_block: invalid_else_stmt | 'else' &&':' block
        mark = self._mark()
        if (
            (invalid_else_stmt := self.invalid_else_stmt())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (literal := self.expect('else'))
            and
            (forced := self.expect_forced(self.expect(':'), "':'"))
            and
            (b := self.block())
        ):
            return b
        self._reset(mark)
        return None

    @memoize
    def while_stmt(self) -> Optional[ast . While]:
        # while_stmt: invalid_while_stmt | 'while' named_expression ':' block else_block?
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (invalid_while_stmt := self.invalid_while_stmt())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (literal := self.expect('while'))
            and
            (a := self.named_expression())
            and
            (literal_1 := self.expect(':'))
            and
            (b := self.block())
            and
            (c := self.else_block(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . While ( test = a , body = b , orelse = c or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def for_stmt(self) -> Optional[Union [ast . For , ast . AsyncFor]]:
        # for_stmt: invalid_for_stmt | 'for' star_targets 'in' ~ star_expressions &&':' TYPE_COMMENT? block else_block? | 'async' 'for' star_targets 'in' ~ star_expressions ':' TYPE_COMMENT? block else_block? | invalid_for_target
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (invalid_for_stmt := self.invalid_for_stmt())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        cut = False
        if (
            (literal := self.expect('for'))
            and
            (t := self.star_targets())
            and
            (literal_1 := self.expect('in'))
            and
            (cut := True)
            and
            (ex := self.star_expressions())
            and
            (forced := self.expect_forced(self.expect(':'), "':'"))
            and
            (tc := self.type_comment(),)
            and
            (b := self.block())
            and
            (el := self.else_block(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . For ( target = t , iter = ex , body = b , orelse = el or [] , type_comment = tc , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if cut: return None
        cut = False
        if (
            (literal := self.expect('async'))
            and
            (literal_1 := self.expect('for'))
            and
            (t := self.star_targets())
            and
            (literal_2 := self.expect('in'))
            and
            (cut := True)
            and
            (ex := self.star_expressions())
            and
            (literal_3 := self.expect(':'))
            and
            (tc := self.type_comment(),)
            and
            (b := self.block())
            and
            (el := self.else_block(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 5 ) , "Async for loops are" , ast . AsyncFor ( target = t , iter = ex , body = b , orelse = el or [] , type_comment = tc , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) )
        self._reset(mark)
        if cut: return None
        if (
            (invalid_for_target := self.invalid_for_target())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def with_stmt(self) -> Optional[Union [ast . With , ast . AsyncWith]]:
        # with_stmt: invalid_with_stmt_indent | 'with' '(' ','.with_item+ ','? ')' ':' block | 'with' ','.with_item+ ':' TYPE_COMMENT? block | 'async' 'with' '(' ','.with_item+ ','? ')' ':' block | 'async' 'with' ','.with_item+ ':' TYPE_COMMENT? block | invalid_with_stmt
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (invalid_with_stmt_indent := self.invalid_with_stmt_indent())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (literal := self.expect('with'))
            and
            (literal_1 := self.expect('('))
            and
            (a := self._gather_71())
            and
            (opt := self.expect(','),)
            and
            (literal_2 := self.expect(')'))
            and
            (literal_3 := self.expect(':'))
            and
            (b := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . With ( items = a , body = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('with'))
            and
            (a := self._gather_73())
            and
            (literal_1 := self.expect(':'))
            and
            (tc := self.type_comment(),)
            and
            (b := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . With ( items = a , body = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('async'))
            and
            (literal_1 := self.expect('with'))
            and
            (literal_2 := self.expect('('))
            and
            (a := self._gather_75())
            and
            (opt := self.expect(','),)
            and
            (literal_3 := self.expect(')'))
            and
            (literal_4 := self.expect(':'))
            and
            (b := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 5 ) , "Async with statements are" , ast . AsyncWith ( items = a , body = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) )
        self._reset(mark)
        if (
            (literal := self.expect('async'))
            and
            (literal_1 := self.expect('with'))
            and
            (a := self._gather_77())
            and
            (literal_2 := self.expect(':'))
            and
            (tc := self.type_comment(),)
            and
            (b := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 5 ) , "Async with statements are" , ast . AsyncWith ( items = a , body = b , type_comment = tc , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) )
        self._reset(mark)
        if (
            (invalid_with_stmt := self.invalid_with_stmt())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def with_item(self) -> Optional[ast . withitem]:
        # with_item: expression 'as' star_target &(',' | ')' | ':') | invalid_with_item | expression
        mark = self._mark()
        if (
            (e := self.expression())
            and
            (literal := self.expect('as'))
            and
            (t := self.star_target())
            and
            self.positive_lookahead(self._tmp_79, )
        ):
            return ast . withitem ( context_expr = e , optional_vars = t )
        self._reset(mark)
        if (
            (invalid_with_item := self.invalid_with_item())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (e := self.expression())
        ):
            return ast . withitem ( context_expr = e , optional_vars = None )
        self._reset(mark)
        return None

    @memoize
    def try_stmt(self) -> Optional[ast . Try]:
        # try_stmt: invalid_try_stmt | 'try' &&':' block finally_block | 'try' &&':' block except_block+ else_block? finally_block?
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (invalid_try_stmt := self.invalid_try_stmt())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (literal := self.expect('try'))
            and
            (forced := self.expect_forced(self.expect(':'), "':'"))
            and
            (b := self.block())
            and
            (f := self.finally_block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Try ( body = b , handlers = [] , orelse = [] , finalbody = f , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('try'))
            and
            (forced := self.expect_forced(self.expect(':'), "':'"))
            and
            (b := self.block())
            and
            (ex := self._loop1_80())
            and
            (el := self.else_block(),)
            and
            (f := self.finally_block(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Try ( body = b , handlers = ex , orelse = el or [] , finalbody = f or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def except_block(self) -> Optional[ast . ExceptHandler]:
        # except_block: invalid_except_stmt_indent | 'except' expression ['as' NAME] ':' block | 'except' ':' block | invalid_except_stmt
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (invalid_except_stmt_indent := self.invalid_except_stmt_indent())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (literal := self.expect('except'))
            and
            (e := self.expression())
            and
            (t := self._tmp_81(),)
            and
            (literal_1 := self.expect(':'))
            and
            (b := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . ExceptHandler ( type = e , name = t , body = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('except'))
            and
            (literal_1 := self.expect(':'))
            and
            (b := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . ExceptHandler ( type = None , name = None , body = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (invalid_except_stmt := self.invalid_except_stmt())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def finally_block(self) -> Optional[list]:
        # finally_block: invalid_finally_stmt | 'finally' &&':' block
        mark = self._mark()
        if (
            (invalid_finally_stmt := self.invalid_finally_stmt())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (literal := self.expect('finally'))
            and
            (forced := self.expect_forced(self.expect(':'), "':'"))
            and
            (a := self.block())
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def match_stmt(self) -> Optional["ast.Match"]:
        # match_stmt: "match" subject_expr ':' NEWLINE INDENT case_block+ DEDENT | invalid_match_stmt
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect("match"))
            and
            (subject := self.subject_expr())
            and
            (literal_1 := self.expect(':'))
            and
            (_newline := self.expect('NEWLINE'))
            and
            (_indent := self.expect('INDENT'))
            and
            (cases := self._loop1_82())
            and
            (_dedent := self.expect('DEDENT'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Match ( subject = subject , cases = cases , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (invalid_match_stmt := self.invalid_match_stmt())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def subject_expr(self) -> Optional[Any]:
        # subject_expr: star_named_expression ',' star_named_expressions? | named_expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (value := self.star_named_expression())
            and
            (literal := self.expect(','))
            and
            (values := self.star_named_expressions(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 10 ) , "Pattern matching is" , ast . Tuple ( elts = [value] + ( values or [] ) , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) )
        self._reset(mark)
        if (
            (e := self.named_expression())
        ):
            return self . check_version ( ( 3 , 10 ) , "Pattern matching is" , e )
        self._reset(mark)
        return None

    @memoize
    def case_block(self) -> Optional["ast.match_case"]:
        # case_block: invalid_case_block | "case" patterns guard? ':' block
        mark = self._mark()
        if (
            (invalid_case_block := self.invalid_case_block())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (literal := self.expect("case"))
            and
            (pattern := self.patterns())
            and
            (guard := self.guard(),)
            and
            (literal_1 := self.expect(':'))
            and
            (body := self.block())
        ):
            return ast . match_case ( pattern = pattern , guard = guard , body = body )
        self._reset(mark)
        return None

    @memoize
    def guard(self) -> Optional[Any]:
        # guard: 'if' named_expression
        mark = self._mark()
        if (
            (literal := self.expect('if'))
            and
            (guard := self.named_expression())
        ):
            return guard
        self._reset(mark)
        return None

    @memoize
    def patterns(self) -> Optional[Any]:
        # patterns: open_sequence_pattern | pattern
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (patterns := self.open_sequence_pattern())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchSequence ( patterns = patterns , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (pattern := self.pattern())
        ):
            return pattern
        self._reset(mark)
        return None

    @memoize
    def pattern(self) -> Optional[Any]:
        # pattern: as_pattern | or_pattern
        mark = self._mark()
        if (
            (as_pattern := self.as_pattern())
        ):
            return as_pattern
        self._reset(mark)
        if (
            (or_pattern := self.or_pattern())
        ):
            return or_pattern
        self._reset(mark)
        return None

    @memoize
    def as_pattern(self) -> Optional["ast.MatchAs"]:
        # as_pattern: or_pattern 'as' pattern_capture_target | invalid_as_pattern
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (pattern := self.or_pattern())
            and
            (literal := self.expect('as'))
            and
            (target := self.pattern_capture_target())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchAs ( pattern = pattern , name = target , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (invalid_as_pattern := self.invalid_as_pattern())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def or_pattern(self) -> Optional["ast.MatchOr"]:
        # or_pattern: '|'.closed_pattern+
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (patterns := self._gather_83())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchOr ( patterns = patterns , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) if len ( patterns ) > 1 else patterns [0]
        self._reset(mark)
        return None

    @memoize
    def closed_pattern(self) -> Optional[Any]:
        # closed_pattern: literal_pattern | capture_pattern | wildcard_pattern | value_pattern | group_pattern | sequence_pattern | mapping_pattern | class_pattern
        mark = self._mark()
        if (
            (literal_pattern := self.literal_pattern())
        ):
            return literal_pattern
        self._reset(mark)
        if (
            (capture_pattern := self.capture_pattern())
        ):
            return capture_pattern
        self._reset(mark)
        if (
            (wildcard_pattern := self.wildcard_pattern())
        ):
            return wildcard_pattern
        self._reset(mark)
        if (
            (value_pattern := self.value_pattern())
        ):
            return value_pattern
        self._reset(mark)
        if (
            (group_pattern := self.group_pattern())
        ):
            return group_pattern
        self._reset(mark)
        if (
            (sequence_pattern := self.sequence_pattern())
        ):
            return sequence_pattern
        self._reset(mark)
        if (
            (mapping_pattern := self.mapping_pattern())
        ):
            return mapping_pattern
        self._reset(mark)
        if (
            (class_pattern := self.class_pattern())
        ):
            return class_pattern
        self._reset(mark)
        return None

    @memoize
    def literal_pattern(self) -> Optional[Any]:
        # literal_pattern: signed_number !('+' | '-') | complex_number | strings | 'None' | 'True' | 'False'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (value := self.signed_number())
            and
            self.negative_lookahead(self._tmp_85, )
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchValue ( value = value , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (value := self.complex_number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchValue ( value = value , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (value := self.strings())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchValue ( value = value , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('None'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchSingleton ( value = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('True'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchSingleton ( value = True , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('False'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchSingleton ( value = False , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def literal_expr(self) -> Optional[Any]:
        # literal_expr: signed_number !('+' | '-') | complex_number | strings | 'None' | 'True' | 'False'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (signed_number := self.signed_number())
            and
            self.negative_lookahead(self._tmp_86, )
        ):
            return signed_number
        self._reset(mark)
        if (
            (complex_number := self.complex_number())
        ):
            return complex_number
        self._reset(mark)
        if (
            (strings := self.strings())
        ):
            return strings
        self._reset(mark)
        if (
            (literal := self.expect('None'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('True'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = True , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('False'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = False , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def complex_number(self) -> Optional[Any]:
        # complex_number: signed_real_number '+' imaginary_number | signed_real_number '-' imaginary_number
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (real := self.signed_real_number())
            and
            (literal := self.expect('+'))
            and
            (imag := self.imaginary_number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = real , op = ast . Add ( ) , right = imag , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (real := self.signed_real_number())
            and
            (literal := self.expect('-'))
            and
            (imag := self.imaginary_number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = real , op = ast . Sub ( ) , right = imag , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def signed_number(self) -> Optional[Any]:
        # signed_number: NUMBER | '-' NUMBER
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = ast . literal_eval ( a . string ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('-'))
            and
            (a := self.number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . UnaryOp ( op = ast . USub ( ) , operand = ast . Constant ( value = ast . literal_eval ( a . string ) , lineno = a . start [0] , col_offset = a . start [1] , end_lineno = a . end [0] , end_col_offset = a . end [1] ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , )
        self._reset(mark)
        return None

    @memoize
    def signed_real_number(self) -> Optional[Any]:
        # signed_real_number: real_number | '-' real_number
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (real_number := self.real_number())
        ):
            return real_number
        self._reset(mark)
        if (
            (literal := self.expect('-'))
            and
            (real := self.real_number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . UnaryOp ( op = ast . USub ( ) , operand = real , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def real_number(self) -> Optional[ast . Constant]:
        # real_number: NUMBER
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (real := self.number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = self . ensure_real ( real . string ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def imaginary_number(self) -> Optional[ast . Constant]:
        # imaginary_number: NUMBER
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (imag := self.number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = self . ensure_imaginary ( imag . string ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def capture_pattern(self) -> Optional[Any]:
        # capture_pattern: pattern_capture_target
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (target := self.pattern_capture_target())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchAs ( pattern = None , name = target , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def pattern_capture_target(self) -> Optional[str]:
        # pattern_capture_target: !"_" NAME !('.' | '(' | '=')
        mark = self._mark()
        if (
            self.negative_lookahead(self.expect, "_")
            and
            (name := self.name())
            and
            self.negative_lookahead(self._tmp_87, )
        ):
            return name . string
        self._reset(mark)
        return None

    @memoize
    def wildcard_pattern(self) -> Optional["ast.MatchAs"]:
        # wildcard_pattern: "_"
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect("_"))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchAs ( pattern = None , target = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def value_pattern(self) -> Optional["ast.MatchValue"]:
        # value_pattern: attr !('.' | '(' | '=')
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (attr := self.attr())
            and
            self.negative_lookahead(self._tmp_88, )
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchValue ( value = attr , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize_left_rec
    def attr(self) -> Optional[ast . Attribute]:
        # attr: name_or_attr '.' NAME
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (value := self.name_or_attr())
            and
            (literal := self.expect('.'))
            and
            (attr := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Attribute ( value = value , attr = attr . string , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @logger
    def name_or_attr(self) -> Optional[Any]:
        # name_or_attr: attr | NAME
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (attr := self.attr())
        ):
            return attr
        self._reset(mark)
        if (
            (name := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Name ( id = name . string , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def group_pattern(self) -> Optional[Any]:
        # group_pattern: '(' pattern ')'
        mark = self._mark()
        if (
            (literal := self.expect('('))
            and
            (pattern := self.pattern())
            and
            (literal_1 := self.expect(')'))
        ):
            return pattern
        self._reset(mark)
        return None

    @memoize
    def sequence_pattern(self) -> Optional["ast.MatchSequence"]:
        # sequence_pattern: '[' maybe_sequence_pattern? ']' | '(' open_sequence_pattern? ')'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('['))
            and
            (patterns := self.maybe_sequence_pattern(),)
            and
            (literal_1 := self.expect(']'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchSequence ( patterns = patterns or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('('))
            and
            (patterns := self.open_sequence_pattern(),)
            and
            (literal_1 := self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchSequence ( patterns = patterns or [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def open_sequence_pattern(self) -> Optional[Any]:
        # open_sequence_pattern: maybe_star_pattern ',' maybe_sequence_pattern?
        mark = self._mark()
        if (
            (pattern := self.maybe_star_pattern())
            and
            (literal := self.expect(','))
            and
            (patterns := self.maybe_sequence_pattern(),)
        ):
            return [pattern] + ( patterns or [] )
        self._reset(mark)
        return None

    @memoize
    def maybe_sequence_pattern(self) -> Optional[Any]:
        # maybe_sequence_pattern: ','.maybe_star_pattern+ ','?
        mark = self._mark()
        if (
            (patterns := self._gather_89())
            and
            (opt := self.expect(','),)
        ):
            return patterns
        self._reset(mark)
        return None

    @memoize
    def maybe_star_pattern(self) -> Optional[Any]:
        # maybe_star_pattern: star_pattern | pattern
        mark = self._mark()
        if (
            (star_pattern := self.star_pattern())
        ):
            return star_pattern
        self._reset(mark)
        if (
            (pattern := self.pattern())
        ):
            return pattern
        self._reset(mark)
        return None

    @memoize
    def star_pattern(self) -> Optional[Any]:
        # star_pattern: '*' pattern_capture_target | '*' wildcard_pattern
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('*'))
            and
            (target := self.pattern_capture_target())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchStar ( name = target , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('*'))
            and
            (wildcard_pattern := self.wildcard_pattern())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchStar ( target = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def mapping_pattern(self) -> Optional[Any]:
        # mapping_pattern: '{' '}' | '{' double_star_pattern ','? '}' | '{' items_pattern ',' double_star_pattern ','? '}' | '{' items_pattern ','? '}'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('{'))
            and
            (literal_1 := self.expect('}'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchMapping ( keys = [] , patterns = [] , rest = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('{'))
            and
            (rest := self.double_star_pattern())
            and
            (opt := self.expect(','),)
            and
            (literal_1 := self.expect('}'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchMapping ( keys = [] , patterns = [] , rest = rest , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('{'))
            and
            (items := self.items_pattern())
            and
            (literal_1 := self.expect(','))
            and
            (rest := self.double_star_pattern())
            and
            (opt := self.expect(','),)
            and
            (literal_2 := self.expect('}'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchMapping ( keys = [k for k , _ in items] , patterns = [p for _ , p in items] , rest = rest , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , )
        self._reset(mark)
        if (
            (literal := self.expect('{'))
            and
            (items := self.items_pattern())
            and
            (opt := self.expect(','),)
            and
            (literal_1 := self.expect('}'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchMapping ( keys = [k for k , _ in items] , patterns = [p for _ , p in items] , rest = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , )
        self._reset(mark)
        return None

    @memoize
    def items_pattern(self) -> Optional[Any]:
        # items_pattern: ','.key_value_pattern+
        mark = self._mark()
        if (
            (_gather_91 := self._gather_91())
        ):
            return _gather_91
        self._reset(mark)
        return None

    @memoize
    def key_value_pattern(self) -> Optional[Any]:
        # key_value_pattern: (literal_expr | attr) ':' pattern
        mark = self._mark()
        if (
            (key := self._tmp_93())
            and
            (literal := self.expect(':'))
            and
            (pattern := self.pattern())
        ):
            return ( key , pattern )
        self._reset(mark)
        return None

    @memoize
    def double_star_pattern(self) -> Optional[Any]:
        # double_star_pattern: '**' pattern_capture_target
        mark = self._mark()
        if (
            (literal := self.expect('**'))
            and
            (target := self.pattern_capture_target())
        ):
            return target
        self._reset(mark)
        return None

    @memoize
    def class_pattern(self) -> Optional["ast.MatchClass"]:
        # class_pattern: name_or_attr '(' ')' | name_or_attr '(' positional_patterns ','? ')' | name_or_attr '(' keyword_patterns ','? ')' | name_or_attr '(' positional_patterns ',' keyword_patterns ','? ')'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (cls := self.name_or_attr())
            and
            (literal := self.expect('('))
            and
            (literal_1 := self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchClass ( cls = cls , patterns = [] , kwd_attrs = [] , kwd_patterns = [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (cls := self.name_or_attr())
            and
            (literal := self.expect('('))
            and
            (patterns := self.positional_patterns())
            and
            (opt := self.expect(','),)
            and
            (literal_1 := self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchClass ( cls = cls , patterns = patterns , kwd_attrs = [] , kwd_patterns = [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (cls := self.name_or_attr())
            and
            (literal := self.expect('('))
            and
            (keywords := self.keyword_patterns())
            and
            (opt := self.expect(','),)
            and
            (literal_1 := self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchClass ( cls = cls , patterns = [] , kwd_attrs = [k for k , _ in keywords] , kwd_patterns = [p for _ , p in keywords] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , )
        self._reset(mark)
        if (
            (cls := self.name_or_attr())
            and
            (literal := self.expect('('))
            and
            (patterns := self.positional_patterns())
            and
            (literal_1 := self.expect(','))
            and
            (keywords := self.keyword_patterns())
            and
            (opt := self.expect(','),)
            and
            (literal_2 := self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . MatchClass ( cls = cls , patterns = patterns , kwd_attrs = [k for k , _ in keywords] , kwd_patterns = [p for _ , p in keywords] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , )
        self._reset(mark)
        return None

    @memoize
    def positional_patterns(self) -> Optional[Any]:
        # positional_patterns: ','.pattern+
        mark = self._mark()
        if (
            (args := self._gather_94())
        ):
            return args
        self._reset(mark)
        return None

    @memoize
    def keyword_patterns(self) -> Optional[Any]:
        # keyword_patterns: ','.keyword_pattern+
        mark = self._mark()
        if (
            (_gather_96 := self._gather_96())
        ):
            return _gather_96
        self._reset(mark)
        return None

    @memoize
    def keyword_pattern(self) -> Optional[Any]:
        # keyword_pattern: NAME '=' pattern
        mark = self._mark()
        if (
            (arg := self.name())
            and
            (literal := self.expect('='))
            and
            (value := self.pattern())
        ):
            return ( arg . string , value )
        self._reset(mark)
        return None

    @memoize
    def return_stmt(self) -> Optional[ast . Return]:
        # return_stmt: 'return' star_expressions?
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('return'))
            and
            (a := self.star_expressions(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Return ( value = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def raise_stmt(self) -> Optional[ast . Raise]:
        # raise_stmt: 'raise' expression ['from' expression] | 'raise'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('raise'))
            and
            (a := self.expression())
            and
            (b := self._tmp_98(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Raise ( exc = a , cause = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('raise'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Raise ( exc = None , cause = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def function_def(self) -> Optional[Union [ast . FunctionDef , ast . AsyncFunctionDef]]:
        # function_def: decorators function_def_raw | function_def_raw
        mark = self._mark()
        if (
            (d := self.decorators())
            and
            (f := self.function_def_raw())
        ):
            return self . set_decorators ( f , d )
        self._reset(mark)
        if (
            (f := self.function_def_raw())
        ):
            return self . set_decorators ( f , [] )
        self._reset(mark)
        return None

    @memoize
    def function_def_raw(self) -> Optional[Union [ast . FunctionDef , ast . AsyncFunctionDef]]:
        # function_def_raw: invalid_def_raw | 'def' NAME '(' params? ')' ['->' expression] &&':' func_type_comment? block | 'async' 'def' NAME '(' params? ')' ['->' expression] &&':' func_type_comment? block
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (invalid_def_raw := self.invalid_def_raw())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (literal := self.expect('def'))
            and
            (n := self.name())
            and
            (literal_1 := self.expect('('))
            and
            (params := self.params(),)
            and
            (literal_2 := self.expect(')'))
            and
            (a := self._tmp_99(),)
            and
            (forced := self.expect_forced(self.expect(':'), "':'"))
            and
            (tc := self.func_type_comment(),)
            and
            (b := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . FunctionDef ( name = n . string , args = params or self . make_arguments ( None , [] , None , [] , None ) , returns = a , body = b , type_comment = tc , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , )
        self._reset(mark)
        if (
            (literal := self.expect('async'))
            and
            (literal_1 := self.expect('def'))
            and
            (n := self.name())
            and
            (literal_2 := self.expect('('))
            and
            (params := self.params(),)
            and
            (literal_3 := self.expect(')'))
            and
            (a := self._tmp_100(),)
            and
            (forced := self.expect_forced(self.expect(':'), "':'"))
            and
            (tc := self.func_type_comment(),)
            and
            (b := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 5 ) , "Async functions are" , ast . AsyncFunctionDef ( name = n . string , args = params or self . make_arguments ( None , [] , None , [] , None ) , returns = a , body = b , type_comment = tc , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) )
        self._reset(mark)
        return None

    @memoize
    def func_type_comment(self) -> Optional[Any]:
        # func_type_comment: NEWLINE TYPE_COMMENT &(NEWLINE INDENT) | invalid_double_type_comments | TYPE_COMMENT
        mark = self._mark()
        if (
            (_newline := self.expect('NEWLINE'))
            and
            (t := self.type_comment())
            and
            self.positive_lookahead(self._tmp_101, )
        ):
            return t . string
        self._reset(mark)
        if (
            (invalid_double_type_comments := self.invalid_double_type_comments())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (type_comment := self.type_comment())
        ):
            return type_comment
        self._reset(mark)
        return None

    @memoize
    def params(self) -> Optional[Any]:
        # params: invalid_parameters | parameters
        mark = self._mark()
        if (
            (invalid_parameters := self.invalid_parameters())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (parameters := self.parameters())
        ):
            return parameters
        self._reset(mark)
        return None

    @memoize
    def parameters(self) -> Optional[ast . arguments]:
        # parameters: slash_no_default param_no_default* param_with_default* star_etc? | slash_with_default param_with_default* star_etc? | param_no_default+ param_with_default* star_etc? | param_with_default+ star_etc? | star_etc
        mark = self._mark()
        if (
            (a := self.slash_no_default())
            and
            (b := self._loop0_102(),)
            and
            (c := self._loop0_103(),)
            and
            (d := self.star_etc(),)
        ):
            return self . check_version ( ( 3 , 8 ) , "Positional only arguments are" , self . make_arguments ( a , [] , b , c , d ) )
        self._reset(mark)
        if (
            (a := self.slash_with_default())
            and
            (b := self._loop0_104(),)
            and
            (c := self.star_etc(),)
        ):
            return self . check_version ( ( 3 , 8 ) , "Positional only arguments are" , self . make_arguments ( None , a , None , b , c ) , )
        self._reset(mark)
        if (
            (a := self._loop1_105())
            and
            (b := self._loop0_106(),)
            and
            (c := self.star_etc(),)
        ):
            return self . make_arguments ( None , [] , a , b , c )
        self._reset(mark)
        if (
            (a := self._loop1_107())
            and
            (b := self.star_etc(),)
        ):
            return self . make_arguments ( None , [] , None , a , b )
        self._reset(mark)
        if (
            (a := self.star_etc())
        ):
            return self . make_arguments ( None , [] , None , None , a )
        self._reset(mark)
        return None

    @memoize
    def slash_no_default(self) -> Optional[List [Tuple [ast . arg , None]]]:
        # slash_no_default: param_no_default+ '/' ',' | param_no_default+ '/' &')'
        mark = self._mark()
        if (
            (a := self._loop1_108())
            and
            (literal := self.expect('/'))
            and
            (literal_1 := self.expect(','))
        ):
            return [( p , None ) for p in a]
        self._reset(mark)
        if (
            (a := self._loop1_109())
            and
            (literal := self.expect('/'))
            and
            self.positive_lookahead(self.expect, ')')
        ):
            return [( p , None ) for p in a]
        self._reset(mark)
        return None

    @memoize
    def slash_with_default(self) -> Optional[List [Tuple [ast . arg , Any]]]:
        # slash_with_default: param_no_default* param_with_default+ '/' ',' | param_no_default* param_with_default+ '/' &')'
        mark = self._mark()
        if (
            (a := self._loop0_110(),)
            and
            (b := self._loop1_111())
            and
            (literal := self.expect('/'))
            and
            (literal_1 := self.expect(','))
        ):
            return ( [( p , None ) for p in a] if a else [] ) + b
        self._reset(mark)
        if (
            (a := self._loop0_112(),)
            and
            (b := self._loop1_113())
            and
            (literal := self.expect('/'))
            and
            self.positive_lookahead(self.expect, ')')
        ):
            return ( [( p , None ) for p in a] if a else [] ) + b
        self._reset(mark)
        return None

    @memoize
    def star_etc(self) -> Optional[Tuple [Optional [ast . arg] , List [Tuple [ast . arg , Any]] , Optional [ast . arg]]]:
        # star_etc: '*' param_no_default param_maybe_default* kwds? | '*' ',' param_maybe_default+ kwds? | kwds | invalid_star_etc
        mark = self._mark()
        if (
            (literal := self.expect('*'))
            and
            (a := self.param_no_default())
            and
            (b := self._loop0_114(),)
            and
            (c := self.kwds(),)
        ):
            return ( a , b , c )
        self._reset(mark)
        if (
            (literal := self.expect('*'))
            and
            (literal_1 := self.expect(','))
            and
            (b := self._loop1_115())
            and
            (c := self.kwds(),)
        ):
            return ( None , b , c )
        self._reset(mark)
        if (
            (a := self.kwds())
        ):
            return ( None , [] , a )
        self._reset(mark)
        if (
            (invalid_star_etc := self.invalid_star_etc())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def kwds(self) -> Optional[Any]:
        # kwds: '**' param_no_default
        mark = self._mark()
        if (
            (literal := self.expect('**'))
            and
            (a := self.param_no_default())
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def param_no_default(self) -> Optional[ast . arg]:
        # param_no_default: param ',' TYPE_COMMENT? | param TYPE_COMMENT? &')'
        mark = self._mark()
        if (
            (a := self.param())
            and
            (literal := self.expect(','))
            and
            (tc := self.type_comment(),)
        ):
            return self . set_arg_type_comment ( a , tc )
        self._reset(mark)
        if (
            (a := self.param())
            and
            (tc := self.type_comment(),)
            and
            self.positive_lookahead(self.expect, ')')
        ):
            return self . set_arg_type_comment ( a , tc )
        self._reset(mark)
        return None

    @memoize
    def param_with_default(self) -> Optional[Tuple [ast . arg , Any]]:
        # param_with_default: param default ',' TYPE_COMMENT? | param default TYPE_COMMENT? &')'
        mark = self._mark()
        if (
            (a := self.param())
            and
            (c := self.default())
            and
            (literal := self.expect(','))
            and
            (tc := self.type_comment(),)
        ):
            return ( self . set_arg_type_comment ( a , tc ) , c )
        self._reset(mark)
        if (
            (a := self.param())
            and
            (c := self.default())
            and
            (tc := self.type_comment(),)
            and
            self.positive_lookahead(self.expect, ')')
        ):
            return ( self . set_arg_type_comment ( a , tc ) , c )
        self._reset(mark)
        return None

    @memoize
    def param_maybe_default(self) -> Optional[Tuple [ast . arg , Any]]:
        # param_maybe_default: param default? ',' TYPE_COMMENT? | param default? TYPE_COMMENT? &')'
        mark = self._mark()
        if (
            (a := self.param())
            and
            (c := self.default(),)
            and
            (literal := self.expect(','))
            and
            (tc := self.type_comment(),)
        ):
            return ( self . set_arg_type_comment ( a , tc ) , c )
        self._reset(mark)
        if (
            (a := self.param())
            and
            (c := self.default(),)
            and
            (tc := self.type_comment(),)
            and
            self.positive_lookahead(self.expect, ')')
        ):
            return ( self . set_arg_type_comment ( a , tc ) , c )
        self._reset(mark)
        return None

    @memoize
    def param(self) -> Optional[Any]:
        # param: NAME annotation?
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
            and
            (b := self.annotation(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . arg ( arg = a . string , annotation = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def annotation(self) -> Optional[Any]:
        # annotation: ':' expression
        mark = self._mark()
        if (
            (literal := self.expect(':'))
            and
            (a := self.expression())
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def default(self) -> Optional[Any]:
        # default: '=' expression
        mark = self._mark()
        if (
            (literal := self.expect('='))
            and
            (a := self.expression())
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def decorators(self) -> Optional[Any]:
        # decorators: decorator+
        mark = self._mark()
        if (
            (_loop1_116 := self._loop1_116())
        ):
            return _loop1_116
        self._reset(mark)
        return None

    @memoize
    def decorator(self) -> Optional[Any]:
        # decorator: ('@' dec_maybe_call NEWLINE) | ('@' named_expression NEWLINE)
        mark = self._mark()
        if (
            (a := self._tmp_117())
        ):
            return a
        self._reset(mark)
        if (
            (a := self._tmp_118())
        ):
            return self . check_version ( ( 3 , 9 ) , "Generic decorator are" , a )
        self._reset(mark)
        return None

    @memoize
    def dec_maybe_call(self) -> Optional[Any]:
        # dec_maybe_call: dec_primary '(' arguments ')' | dec_primary
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (dn := self.dec_primary())
            and
            (literal := self.expect('('))
            and
            (z := self.arguments())
            and
            (literal_1 := self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Call ( func = dn , args = z [0] , keywords = z [1] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (dec_primary := self.dec_primary())
        ):
            return dec_primary
        self._reset(mark)
        return None

    @memoize_left_rec
    def dec_primary(self) -> Optional[Any]:
        # dec_primary: dec_primary '.' NAME | NAME
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.dec_primary())
            and
            (literal := self.expect('.'))
            and
            (b := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Attribute ( value = a , attr = b . string , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Name ( id = a . string , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def class_def(self) -> Optional[ast . ClassDef]:
        # class_def: decorators class_def_raw | class_def_raw
        mark = self._mark()
        if (
            (a := self.decorators())
            and
            (b := self.class_def_raw())
        ):
            return self . set_decorators ( b , a )
        self._reset(mark)
        if (
            (class_def_raw := self.class_def_raw())
        ):
            return class_def_raw
        self._reset(mark)
        return None

    @memoize
    def class_def_raw(self) -> Optional[ast . ClassDef]:
        # class_def_raw: invalid_class_def_raw | 'class' NAME ['(' arguments? ')'] &&':' block
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (invalid_class_def_raw := self.invalid_class_def_raw())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (literal := self.expect('class'))
            and
            (a := self.name())
            and
            (b := self._tmp_119(),)
            and
            (forced := self.expect_forced(self.expect(':'), "':'"))
            and
            (c := self.block())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . ClassDef ( a . string , bases = b [0] if b else [] , keywords = b [1] if b else [] , body = c , decorator_list = [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , )
        self._reset(mark)
        return None

    @memoize
    def block(self) -> Optional[list]:
        # block: NEWLINE INDENT statements DEDENT | simple_stmts | invalid_block
        mark = self._mark()
        if (
            (_newline := self.expect('NEWLINE'))
            and
            (_indent := self.expect('INDENT'))
            and
            (a := self.statements())
            and
            (_dedent := self.expect('DEDENT'))
        ):
            return a
        self._reset(mark)
        if (
            (simple_stmts := self.simple_stmts())
        ):
            return simple_stmts
        self._reset(mark)
        if (
            (invalid_block := self.invalid_block())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def star_expressions(self) -> Optional[Any]:
        # star_expressions: star_expression ((',' star_expression))+ ','? | star_expression ',' | star_expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.star_expression())
            and
            (b := self._loop1_120())
            and
            (opt := self.expect(','),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Tuple ( elts = [a] + b , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.star_expression())
            and
            (literal := self.expect(','))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Tuple ( elts = [a] , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (star_expression := self.star_expression())
        ):
            return star_expression
        self._reset(mark)
        return None

    @memoize
    def star_expression(self) -> Optional[Any]:
        # star_expression: '*' bitwise_or | expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('*'))
            and
            (a := self.bitwise_or())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Starred ( value = a , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (expression := self.expression())
        ):
            return expression
        self._reset(mark)
        return None

    @memoize
    def star_named_expressions(self) -> Optional[Any]:
        # star_named_expressions: ','.star_named_expression+ ','?
        mark = self._mark()
        if (
            (a := self._gather_121())
            and
            (opt := self.expect(','),)
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def star_named_expression(self) -> Optional[Any]:
        # star_named_expression: '*' bitwise_or | named_expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('*'))
            and
            (a := self.bitwise_or())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Starred ( value = a , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (named_expression := self.named_expression())
        ):
            return named_expression
        self._reset(mark)
        return None

    @memoize
    def assignment_expression(self) -> Optional[Any]:
        # assignment_expression: NAME ':=' ~ expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        cut = False
        if (
            (a := self.name())
            and
            (literal := self.expect(':='))
            and
            (cut := True)
            and
            (b := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 8 ) , "The ':=' operator is" , ast . NamedExpr ( target = ast . Name ( id = a . string , ctx = Store , lineno = a . start [0] , col_offset = a . start [1] , end_lineno = a . end [0] , end_col_offset = a . end [1] ) , value = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , ) )
        self._reset(mark)
        if cut: return None
        return None

    @memoize
    def named_expression(self) -> Optional[Any]:
        # named_expression: assignment_expression | invalid_named_expression | expression !':='
        mark = self._mark()
        if (
            (assignment_expression := self.assignment_expression())
        ):
            return assignment_expression
        self._reset(mark)
        if (
            (invalid_named_expression := self.invalid_named_expression())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (a := self.expression())
            and
            self.negative_lookahead(self.expect, ':=')
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def annotated_rhs(self) -> Optional[Any]:
        # annotated_rhs: yield_expr | star_expressions
        mark = self._mark()
        if (
            (yield_expr := self.yield_expr())
        ):
            return yield_expr
        self._reset(mark)
        if (
            (star_expressions := self.star_expressions())
        ):
            return star_expressions
        self._reset(mark)
        return None

    @memoize
    def expressions(self) -> Optional[Any]:
        # expressions: expression ((',' expression))+ ','? | expression ',' | expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.expression())
            and
            (b := self._loop1_123())
            and
            (opt := self.expect(','),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Tuple ( elts = [a] + b , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.expression())
            and
            (literal := self.expect(','))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Tuple ( elts = [a] , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (expression := self.expression())
        ):
            return expression
        self._reset(mark)
        return None

    @memoize
    def expression(self) -> Optional[Any]:
        # expression: invalid_expression | disjunction 'if' disjunction 'else' expression | disjunction | lambdef
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (invalid_expression := self.invalid_expression())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (a := self.disjunction())
            and
            (literal := self.expect('if'))
            and
            (b := self.disjunction())
            and
            (literal_1 := self.expect('else'))
            and
            (c := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . IfExp ( body = a , test = b , orelse = c , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (disjunction := self.disjunction())
        ):
            return disjunction
        self._reset(mark)
        if (
            (lambdef := self.lambdef())
        ):
            return lambdef
        self._reset(mark)
        return None

    @memoize
    def lambdef(self) -> Optional[Any]:
        # lambdef: 'lambda' lambda_params? ':' expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('lambda'))
            and
            (a := self.lambda_params(),)
            and
            (literal_1 := self.expect(':'))
            and
            (b := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Lambda ( args = a or self . make_arguments ( None , [] , None , [] , ( None , [] , None ) ) , body = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def lambda_params(self) -> Optional[Any]:
        # lambda_params: invalid_lambda_parameters | lambda_parameters
        mark = self._mark()
        if (
            (invalid_lambda_parameters := self.invalid_lambda_parameters())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (lambda_parameters := self.lambda_parameters())
        ):
            return lambda_parameters
        self._reset(mark)
        return None

    @memoize
    def lambda_parameters(self) -> Optional[ast . arguments]:
        # lambda_parameters: lambda_slash_no_default lambda_param_no_default* lambda_param_with_default* lambda_star_etc? | lambda_slash_with_default lambda_param_with_default* lambda_star_etc? | lambda_param_no_default+ lambda_param_with_default* lambda_star_etc? | lambda_param_with_default+ lambda_star_etc? | lambda_star_etc
        mark = self._mark()
        if (
            (a := self.lambda_slash_no_default())
            and
            (b := self._loop0_124(),)
            and
            (c := self._loop0_125(),)
            and
            (d := self.lambda_star_etc(),)
        ):
            return self . make_arguments ( a , [] , b , c , d )
        self._reset(mark)
        if (
            (a := self.lambda_slash_with_default())
            and
            (b := self._loop0_126(),)
            and
            (c := self.lambda_star_etc(),)
        ):
            return self . make_arguments ( None , a , None , b , c )
        self._reset(mark)
        if (
            (a := self._loop1_127())
            and
            (b := self._loop0_128(),)
            and
            (c := self.lambda_star_etc(),)
        ):
            return self . make_arguments ( None , [] , a , b , c )
        self._reset(mark)
        if (
            (a := self._loop1_129())
            and
            (b := self.lambda_star_etc(),)
        ):
            return self . make_arguments ( None , [] , None , a , b )
        self._reset(mark)
        if (
            (a := self.lambda_star_etc())
        ):
            return self . make_arguments ( None , [] , None , [] , a )
        self._reset(mark)
        return None

    @memoize
    def lambda_slash_no_default(self) -> Optional[List [Tuple [ast . arg , None]]]:
        # lambda_slash_no_default: lambda_param_no_default+ '/' ',' | lambda_param_no_default+ '/' &':'
        mark = self._mark()
        if (
            (a := self._loop1_130())
            and
            (literal := self.expect('/'))
            and
            (literal_1 := self.expect(','))
        ):
            return [( p , None ) for p in a]
        self._reset(mark)
        if (
            (a := self._loop1_131())
            and
            (literal := self.expect('/'))
            and
            self.positive_lookahead(self.expect, ':')
        ):
            return [( p , None ) for p in a]
        self._reset(mark)
        return None

    @memoize
    def lambda_slash_with_default(self) -> Optional[List [Tuple [ast . arg , Any]]]:
        # lambda_slash_with_default: lambda_param_no_default* lambda_param_with_default+ '/' ',' | lambda_param_no_default* lambda_param_with_default+ '/' &':'
        mark = self._mark()
        if (
            (a := self._loop0_132(),)
            and
            (b := self._loop1_133())
            and
            (literal := self.expect('/'))
            and
            (literal_1 := self.expect(','))
        ):
            return ( [( p , None ) for p in a] if a else [] ) + b
        self._reset(mark)
        if (
            (a := self._loop0_134(),)
            and
            (b := self._loop1_135())
            and
            (literal := self.expect('/'))
            and
            self.positive_lookahead(self.expect, ':')
        ):
            return ( [( p , None ) for p in a] if a else [] ) + b
        self._reset(mark)
        return None

    @memoize
    def lambda_star_etc(self) -> Optional[Tuple [Optional [ast . arg] , List [Tuple [ast . arg , Any]] , Optional [ast . arg]]]:
        # lambda_star_etc: '*' lambda_param_no_default lambda_param_maybe_default* lambda_kwds? | '*' ',' lambda_param_maybe_default+ lambda_kwds? | lambda_kwds | invalid_lambda_star_etc
        mark = self._mark()
        if (
            (literal := self.expect('*'))
            and
            (a := self.lambda_param_no_default())
            and
            (b := self._loop0_136(),)
            and
            (c := self.lambda_kwds(),)
        ):
            return ( a , b , c )
        self._reset(mark)
        if (
            (literal := self.expect('*'))
            and
            (literal_1 := self.expect(','))
            and
            (b := self._loop1_137())
            and
            (c := self.lambda_kwds(),)
        ):
            return ( None , b , c )
        self._reset(mark)
        if (
            (a := self.lambda_kwds())
        ):
            return ( None , [] , a )
        self._reset(mark)
        if (
            (invalid_lambda_star_etc := self.invalid_lambda_star_etc())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def lambda_kwds(self) -> Optional[ast . arg]:
        # lambda_kwds: '**' lambda_param_no_default
        mark = self._mark()
        if (
            (literal := self.expect('**'))
            and
            (a := self.lambda_param_no_default())
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def lambda_param_no_default(self) -> Optional[ast . arg]:
        # lambda_param_no_default: lambda_param ',' | lambda_param &':'
        mark = self._mark()
        if (
            (a := self.lambda_param())
            and
            (literal := self.expect(','))
        ):
            return a
        self._reset(mark)
        if (
            (a := self.lambda_param())
            and
            self.positive_lookahead(self.expect, ':')
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def lambda_param_with_default(self) -> Optional[Tuple [ast . arg , Any]]:
        # lambda_param_with_default: lambda_param default ',' | lambda_param default &':'
        mark = self._mark()
        if (
            (a := self.lambda_param())
            and
            (c := self.default())
            and
            (literal := self.expect(','))
        ):
            return ( a , c )
        self._reset(mark)
        if (
            (a := self.lambda_param())
            and
            (c := self.default())
            and
            self.positive_lookahead(self.expect, ':')
        ):
            return ( a , c )
        self._reset(mark)
        return None

    @memoize
    def lambda_param_maybe_default(self) -> Optional[Tuple [ast . arg , Any]]:
        # lambda_param_maybe_default: lambda_param default? ',' | lambda_param default? &':'
        mark = self._mark()
        if (
            (a := self.lambda_param())
            and
            (c := self.default(),)
            and
            (literal := self.expect(','))
        ):
            return ( a , c )
        self._reset(mark)
        if (
            (a := self.lambda_param())
            and
            (c := self.default(),)
            and
            self.positive_lookahead(self.expect, ':')
        ):
            return ( a , c )
        self._reset(mark)
        return None

    @memoize
    def lambda_param(self) -> Optional[ast . arg]:
        # lambda_param: NAME
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . arg ( arg = a . string , annotation = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def disjunction(self) -> Optional[Any]:
        # disjunction: conjunction (('or' conjunction))+ | conjunction
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.conjunction())
            and
            (b := self._loop1_138())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BoolOp ( op = ast . Or ( ) , values = [a] + b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (conjunction := self.conjunction())
        ):
            return conjunction
        self._reset(mark)
        return None

    @memoize
    def conjunction(self) -> Optional[Any]:
        # conjunction: inversion (('and' inversion))+ | inversion
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.inversion())
            and
            (b := self._loop1_139())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BoolOp ( op = ast . And ( ) , values = [a] + b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (inversion := self.inversion())
        ):
            return inversion
        self._reset(mark)
        return None

    @memoize
    def inversion(self) -> Optional[Any]:
        # inversion: 'not' inversion | comparison
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('not'))
            and
            (a := self.inversion())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . UnaryOp ( op = ast . Not ( ) , operand = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (comparison := self.comparison())
        ):
            return comparison
        self._reset(mark)
        return None

    @memoize
    def comparison(self) -> Optional[Any]:
        # comparison: bitwise_or compare_op_bitwise_or_pair+ | bitwise_or
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.bitwise_or())
            and
            (b := self._loop1_140())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Compare ( left = a , ops = self . get_comparison_ops ( b ) , comparators = self . get_comparators ( b ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (bitwise_or := self.bitwise_or())
        ):
            return bitwise_or
        self._reset(mark)
        return None

    @memoize
    def compare_op_bitwise_or_pair(self) -> Optional[Any]:
        # compare_op_bitwise_or_pair: eq_bitwise_or | noteq_bitwise_or | lte_bitwise_or | lt_bitwise_or | gte_bitwise_or | gt_bitwise_or | notin_bitwise_or | in_bitwise_or | isnot_bitwise_or | is_bitwise_or
        mark = self._mark()
        if (
            (eq_bitwise_or := self.eq_bitwise_or())
        ):
            return eq_bitwise_or
        self._reset(mark)
        if (
            (noteq_bitwise_or := self.noteq_bitwise_or())
        ):
            return noteq_bitwise_or
        self._reset(mark)
        if (
            (lte_bitwise_or := self.lte_bitwise_or())
        ):
            return lte_bitwise_or
        self._reset(mark)
        if (
            (lt_bitwise_or := self.lt_bitwise_or())
        ):
            return lt_bitwise_or
        self._reset(mark)
        if (
            (gte_bitwise_or := self.gte_bitwise_or())
        ):
            return gte_bitwise_or
        self._reset(mark)
        if (
            (gt_bitwise_or := self.gt_bitwise_or())
        ):
            return gt_bitwise_or
        self._reset(mark)
        if (
            (notin_bitwise_or := self.notin_bitwise_or())
        ):
            return notin_bitwise_or
        self._reset(mark)
        if (
            (in_bitwise_or := self.in_bitwise_or())
        ):
            return in_bitwise_or
        self._reset(mark)
        if (
            (isnot_bitwise_or := self.isnot_bitwise_or())
        ):
            return isnot_bitwise_or
        self._reset(mark)
        if (
            (is_bitwise_or := self.is_bitwise_or())
        ):
            return is_bitwise_or
        self._reset(mark)
        return None

    @memoize
    def eq_bitwise_or(self) -> Optional[Any]:
        # eq_bitwise_or: '==' bitwise_or
        mark = self._mark()
        if (
            (literal := self.expect('=='))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . Eq ( ) , a )
        self._reset(mark)
        return None

    @memoize
    def noteq_bitwise_or(self) -> Optional[tuple]:
        # noteq_bitwise_or: '!=' bitwise_or
        mark = self._mark()
        if (
            (literal := self.expect('!='))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . NotEq ( ) , a )
        self._reset(mark)
        return None

    @memoize
    def lte_bitwise_or(self) -> Optional[Any]:
        # lte_bitwise_or: '<=' bitwise_or
        mark = self._mark()
        if (
            (literal := self.expect('<='))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . LtE ( ) , a )
        self._reset(mark)
        return None

    @memoize
    def lt_bitwise_or(self) -> Optional[Any]:
        # lt_bitwise_or: '<' bitwise_or
        mark = self._mark()
        if (
            (literal := self.expect('<'))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . Lt ( ) , a )
        self._reset(mark)
        return None

    @memoize
    def gte_bitwise_or(self) -> Optional[Any]:
        # gte_bitwise_or: '>=' bitwise_or
        mark = self._mark()
        if (
            (literal := self.expect('>='))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . GtE ( ) , a )
        self._reset(mark)
        return None

    @memoize
    def gt_bitwise_or(self) -> Optional[Any]:
        # gt_bitwise_or: '>' bitwise_or
        mark = self._mark()
        if (
            (literal := self.expect('>'))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . Gt ( ) , a )
        self._reset(mark)
        return None

    @memoize
    def notin_bitwise_or(self) -> Optional[Any]:
        # notin_bitwise_or: 'not' 'in' bitwise_or
        mark = self._mark()
        if (
            (literal := self.expect('not'))
            and
            (literal_1 := self.expect('in'))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . NotIn ( ) , a )
        self._reset(mark)
        return None

    @memoize
    def in_bitwise_or(self) -> Optional[Any]:
        # in_bitwise_or: 'in' bitwise_or
        mark = self._mark()
        if (
            (literal := self.expect('in'))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . In ( ) , a )
        self._reset(mark)
        return None

    @memoize
    def isnot_bitwise_or(self) -> Optional[Any]:
        # isnot_bitwise_or: 'is' 'not' bitwise_or
        mark = self._mark()
        if (
            (literal := self.expect('is'))
            and
            (literal_1 := self.expect('not'))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . IsNot ( ) , a )
        self._reset(mark)
        return None

    @memoize
    def is_bitwise_or(self) -> Optional[Any]:
        # is_bitwise_or: 'is' bitwise_or
        mark = self._mark()
        if (
            (literal := self.expect('is'))
            and
            (a := self.bitwise_or())
        ):
            return ( ast . Is ( ) , a )
        self._reset(mark)
        return None

    @memoize_left_rec
    def bitwise_or(self) -> Optional[Any]:
        # bitwise_or: bitwise_or '|' bitwise_xor | bitwise_xor
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.bitwise_or())
            and
            (literal := self.expect('|'))
            and
            (b := self.bitwise_xor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . BitOr ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (bitwise_xor := self.bitwise_xor())
        ):
            return bitwise_xor
        self._reset(mark)
        return None

    @memoize_left_rec
    def bitwise_xor(self) -> Optional[Any]:
        # bitwise_xor: bitwise_xor '^' bitwise_and | bitwise_and
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.bitwise_xor())
            and
            (literal := self.expect('^'))
            and
            (b := self.bitwise_and())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . BitXor ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (bitwise_and := self.bitwise_and())
        ):
            return bitwise_and
        self._reset(mark)
        return None

    @memoize_left_rec
    def bitwise_and(self) -> Optional[Any]:
        # bitwise_and: bitwise_and '&' shift_expr | shift_expr
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.bitwise_and())
            and
            (literal := self.expect('&'))
            and
            (b := self.shift_expr())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . BitAnd ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (shift_expr := self.shift_expr())
        ):
            return shift_expr
        self._reset(mark)
        return None

    @memoize_left_rec
    def shift_expr(self) -> Optional[Any]:
        # shift_expr: shift_expr '<<' sum | shift_expr '>>' sum | sum
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.shift_expr())
            and
            (literal := self.expect('<<'))
            and
            (b := self.sum())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . LShift ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.shift_expr())
            and
            (literal := self.expect('>>'))
            and
            (b := self.sum())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . RShift ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (sum := self.sum())
        ):
            return sum
        self._reset(mark)
        return None

    @memoize_left_rec
    def sum(self) -> Optional[Any]:
        # sum: sum '+' term | sum '-' term | term
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.sum())
            and
            (literal := self.expect('+'))
            and
            (b := self.term())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . Add ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.sum())
            and
            (literal := self.expect('-'))
            and
            (b := self.term())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . Sub ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (term := self.term())
        ):
            return term
        self._reset(mark)
        return None

    @memoize_left_rec
    def term(self) -> Optional[Any]:
        # term: term '*' factor | term '/' factor | term '//' factor | term '%' factor | term '@' factor | factor
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.term())
            and
            (literal := self.expect('*'))
            and
            (b := self.factor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . Mult ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.term())
            and
            (literal := self.expect('/'))
            and
            (b := self.factor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . Div ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.term())
            and
            (literal := self.expect('//'))
            and
            (b := self.factor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . FloorDiv ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.term())
            and
            (literal := self.expect('%'))
            and
            (b := self.factor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . Mod ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.term())
            and
            (literal := self.expect('@'))
            and
            (b := self.factor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 5 ) , "The '@' operator is" , ast . BinOp ( left = a , op = ast . MatMult ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) )
        self._reset(mark)
        if (
            (factor := self.factor())
        ):
            return factor
        self._reset(mark)
        return None

    @memoize
    def factor(self) -> Optional[Any]:
        # factor: '+' factor | '-' factor | '~' factor | power
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('+'))
            and
            (a := self.factor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . UnaryOp ( op = ast . UAdd ( ) , operand = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('-'))
            and
            (a := self.factor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . UnaryOp ( op = ast . USub ( ) , operand = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('~'))
            and
            (a := self.factor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . UnaryOp ( op = ast . Invert ( ) , operand = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (power := self.power())
        ):
            return power
        self._reset(mark)
        return None

    @memoize
    def power(self) -> Optional[Any]:
        # power: await_primary '**' factor | await_primary
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.await_primary())
            and
            (literal := self.expect('**'))
            and
            (b := self.factor())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . BinOp ( left = a , op = ast . Pow ( ) , right = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (await_primary := self.await_primary())
        ):
            return await_primary
        self._reset(mark)
        return None

    @memoize
    def await_primary(self) -> Optional[Any]:
        # await_primary: 'await' primary | primary
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('await'))
            and
            (a := self.primary())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return self . check_version ( ( 3 , 5 ) , "Await expressions are" , ast . Await ( a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset ) )
        self._reset(mark)
        if (
            (primary := self.primary())
        ):
            return primary
        self._reset(mark)
        return None

    @memoize_left_rec
    def primary(self) -> Optional[Any]:
        # primary: invalid_primary | primary '.' NAME | primary genexp | primary '(' arguments? ')' | primary '[' slices ']' | atom
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (invalid_primary := self.invalid_primary())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (a := self.primary())
            and
            (literal := self.expect('.'))
            and
            (b := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Attribute ( value = a , attr = b . string , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.primary())
            and
            (b := self.genexp())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Call ( func = a , args = [b] , keywords = [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.primary())
            and
            (literal := self.expect('('))
            and
            (b := self.arguments(),)
            and
            (literal_1 := self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Call ( func = a , args = b [0] if b else [] , keywords = b [1] if b else [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , )
        self._reset(mark)
        if (
            (a := self.primary())
            and
            (literal := self.expect('['))
            and
            (b := self.slices())
            and
            (literal_1 := self.expect(']'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Subscript ( value = a , slice = b , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (atom := self.atom())
        ):
            return atom
        self._reset(mark)
        return None

    @memoize
    def slices(self) -> Optional[Any]:
        # slices: slice !',' | ','.slice+ ','?
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.slice())
            and
            self.negative_lookahead(self.expect, ',')
        ):
            return a
        self._reset(mark)
        if (
            (a := self._gather_141())
            and
            (opt := self.expect(','),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Tuple ( elts = a , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def slice(self) -> Optional[Any]:
        # slice: expression? ':' expression? [':' expression?] | named_expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.expression(),)
            and
            (literal := self.expect(':'))
            and
            (b := self.expression(),)
            and
            (c := self._tmp_143(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Slice ( lower = a , upper = b , step = c , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.named_expression())
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def atom(self) -> Optional[Any]:
        # atom: NAME | 'True' | 'False' | 'None' | &STRING strings | NUMBER | &'(' (tuple | group | genexp) | &'[' (list | listcomp) | &'{' (dict | set | dictcomp | setcomp) | '...'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Name ( id = a . string , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('True'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = True , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('False'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = False , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('None'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = None , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            self.positive_lookahead(self.string, )
            and
            (strings := self.strings())
        ):
            return strings
        self._reset(mark)
        if (
            (a := self.number())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = ast . literal_eval ( a . string ) , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            self.positive_lookahead(self.expect, '(')
            and
            (_tmp_144 := self._tmp_144())
        ):
            return _tmp_144
        self._reset(mark)
        if (
            self.positive_lookahead(self.expect, '[')
            and
            (_tmp_145 := self._tmp_145())
        ):
            return _tmp_145
        self._reset(mark)
        if (
            self.positive_lookahead(self.expect, '{')
            and
            (_tmp_146 := self._tmp_146())
        ):
            return _tmp_146
        self._reset(mark)
        if (
            (literal := self.expect('...'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Constant ( value = Ellipsis , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def strings(self) -> Optional[ast . Str]:
        # strings: STRING+
        mark = self._mark()
        if (
            (a := self._loop1_147())
        ):
            return self . generate_ast_for_string ( a )
        self._reset(mark)
        return None

    @memoize
    def list(self) -> Optional[ast . List]:
        # list: '[' star_named_expressions? ']'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('['))
            and
            (a := self.star_named_expressions(),)
            and
            (literal_1 := self.expect(']'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . List ( elts = a or [] , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def listcomp(self) -> Optional[ast . ListComp]:
        # listcomp: '[' named_expression for_if_clauses ']' | invalid_comprehension
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('['))
            and
            (a := self.named_expression())
            and
            (b := self.for_if_clauses())
            and
            (literal_1 := self.expect(']'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . ListComp ( elt = a , generators = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (invalid_comprehension := self.invalid_comprehension())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def tuple(self) -> Optional[ast . Tuple]:
        # tuple: '(' [star_named_expression ',' star_named_expressions?] ')'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('('))
            and
            (a := self._tmp_148(),)
            and
            (literal_1 := self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Tuple ( elts = a or [] , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def group(self) -> Optional[Any]:
        # group: '(' (yield_expr | named_expression) ')' | invalid_group
        mark = self._mark()
        if (
            (literal := self.expect('('))
            and
            (a := self._tmp_149())
            and
            (literal_1 := self.expect(')'))
        ):
            return a
        self._reset(mark)
        if (
            (invalid_group := self.invalid_group())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def genexp(self) -> Optional[ast . GeneratorExp]:
        # genexp: '(' (assignment_expression | expression !':=') for_if_clauses ')' | invalid_comprehension
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('('))
            and
            (a := self._tmp_150())
            and
            (b := self.for_if_clauses())
            and
            (literal_1 := self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . GeneratorExp ( elt = a , generators = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (invalid_comprehension := self.invalid_comprehension())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def set(self) -> Optional[ast . Set]:
        # set: '{' star_named_expressions '}'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('{'))
            and
            (a := self.star_named_expressions())
            and
            (literal_1 := self.expect('}'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Set ( elts = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def setcomp(self) -> Optional[ast . SetComp]:
        # setcomp: '{' named_expression for_if_clauses '}' | invalid_comprehension
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('{'))
            and
            (a := self.named_expression())
            and
            (b := self.for_if_clauses())
            and
            (literal_1 := self.expect('}'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . SetComp ( elt = a , generators = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (invalid_comprehension := self.invalid_comprehension())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def dict(self) -> Optional[ast . Dict]:
        # dict: '{' double_starred_kvpairs? '}' | '{' invalid_double_starred_kvpairs '}'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('{'))
            and
            (a := self.double_starred_kvpairs(),)
            and
            (literal_1 := self.expect('}'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Dict ( keys = [kv [0] for kv in ( a or [] )] , values = [kv [1] for kv in ( a or [] )] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('{'))
            and
            (invalid_double_starred_kvpairs := self.invalid_double_starred_kvpairs())
            and
            (literal_1 := self.expect('}'))
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def dictcomp(self) -> Optional[ast . DictComp]:
        # dictcomp: '{' kvpair for_if_clauses '}' | invalid_dict_comprehension
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('{'))
            and
            (a := self.kvpair())
            and
            (b := self.for_if_clauses())
            and
            (literal_1 := self.expect('}'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . DictComp ( key = a [0] , value = a [1] , generators = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (invalid_dict_comprehension := self.invalid_dict_comprehension())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def double_starred_kvpairs(self) -> Optional[list]:
        # double_starred_kvpairs: ','.double_starred_kvpair+ ','?
        mark = self._mark()
        if (
            (a := self._gather_151())
            and
            (opt := self.expect(','),)
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def double_starred_kvpair(self) -> Optional[Any]:
        # double_starred_kvpair: '**' bitwise_or | kvpair
        mark = self._mark()
        if (
            (literal := self.expect('**'))
            and
            (a := self.bitwise_or())
        ):
            return ( None , a )
        self._reset(mark)
        if (
            (kvpair := self.kvpair())
        ):
            return kvpair
        self._reset(mark)
        return None

    @memoize
    def kvpair(self) -> Optional[tuple]:
        # kvpair: expression ':' expression
        mark = self._mark()
        if (
            (a := self.expression())
            and
            (literal := self.expect(':'))
            and
            (b := self.expression())
        ):
            return ( a , b )
        self._reset(mark)
        return None

    @memoize
    def for_if_clauses(self) -> Optional[List [ast . comprehension]]:
        # for_if_clauses: for_if_clause+
        mark = self._mark()
        if (
            (a := self._loop1_153())
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def for_if_clause(self) -> Optional[ast . comprehension]:
        # for_if_clause: 'async' 'for' star_targets 'in' ~ disjunction (('if' disjunction))* | 'for' star_targets 'in' ~ disjunction (('if' disjunction))* | invalid_for_target
        mark = self._mark()
        cut = False
        if (
            (literal := self.expect('async'))
            and
            (literal_1 := self.expect('for'))
            and
            (a := self.star_targets())
            and
            (literal_2 := self.expect('in'))
            and
            (cut := True)
            and
            (b := self.disjunction())
            and
            (c := self._loop0_154(),)
        ):
            return self . check_version ( ( 3 , 6 ) , "Async comprehensions are" , ast . comprehension ( target = a , iter = b , ifs = c , is_async = 1 ) )
        self._reset(mark)
        if cut: return None
        cut = False
        if (
            (literal := self.expect('for'))
            and
            (a := self.star_targets())
            and
            (literal_1 := self.expect('in'))
            and
            (cut := True)
            and
            (b := self.disjunction())
            and
            (c := self._loop0_155(),)
        ):
            return ast . comprehension ( target = a , iter = b , ifs = c , is_async = 0 )
        self._reset(mark)
        if cut: return None
        if (
            (invalid_for_target := self.invalid_for_target())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def yield_expr(self) -> Optional[Any]:
        # yield_expr: 'yield' 'from' expression | 'yield' star_expressions?
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('yield'))
            and
            (literal_1 := self.expect('from'))
            and
            (a := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . YieldFrom ( value = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('yield'))
            and
            (a := self.star_expressions(),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Yield ( value = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def arguments(self) -> Optional[Tuple [list , list]]:
        # arguments: args ','? &')' | invalid_arguments
        mark = self._mark()
        if (
            (a := self.args())
            and
            (opt := self.expect(','),)
            and
            self.positive_lookahead(self.expect, ')')
        ):
            return a
        self._reset(mark)
        if (
            (invalid_arguments := self.invalid_arguments())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def args(self) -> Optional[Tuple [list , list]]:
        # args: ','.(starred_expression | (assignment_expression | expression !':=') !'=')+ [',' kwargs] | kwargs
        mark = self._mark()
        if (
            (a := self._gather_156())
            and
            (b := self._tmp_158(),)
        ):
            return ( a + ( [e for e in b if isinstance ( e , ast . Starred )] if b else [] ) , ( [e for e in b if not isinstance ( e , ast . Starred )] if b else [] ) )
        self._reset(mark)
        if (
            (a := self.kwargs())
        ):
            return ( [e for e in a if isinstance ( e , ast . Starred )] , [e for e in a if not isinstance ( e , ast . Starred )] )
        self._reset(mark)
        return None

    @memoize
    def kwargs(self) -> Optional[list]:
        # kwargs: ','.kwarg_or_starred+ ',' ','.kwarg_or_double_starred+ | ','.kwarg_or_starred+ | ','.kwarg_or_double_starred+
        mark = self._mark()
        if (
            (a := self._gather_159())
            and
            (literal := self.expect(','))
            and
            (b := self._gather_161())
        ):
            return a + b
        self._reset(mark)
        if (
            (_gather_163 := self._gather_163())
        ):
            return _gather_163
        self._reset(mark)
        if (
            (_gather_165 := self._gather_165())
        ):
            return _gather_165
        self._reset(mark)
        return None

    @memoize
    def starred_expression(self) -> Optional[Any]:
        # starred_expression: '*' expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('*'))
            and
            (a := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Starred ( value = a , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def kwarg_or_starred(self) -> Optional[Any]:
        # kwarg_or_starred: invalid_kwarg | NAME '=' expression | starred_expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (invalid_kwarg := self.invalid_kwarg())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (a := self.name())
            and
            (literal := self.expect('='))
            and
            (b := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . keyword ( arg = a . string , value = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.starred_expression())
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def kwarg_or_double_starred(self) -> Optional[Any]:
        # kwarg_or_double_starred: invalid_kwarg | NAME '=' expression | '**' expression
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (invalid_kwarg := self.invalid_kwarg())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (a := self.name())
            and
            (literal := self.expect('='))
            and
            (b := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . keyword ( arg = a . string , value = b , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('**'))
            and
            (a := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . keyword ( arg = None , value = a , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def star_targets(self) -> Optional[Any]:
        # star_targets: star_target !',' | star_target ((',' star_target))* ','?
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.star_target())
            and
            self.negative_lookahead(self.expect, ',')
        ):
            return a
        self._reset(mark)
        if (
            (a := self.star_target())
            and
            (b := self._loop0_167(),)
            and
            (opt := self.expect(','),)
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Tuple ( elts = [a] + b , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def star_targets_list_seq(self) -> Optional[list]:
        # star_targets_list_seq: ','.star_target+ ','?
        mark = self._mark()
        if (
            (a := self._gather_168())
            and
            (opt := self.expect(','),)
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def star_targets_tuple_seq(self) -> Optional[list]:
        # star_targets_tuple_seq: star_target ((',' star_target))+ ','? | star_target ','
        mark = self._mark()
        if (
            (a := self.star_target())
            and
            (b := self._loop1_170())
            and
            (opt := self.expect(','),)
        ):
            return [a] + b
        self._reset(mark)
        if (
            (a := self.star_target())
            and
            (literal := self.expect(','))
        ):
            return [a]
        self._reset(mark)
        return None

    @memoize
    def star_target(self) -> Optional[Any]:
        # star_target: '*' (!'*' star_target) | target_with_star_atom
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (literal := self.expect('*'))
            and
            (a := self._tmp_171())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Starred ( value = self . set_expr_context ( a , Store ) , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (target_with_star_atom := self.target_with_star_atom())
        ):
            return target_with_star_atom
        self._reset(mark)
        return None

    @memoize
    def target_with_star_atom(self) -> Optional[Any]:
        # target_with_star_atom: t_primary '.' NAME !t_lookahead | t_primary '[' slices ']' !t_lookahead | star_atom
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.t_primary())
            and
            (literal := self.expect('.'))
            and
            (b := self.name())
            and
            self.negative_lookahead(self.t_lookahead, )
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Attribute ( value = a , attr = b . string , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.t_primary())
            and
            (literal := self.expect('['))
            and
            (b := self.slices())
            and
            (literal_1 := self.expect(']'))
            and
            self.negative_lookahead(self.t_lookahead, )
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Subscript ( value = a , slice = b , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (star_atom := self.star_atom())
        ):
            return star_atom
        self._reset(mark)
        return None

    @memoize
    def star_atom(self) -> Optional[Any]:
        # star_atom: NAME | '(' target_with_star_atom ')' | '(' star_targets_tuple_seq? ')' | '[' star_targets_list_seq? ']'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Name ( id = a . string , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('('))
            and
            (a := self.target_with_star_atom())
            and
            (literal_1 := self.expect(')'))
        ):
            return self . set_expr_context ( a , Store )
        self._reset(mark)
        if (
            (literal := self.expect('('))
            and
            (a := self.star_targets_tuple_seq(),)
            and
            (literal_1 := self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Tuple ( elts = a , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('['))
            and
            (a := self.star_targets_list_seq(),)
            and
            (literal_1 := self.expect(']'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . List ( elts = a , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def single_target(self) -> Optional[Any]:
        # single_target: single_subscript_attribute_target | NAME | '(' single_target ')'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (single_subscript_attribute_target := self.single_subscript_attribute_target())
        ):
            return single_subscript_attribute_target
        self._reset(mark)
        if (
            (a := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Name ( id = a . string , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('('))
            and
            (a := self.single_target())
            and
            (literal_1 := self.expect(')'))
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def single_subscript_attribute_target(self) -> Optional[Any]:
        # single_subscript_attribute_target: t_primary '.' NAME !t_lookahead | t_primary '[' slices ']' !t_lookahead
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.t_primary())
            and
            (literal := self.expect('.'))
            and
            (b := self.name())
            and
            self.negative_lookahead(self.t_lookahead, )
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Attribute ( value = a , attr = b . string , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.t_primary())
            and
            (literal := self.expect('['))
            and
            (b := self.slices())
            and
            (literal_1 := self.expect(']'))
            and
            self.negative_lookahead(self.t_lookahead, )
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Subscript ( value = a , slice = b , ctx = Store , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize
    def del_targets(self) -> Optional[Any]:
        # del_targets: ','.del_target+ ','?
        mark = self._mark()
        if (
            (a := self._gather_172())
            and
            (opt := self.expect(','),)
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def del_target(self) -> Optional[Any]:
        # del_target: t_primary '.' NAME !t_lookahead | t_primary '[' slices ']' !t_lookahead | del_t_atom
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.t_primary())
            and
            (literal := self.expect('.'))
            and
            (b := self.name())
            and
            self.negative_lookahead(self.t_lookahead, )
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Attribute ( value = a , attr = b . string , ctx = Del , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.t_primary())
            and
            (literal := self.expect('['))
            and
            (b := self.slices())
            and
            (literal_1 := self.expect(']'))
            and
            self.negative_lookahead(self.t_lookahead, )
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Subscript ( value = a , slice = b , ctx = Del , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (del_t_atom := self.del_t_atom())
        ):
            return del_t_atom
        self._reset(mark)
        return None

    @memoize
    def del_t_atom(self) -> Optional[Any]:
        # del_t_atom: NAME | '(' del_target ')' | '(' del_targets? ')' | '[' del_targets? ']'
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.name())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Name ( id = a . string , ctx = Del , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('('))
            and
            (a := self.del_target())
            and
            (literal_1 := self.expect(')'))
        ):
            return self . set_expr_context ( a , Del )
        self._reset(mark)
        if (
            (literal := self.expect('('))
            and
            (a := self.del_targets(),)
            and
            (literal_1 := self.expect(')'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Tuple ( elts = a , ctx = Del , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (literal := self.expect('['))
            and
            (a := self.del_targets(),)
            and
            (literal_1 := self.expect(']'))
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . List ( elts = a , ctx = Del , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        return None

    @memoize_left_rec
    def t_primary(self) -> Optional[Any]:
        # t_primary: t_primary '.' NAME &t_lookahead | t_primary '[' slices ']' &t_lookahead | t_primary genexp &t_lookahead | t_primary '(' arguments? ')' &t_lookahead | atom &t_lookahead
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.t_primary())
            and
            (literal := self.expect('.'))
            and
            (b := self.name())
            and
            self.positive_lookahead(self.t_lookahead, )
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Attribute ( value = a , attr = b . string , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.t_primary())
            and
            (literal := self.expect('['))
            and
            (b := self.slices())
            and
            (literal_1 := self.expect(']'))
            and
            self.positive_lookahead(self.t_lookahead, )
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Subscript ( value = a , slice = b , ctx = Load , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.t_primary())
            and
            (b := self.genexp())
            and
            self.positive_lookahead(self.t_lookahead, )
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Call ( func = a , args = [b] , keywords = [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (a := self.t_primary())
            and
            (literal := self.expect('('))
            and
            (b := self.arguments(),)
            and
            (literal_1 := self.expect(')'))
            and
            self.positive_lookahead(self.t_lookahead, )
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . Call ( func = a , args = b [0] if b else [] , keywords = b [1] if b else [] , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset , )
        self._reset(mark)
        if (
            (a := self.atom())
            and
            self.positive_lookahead(self.t_lookahead, )
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def t_lookahead(self) -> Optional[Any]:
        # t_lookahead: '(' | '[' | '.'
        mark = self._mark()
        if (
            (literal := self.expect('('))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('['))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('.'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def invalid_arguments(self) -> Optional[Optional [NoReturn]]:
        # invalid_arguments: args ',' '*' | expression for_if_clauses ',' [args | expression for_if_clauses] | NAME '=' expression for_if_clauses | args for_if_clauses | args ',' expression for_if_clauses | args ',' args
        mark = self._mark()
        if (
            (a := self.args())
            and
            (literal := self.expect(','))
            and
            (literal_1 := self.expect('*'))
        ):
            return self . store_syntax_error_known_location ( "iterable argument unpacking follows keyword argument unpacking" , a [1] [- 1] if a [1] else a [0] [- 1] , )
        self._reset(mark)
        if (
            (a := self.expression())
            and
            (b := self.for_if_clauses())
            and
            (literal := self.expect(','))
            and
            (opt := self._tmp_174(),)
        ):
            return self . store_syntax_error_known_range ( "Generator expression must be parenthesized" , a , b [- 1] . target )
        self._reset(mark)
        if (
            (a := self.name())
            and
            (b := self.expect('='))
            and
            (expression := self.expression())
            and
            (for_if_clauses := self.for_if_clauses())
        ):
            return self . store_syntax_error_known_range ( "invalid syntax. Maybe you meant '==' or ':=' instead of '='?" , a , b )
        self._reset(mark)
        if (
            (a := self.args())
            and
            (for_if_clauses := self.for_if_clauses())
        ):
            return self . store_syntax_error_starting_from ( "Generator expression must be parenthesized" , a [1] [- 1] if a [1] else a [0] [- 1] )
        self._reset(mark)
        if (
            (args := self.args())
            and
            (literal := self.expect(','))
            and
            (a := self.expression())
            and
            (b := self.for_if_clauses())
        ):
            return self . store_syntax_error_known_range ( "Generator expression must be parenthesized" , a , b [- 1] . target , )
        self._reset(mark)
        if (
            (a := self.args())
            and
            (literal := self.expect(','))
            and
            (args := self.args())
        ):
            return self . store_syntax_error ( "positional argument follows keyword argument unpacking" if a [1] [- 1] . arg is None else "positional argument follows keyword argument" , )
        self._reset(mark)
        return None

    @memoize
    def invalid_kwarg(self) -> Optional[Optional [NoReturn]]:
        # invalid_kwarg: NAME '=' expression for_if_clauses | !(NAME '=') expression '='
        mark = self._mark()
        if (
            (a := self.name())
            and
            (b := self.expect('='))
            and
            (expression := self.expression())
            and
            (for_if_clauses := self.for_if_clauses())
        ):
            return self . store_syntax_error_known_range ( "invalid syntax. Maybe you meant '==' or ':=' instead of '='?" , a , b )
        self._reset(mark)
        if (
            self.negative_lookahead(self._tmp_175, )
            and
            (a := self.expression())
            and
            (b := self.expect('='))
        ):
            return self . store_syntax_error_known_range ( "expression cannot contain assignment, perhaps you meant \"==\"?" , a , b , )
        self._reset(mark)
        return None

    @memoize
    def expression_without_invalid(self) -> Optional[ast . AST]:
        # expression_without_invalid: disjunction 'if' disjunction 'else' expression | disjunction | lambdef
        mark = self._mark()
        tok = self._tokenizer.peek()
        start_lineno, start_col_offset = tok.start
        if (
            (a := self.disjunction())
            and
            (literal := self.expect('if'))
            and
            (b := self.disjunction())
            and
            (literal_1 := self.expect('else'))
            and
            (c := self.expression())
        ):
            tok = self._tokenizer.get_last_non_whitespace_token()
            end_lineno, end_col_offset = tok.end
            return ast . IfExp ( body = b , test = a , orelse = c , lineno=start_lineno, col_offset=start_col_offset, end_lineno=end_lineno, end_col_offset=end_col_offset )
        self._reset(mark)
        if (
            (disjunction := self.disjunction())
        ):
            return disjunction
        self._reset(mark)
        if (
            (lambdef := self.lambdef())
        ):
            return lambdef
        self._reset(mark)
        return None

    @memoize
    def invalid_expression(self) -> Optional[Optional [NoReturn]]:
        # invalid_expression: !(NAME STRING | SOFT_KEYWORD) disjunction expression_without_invalid
        mark = self._mark()
        if (
            self.negative_lookahead(self._tmp_176, )
            and
            (a := self.disjunction())
            and
            (b := self.expression_without_invalid())
        ):
            return self . store_syntax_error_known_range ( "invalid syntax. Perhaps you forgot a comma?" , a , b )
        self._reset(mark)
        return None

    @memoize
    def invalid_named_expression(self) -> Optional[Optional [NoReturn]]:
        # invalid_named_expression: expression ':=' expression | NAME '=' bitwise_or !('=' | ':=') | !(list | tuple | genexp | 'True' | 'None' | 'False') bitwise_or '=' bitwise_or !('=' | ':=')
        mark = self._mark()
        if (
            (a := self.expression())
            and
            (literal := self.expect(':='))
            and
            (expression := self.expression())
        ):
            return self . store_syntax_error_known_location ( f"cannot use assignment expressions with {self.get_expr_name(a)}" , a )
        self._reset(mark)
        if (
            (a := self.name())
            and
            (literal := self.expect('='))
            and
            (b := self.bitwise_or())
            and
            self.negative_lookahead(self._tmp_177, )
        ):
            return ( None if self . in_recursive_rule else self . store_syntax_error_known_range ( "invalid syntax. Maybe you meant '==' or ':=' instead of '='?" , a , b ) )
        self._reset(mark)
        if (
            self.negative_lookahead(self._tmp_178, )
            and
            (a := self.bitwise_or())
            and
            (b := self.expect('='))
            and
            (bitwise_or := self.bitwise_or())
            and
            self.negative_lookahead(self._tmp_179, )
        ):
            return ( None if self . in_recursive_rule else self . store_syntax_error_known_range ( f"cannot assign to {self.get_expr_name(a)} here. Maybe you meant '==' instead of '='?" , a , b ) )
        self._reset(mark)
        return None

    @memoize
    def invalid_assignment(self) -> Optional[Optional [NoReturn]]:
        # invalid_assignment: invalid_ann_assign_target ':' expression | star_named_expression ',' star_named_expressions* ':' expression | expression ':' expression | ((star_targets '='))* star_expressions '=' | ((star_targets '='))* yield_expr '=' | star_expressions augassign (yield_expr | star_expressions)
        mark = self._mark()
        if (
            (a := self.invalid_ann_assign_target())
            and
            (literal := self.expect(':'))
            and
            (expression := self.expression())
        ):
            return self . store_syntax_error_known_location ( f"only single target (not {self.get_expr_name(a)}) can be annotated" , a )
        self._reset(mark)
        if (
            (a := self.star_named_expression())
            and
            (literal := self.expect(','))
            and
            (_loop0_180 := self._loop0_180(),)
            and
            (literal_1 := self.expect(':'))
            and
            (expression := self.expression())
        ):
            return self . store_syntax_error_known_location ( "only single target (not tuple) can be annotated" , a )
        self._reset(mark)
        if (
            (a := self.expression())
            and
            (literal := self.expect(':'))
            and
            (expression := self.expression())
        ):
            return self . store_syntax_error_known_location ( "illegal target for annotation" , a )
        self._reset(mark)
        if (
            (_loop0_181 := self._loop0_181(),)
            and
            (a := self.star_expressions())
            and
            (literal := self.expect('='))
        ):
            return self . store_syntax_error_known_location ( f"cannot assign to {self.get_expr_name(a)}" , a )
        self._reset(mark)
        if (
            (_loop0_182 := self._loop0_182(),)
            and
            (a := self.yield_expr())
            and
            (literal := self.expect('='))
        ):
            return self . store_syntax_error_known_location ( "assignment to yield expression not possible" , a )
        self._reset(mark)
        if (
            (a := self.star_expressions())
            and
            (augassign := self.augassign())
            and
            (_tmp_183 := self._tmp_183())
        ):
            return self . store_syntax_error_known_location ( f"{self.get_expr_name(a)} is an illegal expression for augmented assignment" , a )
        self._reset(mark)
        return None

    @memoize
    def invalid_ann_assign_target(self) -> Optional[Optional [ast . AST]]:
        # invalid_ann_assign_target: list | tuple | '(' invalid_ann_assign_target ')'
        mark = self._mark()
        if (
            (list := self.list())
        ):
            return list
        self._reset(mark)
        if (
            (tuple := self.tuple())
        ):
            return tuple
        self._reset(mark)
        if (
            (literal := self.expect('('))
            and
            (a := self.invalid_ann_assign_target())
            and
            (literal_1 := self.expect(')'))
        ):
            return a
        self._reset(mark)
        return None

    @memoize
    def invalid_del_stmt(self) -> Optional[Optional [NoReturn]]:
        # invalid_del_stmt: 'del' star_expressions
        mark = self._mark()
        if (
            (literal := self.expect('del'))
            and
            (a := self.star_expressions())
        ):
            return self . raise_syntax_error_known_location ( f"cannot delete {self.get_expr_name(a)}" , a )
        self._reset(mark)
        return None

    @memoize
    def invalid_block(self) -> Optional[Optional [NoReturn]]:
        # invalid_block: NEWLINE !INDENT
        mark = self._mark()
        if (
            (_newline := self.expect('NEWLINE'))
            and
            self.negative_lookahead(self.expect, 'INDENT')
        ):
            return self . raise_indentation_error ( "expected an indented block" )
        self._reset(mark)
        return None

    @logger
    def invalid_primary(self) -> Optional[Optional [NoReturn]]:
        # invalid_primary: primary '{'
        mark = self._mark()
        if (
            (primary := self.primary())
            and
            (a := self.expect('{'))
        ):
            return self . raise_syntax_error_known_location ( "invalid syntax" , a )
        self._reset(mark)
        return None

    @memoize
    def invalid_comprehension(self) -> Optional[Optional [NoReturn]]:
        # invalid_comprehension: ('[' | '(' | '{') starred_expression for_if_clauses | ('[' | '{') star_named_expression ',' star_named_expressions for_if_clauses | ('[' | '{') star_named_expression ',' for_if_clauses
        mark = self._mark()
        if (
            (_tmp_184 := self._tmp_184())
            and
            (a := self.starred_expression())
            and
            (for_if_clauses := self.for_if_clauses())
        ):
            return self . raise_syntax_error_known_location ( "iterable unpacking cannot be used in comprehension" , a )
        self._reset(mark)
        if (
            (_tmp_185 := self._tmp_185())
            and
            (a := self.star_named_expression())
            and
            (literal := self.expect(','))
            and
            (b := self.star_named_expressions())
            and
            (for_if_clauses := self.for_if_clauses())
        ):
            return self . raise_syntax_error_known_range ( "did you forget parentheses around the comprehension target?" , a , b [- 1] )
        self._reset(mark)
        if (
            (_tmp_186 := self._tmp_186())
            and
            (a := self.star_named_expression())
            and
            (b := self.expect(','))
            and
            (for_if_clauses := self.for_if_clauses())
        ):
            return self . raise_syntax_error_known_range ( "did you forget parentheses around the comprehension target?" , a , b )
        self._reset(mark)
        return None

    @memoize
    def invalid_dict_comprehension(self) -> Optional[Optional [NoReturn]]:
        # invalid_dict_comprehension: '{' '**' bitwise_or for_if_clauses '}'
        mark = self._mark()
        if (
            (literal := self.expect('{'))
            and
            (a := self.expect('**'))
            and
            (bitwise_or := self.bitwise_or())
            and
            (for_if_clauses := self.for_if_clauses())
            and
            (literal_1 := self.expect('}'))
        ):
            return self . raise_syntax_error_known_location ( "dict unpacking cannot be used in dict comprehension" , a )
        self._reset(mark)
        return None

    @memoize
    def invalid_parameters(self) -> Optional[Optional [NoReturn]]:
        # invalid_parameters: param_no_default* invalid_parameters_helper param_no_default
        mark = self._mark()
        if (
            (_loop0_187 := self._loop0_187(),)
            and
            (invalid_parameters_helper := self.invalid_parameters_helper())
            and
            (a := self.param_no_default())
        ):
            return self . raise_syntax_error_known_location ( "non-default argument follows default argument" , a )
        self._reset(mark)
        return None

    @memoize
    def invalid_parameters_helper(self) -> Optional[Any]:
        # invalid_parameters_helper: slash_with_default | param_with_default+
        mark = self._mark()
        if (
            (a := self.slash_with_default())
        ):
            return [a]
        self._reset(mark)
        if (
            (_loop1_188 := self._loop1_188())
        ):
            return _loop1_188
        self._reset(mark)
        return None

    @memoize
    def invalid_lambda_parameters(self) -> Optional[Optional [NoReturn]]:
        # invalid_lambda_parameters: lambda_param_no_default* invalid_lambda_parameters_helper lambda_param_no_default
        mark = self._mark()
        if (
            (_loop0_189 := self._loop0_189(),)
            and
            (invalid_lambda_parameters_helper := self.invalid_lambda_parameters_helper())
            and
            (a := self.lambda_param_no_default())
        ):
            return self . raise_syntax_error_known_location ( "non-default argument follows default argument" , a )
        self._reset(mark)
        return None

    @memoize
    def invalid_lambda_parameters_helper(self) -> Optional[Optional [NoReturn]]:
        # invalid_lambda_parameters_helper: lambda_slash_with_default | lambda_param_with_default+
        mark = self._mark()
        if (
            (a := self.lambda_slash_with_default())
        ):
            return [a]
        self._reset(mark)
        if (
            (_loop1_190 := self._loop1_190())
        ):
            return _loop1_190
        self._reset(mark)
        return None

    @memoize
    def invalid_star_etc(self) -> Optional[Optional [NoReturn]]:
        # invalid_star_etc: '*' (')' | ',' (')' | '**')) | '*' ',' TYPE_COMMENT
        mark = self._mark()
        if (
            (a := self.expect('*'))
            and
            (_tmp_191 := self._tmp_191())
        ):
            return self . store_syntax_error_known_location ( "named arguments must follow bare *" , a )
        self._reset(mark)
        if (
            (literal := self.expect('*'))
            and
            (literal_1 := self.expect(','))
            and
            (type_comment := self.type_comment())
        ):
            return self . store_syntax_error ( "bare * has associated type comment" )
        self._reset(mark)
        return None

    @memoize
    def invalid_lambda_star_etc(self) -> Optional[Optional [NoReturn]]:
        # invalid_lambda_star_etc: '*' (':' | ',' (':' | '**'))
        mark = self._mark()
        if (
            (literal := self.expect('*'))
            and
            (_tmp_192 := self._tmp_192())
        ):
            return self . raise_syntax_error ( "named arguments must follow bare *" )
        self._reset(mark)
        return None

    @memoize
    def invalid_double_type_comments(self) -> Optional[Optional [NoReturn]]:
        # invalid_double_type_comments: TYPE_COMMENT NEWLINE TYPE_COMMENT NEWLINE INDENT
        mark = self._mark()
        if (
            (type_comment := self.type_comment())
            and
            (_newline := self.expect('NEWLINE'))
            and
            (type_comment_1 := self.type_comment())
            and
            (_newline_1 := self.expect('NEWLINE'))
            and
            (_indent := self.expect('INDENT'))
        ):
            return self . raise_syntax_error ( "Cannot have two type comments on def" )
        self._reset(mark)
        return None

    @memoize
    def invalid_with_item(self) -> Optional[Optional [NoReturn]]:
        # invalid_with_item: expression 'as' expression &(',' | ')' | ':')
        mark = self._mark()
        if (
            (expression := self.expression())
            and
            (literal := self.expect('as'))
            and
            (a := self.expression())
            and
            self.positive_lookahead(self._tmp_193, )
        ):
            return self . raise_syntax_error_known_location ( f"cannot assign to {self.get_expr_name(a)}" , a )
        self._reset(mark)
        return None

    @memoize
    def invalid_for_target(self) -> Optional[Optional [NoReturn]]:
        # invalid_for_target: 'async'? 'for' star_expressions
        mark = self._mark()
        if (
            (opt := self.expect('async'),)
            and
            (literal := self.expect('for'))
            and
            (a := self.star_expressions())
        ):
            return self . raise_syntax_error_known_location ( f"cannot assign to {self.get_expr_name(a)}" , a )
        self._reset(mark)
        return None

    @memoize
    def invalid_group(self) -> Optional[Optional [NoReturn]]:
        # invalid_group: '(' starred_expression ')' | '(' '**' expression ')'
        mark = self._mark()
        if (
            (literal := self.expect('('))
            and
            (a := self.starred_expression())
            and
            (literal_1 := self.expect(')'))
        ):
            return self . raise_syntax_error_known_location ( "cannot use starred expression here" , a )
        self._reset(mark)
        if (
            (literal := self.expect('('))
            and
            (a := self.expect('**'))
            and
            (expression := self.expression())
            and
            (literal_1 := self.expect(')'))
        ):
            return self . raise_syntax_error_known_location ( "cannot use double starred expression here" , a )
        self._reset(mark)
        return None

    @memoize
    def invalid_import_from_targets(self) -> Optional[Optional [NoReturn]]:
        # invalid_import_from_targets: import_from_as_names ','
        mark = self._mark()
        if (
            (import_from_as_names := self.import_from_as_names())
            and
            (literal := self.expect(','))
        ):
            return self . raise_syntax_error ( "trailing comma not allowed without surrounding parentheses" )
        self._reset(mark)
        return None

    @memoize
    def invalid_with_stmt(self) -> Optional[None]:
        # invalid_with_stmt: 'async'? 'with' ','.(expression ['as' star_target])+ &&':' | 'async'? 'with' '(' ','.(expressions ['as' star_target])+ ','? ')' &&':'
        mark = self._mark()
        if (
            (opt := self.expect('async'),)
            and
            (literal := self.expect('with'))
            and
            (_gather_194 := self._gather_194())
            and
            (forced := self.expect_forced(self.expect(':'), "':'"))
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (opt := self.expect('async'),)
            and
            (literal := self.expect('with'))
            and
            (literal_1 := self.expect('('))
            and
            (_gather_196 := self._gather_196())
            and
            (opt_1 := self.expect(','),)
            and
            (literal_2 := self.expect(')'))
            and
            (forced := self.expect_forced(self.expect(':'), "':'"))
        ):
            return None  # pragma: no cover
        self._reset(mark)
        return None

    @memoize
    def invalid_with_stmt_indent(self) -> Optional[Optional [NoReturn]]:
        # invalid_with_stmt_indent: 'async'? 'with' ','.(expression ['as' star_target])+ ':' NEWLINE !INDENT | 'async'? 'with' '(' ','.(expressions ['as' star_target])+ ','? ')' ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (opt := self.expect('async'),)
            and
            (a := self.expect('with'))
            and
            (_gather_198 := self._gather_198())
            and
            (literal := self.expect(':'))
            and
            (_newline := self.expect('NEWLINE'))
            and
            self.negative_lookahead(self.expect, 'INDENT')
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'with' statement on line {a.start[0]}" )
        self._reset(mark)
        if (
            (opt := self.expect('async'),)
            and
            (a := self.expect('with'))
            and
            (literal := self.expect('('))
            and
            (_gather_200 := self._gather_200())
            and
            (opt_1 := self.expect(','),)
            and
            (literal_1 := self.expect(')'))
            and
            (literal_2 := self.expect(':'))
            and
            (_newline := self.expect('NEWLINE'))
            and
            self.negative_lookahead(self.expect, 'INDENT')
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'with' statement on line {a.start[0]}" )
        self._reset(mark)
        return None

    @memoize
    def invalid_try_stmt(self) -> Optional[Optional [NoReturn]]:
        # invalid_try_stmt: 'try' ':' NEWLINE !INDENT | 'try' ':' block !('except' | 'finally')
        mark = self._mark()
        if (
            (a := self.expect('try'))
            and
            (literal := self.expect(':'))
            and
            (_newline := self.expect('NEWLINE'))
            and
            self.negative_lookahead(self.expect, 'INDENT')
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'try' statement on line {a.start[0]}" , )
        self._reset(mark)
        if (
            (literal := self.expect('try'))
            and
            (literal_1 := self.expect(':'))
            and
            (block := self.block())
            and
            self.negative_lookahead(self._tmp_202, )
        ):
            return self . raise_syntax_error ( "expected 'except' or 'finally' block" )
        self._reset(mark)
        return None

    @memoize
    def invalid_except_stmt(self) -> Optional[None]:
        # invalid_except_stmt: 'except' expression ',' expressions ['as' NAME] ':' | 'except' expression ['as' NAME] NEWLINE | 'except' NEWLINE
        mark = self._mark()
        if (
            (literal := self.expect('except'))
            and
            (a := self.expression())
            and
            (literal_1 := self.expect(','))
            and
            (expressions := self.expressions())
            and
            (opt := self._tmp_203(),)
            and
            (literal_2 := self.expect(':'))
        ):
            return self . raise_syntax_error_starting_from ( "exception group must be parenthesized" , a )
        self._reset(mark)
        if (
            (a := self.expect('except'))
            and
            (expression := self.expression())
            and
            (opt := self._tmp_204(),)
            and
            (_newline := self.expect('NEWLINE'))
        ):
            return self . store_syntax_error ( "expected ':'" )
        self._reset(mark)
        if (
            (a := self.expect('except'))
            and
            (_newline := self.expect('NEWLINE'))
        ):
            return self . store_syntax_error ( "expected ':'" )
        self._reset(mark)
        return None

    @memoize
    def invalid_finally_stmt(self) -> Optional[Optional [NoReturn]]:
        # invalid_finally_stmt: 'finally' ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (a := self.expect('finally'))
            and
            (literal := self.expect(':'))
            and
            (_newline := self.expect('NEWLINE'))
            and
            self.negative_lookahead(self.expect, 'INDENT')
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'finally' statement on line {a.start[0]}" )
        self._reset(mark)
        return None

    @memoize
    def invalid_except_stmt_indent(self) -> Optional[Optional [NoReturn]]:
        # invalid_except_stmt_indent: 'except' expression ['as' NAME] ':' NEWLINE !INDENT | 'except' ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (a := self.expect('except'))
            and
            (expression := self.expression())
            and
            (opt := self._tmp_205(),)
            and
            (literal := self.expect(':'))
            and
            (_newline := self.expect('NEWLINE'))
            and
            self.negative_lookahead(self.expect, 'INDENT')
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'except' statement on line {a.start[0]}" )
        self._reset(mark)
        if (
            (a := self.expect('except'))
            and
            (literal := self.expect(':'))
            and
            (_newline := self.expect('NEWLINE'))
            and
            self.negative_lookahead(self.expect, 'INDENT')
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'except' statement on line {a.start[0]}" )
        self._reset(mark)
        return None

    @memoize
    def invalid_match_stmt(self) -> Optional[Optional [NoReturn]]:
        # invalid_match_stmt: "match" subject_expr !':' | "match" subject_expr ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (literal := self.expect("match"))
            and
            (subject_expr := self.subject_expr())
            and
            self.negative_lookahead(self.expect, ':')
        ):
            return self . check_version ( ( 3 , 10 ) , "Pattern matching is" , self . raise_syntax_error ( "expected ':'" ) )
        self._reset(mark)
        if (
            (a := self.expect("match"))
            and
            (subject := self.subject_expr())
            and
            (literal := self.expect(':'))
            and
            (_newline := self.expect('NEWLINE'))
            and
            self.negative_lookahead(self.expect, 'INDENT')
        ):
            return self . check_version ( ( 3 , 10 ) , "Pattern matching is" , self . raise_indentation_error ( f"expected an indented block after 'match' statement on line {a.start[0]}" ) )
        self._reset(mark)
        return None

    @memoize
    def invalid_case_block(self) -> Optional[Optional [NoReturn]]:
        # invalid_case_block: "case" patterns guard? !':' | "case" patterns guard? ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (literal := self.expect("case"))
            and
            (patterns := self.patterns())
            and
            (opt := self.guard(),)
            and
            self.negative_lookahead(self.expect, ':')
        ):
            return self . store_syntax_error ( "expected ':'" )
        self._reset(mark)
        if (
            (a := self.expect("case"))
            and
            (patterns := self.patterns())
            and
            (opt := self.guard(),)
            and
            (literal := self.expect(':'))
            and
            (_newline := self.expect('NEWLINE'))
            and
            self.negative_lookahead(self.expect, 'INDENT')
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'case' statement on line {a.start[0]}" )
        self._reset(mark)
        return None

    @memoize
    def invalid_as_pattern(self) -> Optional[None]:
        # invalid_as_pattern: or_pattern 'as' "_" | or_pattern 'as' !NAME expression
        mark = self._mark()
        if (
            (or_pattern := self.or_pattern())
            and
            (literal := self.expect('as'))
            and
            (a := self.expect("_"))
        ):
            return self . raise_syntax_error_known_location ( "cannot use '_' as a target" , a )
        self._reset(mark)
        if (
            (or_pattern := self.or_pattern())
            and
            (literal := self.expect('as'))
            and
            self.negative_lookahead(self.name, )
            and
            (a := self.expression())
        ):
            return self . raise_syntax_error_known_location ( "invalid pattern target" , a )
        self._reset(mark)
        return None

    @memoize
    def invalid_if_stmt(self) -> Optional[Optional [NoReturn]]:
        # invalid_if_stmt: 'if' named_expression NEWLINE | 'if' named_expression ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (literal := self.expect('if'))
            and
            (named_expression := self.named_expression())
            and
            (_newline := self.expect('NEWLINE'))
        ):
            return self . raise_syntax_error ( "expected ':'" )
        self._reset(mark)
        if (
            (a := self.expect('if'))
            and
            (a_1 := self.named_expression())
            and
            (literal := self.expect(':'))
            and
            (_newline := self.expect('NEWLINE'))
            and
            self.negative_lookahead(self.expect, 'INDENT')
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'if' statement on line {a.start[0]}" )
        self._reset(mark)
        return None

    @memoize
    def invalid_elif_stmt(self) -> Optional[Optional [NoReturn]]:
        # invalid_elif_stmt: 'elif' named_expression NEWLINE | 'elif' named_expression ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (literal := self.expect('elif'))
            and
            (named_expression := self.named_expression())
            and
            (_newline := self.expect('NEWLINE'))
        ):
            return self . raise_syntax_error ( "expected ':'" )
        self._reset(mark)
        if (
            (a := self.expect('elif'))
            and
            (named_expression := self.named_expression())
            and
            (literal := self.expect(':'))
            and
            (_newline := self.expect('NEWLINE'))
            and
            self.negative_lookahead(self.expect, 'INDENT')
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'elif' statement on line {a.start[0]}" )
        self._reset(mark)
        return None

    @memoize
    def invalid_else_stmt(self) -> Optional[Optional [NoReturn]]:
        # invalid_else_stmt: 'else' ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (a := self.expect('else'))
            and
            (literal := self.expect(':'))
            and
            (_newline := self.expect('NEWLINE'))
            and
            self.negative_lookahead(self.expect, 'INDENT')
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'else' statement on line {a.start[0]}" )
        self._reset(mark)
        return None

    @memoize
    def invalid_while_stmt(self) -> Optional[Optional [NoReturn]]:
        # invalid_while_stmt: 'while' named_expression NEWLINE | 'while' named_expression ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (literal := self.expect('while'))
            and
            (named_expression := self.named_expression())
            and
            (_newline := self.expect('NEWLINE'))
        ):
            return self . store_syntax_error ( "expected ':'" )
        self._reset(mark)
        if (
            (a := self.expect('while'))
            and
            (named_expression := self.named_expression())
            and
            (literal := self.expect(':'))
            and
            (_newline := self.expect('NEWLINE'))
            and
            self.negative_lookahead(self.expect, 'INDENT')
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'while' statement on line {a.start[0]}" )
        self._reset(mark)
        return None

    @memoize
    def invalid_for_stmt(self) -> Optional[Optional [NoReturn]]:
        # invalid_for_stmt: 'async'? 'for' star_targets 'in' star_expressions ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (opt := self.expect('async'),)
            and
            (a := self.expect('for'))
            and
            (star_targets := self.star_targets())
            and
            (literal := self.expect('in'))
            and
            (star_expressions := self.star_expressions())
            and
            (literal_1 := self.expect(':'))
            and
            (_newline := self.expect('NEWLINE'))
            and
            self.negative_lookahead(self.expect, 'INDENT')
        ):
            return self . raise_indentation_error ( f"expected an indented block after 'for' statement on line {a.start[0]}" )
        self._reset(mark)
        return None

    @memoize
    def invalid_def_raw(self) -> Optional[Optional [NoReturn]]:
        # invalid_def_raw: 'async'? 'def' NAME '(' params? ')' ['->' expression] ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (opt := self.expect('async'),)
            and
            (a := self.expect('def'))
            and
            (name := self.name())
            and
            (literal := self.expect('('))
            and
            (opt_1 := self.params(),)
            and
            (literal_1 := self.expect(')'))
            and
            (opt_2 := self._tmp_206(),)
            and
            (literal_2 := self.expect(':'))
            and
            (_newline := self.expect('NEWLINE'))
            and
            self.negative_lookahead(self.expect, 'INDENT')
        ):
            return self . raise_indentation_error ( f"expected an indented block after function definition on line {a.start[0]}" )
        self._reset(mark)
        return None

    @memoize
    def invalid_class_def_raw(self) -> Optional[Optional [NoReturn]]:
        # invalid_class_def_raw: 'class' NAME ['(' arguments? ')'] ':' NEWLINE !INDENT
        mark = self._mark()
        if (
            (a := self.expect('class'))
            and
            (name := self.name())
            and
            (opt := self._tmp_207(),)
            and
            (literal := self.expect(':'))
            and
            (_newline := self.expect('NEWLINE'))
            and
            self.negative_lookahead(self.expect, 'INDENT')
        ):
            return self . raise_indentation_error ( f"expected an indented block after class definition on line {a.start[0]}" )
        self._reset(mark)
        return None

    @memoize
    def invalid_double_starred_kvpairs(self) -> Optional[None]:
        # invalid_double_starred_kvpairs: ','.double_starred_kvpair+ ',' invalid_kvpair | expression ':' '*' bitwise_or | expression ':' &('}' | ',')
        mark = self._mark()
        if (
            (_gather_208 := self._gather_208())
            and
            (literal := self.expect(','))
            and
            (invalid_kvpair := self.invalid_kvpair())
        ):
            return None  # pragma: no cover
        self._reset(mark)
        if (
            (expression := self.expression())
            and
            (literal := self.expect(':'))
            and
            (a := self.expect('*'))
            and
            (bitwise_or := self.bitwise_or())
        ):
            return self . store_syntax_error_starting_from ( "cannot use a starred expression in a dictionary value" , a )
        self._reset(mark)
        if (
            (expression := self.expression())
            and
            (a := self.expect(':'))
            and
            self.positive_lookahead(self._tmp_210, )
        ):
            return self . store_syntax_error_known_location ( "expression expected after dictionary key and ':'" , a )
        self._reset(mark)
        return None

    @memoize
    def invalid_kvpair(self) -> Optional[None]:
        # invalid_kvpair: expression !(':') | expression ':' '*' bitwise_or | expression ':'
        mark = self._mark()
        if (
            (a := self.expression())
            and
            self.negative_lookahead(self.expect, ':')
        ):
            return self . _store_syntax_error ( "':' expected after dictionary key" , ( a . lineno , a . col_offset - 1 ) , ( a . end_lineno , a . end_col_offset , - 1 ) )
        self._reset(mark)
        if (
            (expression := self.expression())
            and
            (literal := self.expect(':'))
            and
            (a := self.expect('*'))
            and
            (bitwise_or := self.bitwise_or())
        ):
            return self . store_syntax_error_starting_from ( "cannot use a starred expression in a dictionary value" , a )
        self._reset(mark)
        if (
            (expression := self.expression())
            and
            (a := self.expect(':'))
        ):
            return self . store_syntax_error_known_location ( "expression expected after dictionary key and ':'" , a )
        self._reset(mark)
        return None

    @memoize
    def _loop0_1(self) -> Optional[Any]:
        # _loop0_1: enaml_item
        mark = self._mark()
        children = []
        while (
            (enaml_item := self.enaml_item())
        ):
            children.append(enaml_item)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_2(self) -> Optional[Any]:
        # _loop0_2: pragma
        mark = self._mark()
        children = []
        while (
            (pragma := self.pragma())
        ):
            children.append(pragma)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _tmp_3(self) -> Optional[Any]:
        # _tmp_3: ':' NAME
        mark = self._mark()
        if (
            (literal := self.expect(':'))
            and
            (z := self.name())
        ):
            return z
        self._reset(mark)
        return None

    @memoize
    def _loop1_4(self) -> Optional[Any]:
        # _loop1_4: enamldef_item
        mark = self._mark()
        children = []
        while (
            (enamldef_item := self.enamldef_item())
        ):
            children.append(enamldef_item)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_5(self) -> Optional[Any]:
        # _loop1_5: enamldef_item
        mark = self._mark()
        children = []
        while (
            (enamldef_item := self.enamldef_item())
        ):
            children.append(enamldef_item)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_6(self) -> Optional[Any]:
        # _loop1_6: pragma
        mark = self._mark()
        children = []
        while (
            (pragma := self.pragma())
        ):
            children.append(pragma)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _tmp_7(self) -> Optional[Any]:
        # _tmp_7: '(' ','.pragma_arg+ ')'
        mark = self._mark()
        if (
            (literal := self.expect('('))
            and
            (b := self._gather_211())
            and
            (literal_1 := self.expect(')'))
        ):
            return b
        self._reset(mark)
        return None

    @memoize
    def _tmp_8(self) -> Optional[Any]:
        # _tmp_8: ':' '.'.NAME+
        mark = self._mark()
        if (
            (literal := self.expect(':'))
            and
            (c := self._gather_213())
        ):
            return c
        self._reset(mark)
        return None

    @memoize
    def _tmp_9(self) -> Optional[Any]:
        # _tmp_9: ':' dec_primary
        mark = self._mark()
        if (
            (literal := self.expect(':'))
            and
            (c := self.dec_primary())
        ):
            return c
        self._reset(mark)
        return None

    @memoize
    def _tmp_10(self) -> Optional[Any]:
        # _tmp_10: "attr" | "event"
        mark = self._mark()
        if (
            (literal := self.expect("attr"))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect("event"))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_11(self) -> Optional[Any]:
        # _tmp_11: ':' dec_primary
        mark = self._mark()
        if (
            (literal := self.expect(':'))
            and
            (d := self.dec_primary())
        ):
            return d
        self._reset(mark)
        return None

    @memoize
    def _tmp_12(self) -> Optional[Any]:
        # _tmp_12: "attr" | "event"
        mark = self._mark()
        if (
            (literal := self.expect("attr"))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect("event"))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_13(self) -> Optional[Any]:
        # _tmp_13: ':' dec_primary
        mark = self._mark()
        if (
            (literal := self.expect(':'))
            and
            (d := self.dec_primary())
        ):
            return d
        self._reset(mark)
        return None

    @memoize
    def _tmp_14(self) -> Optional[Any]:
        # _tmp_14: ':' NAME
        mark = self._mark()
        if (
            (literal := self.expect(':'))
            and
            (z := self.name())
        ):
            return z
        self._reset(mark)
        return None

    @memoize
    def _loop1_15(self) -> Optional[Any]:
        # _loop1_15: child_def_item
        mark = self._mark()
        children = []
        while (
            (child_def_item := self.child_def_item())
        ):
            children.append(child_def_item)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_17(self) -> Optional[Any]:
        # _loop0_17: '.' NAME
        mark = self._mark()
        children = []
        while (
            (literal := self.expect('.'))
            and
            (elem := self.name())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_16(self) -> Optional[Any]:
        # _gather_16: NAME _loop0_17
        mark = self._mark()
        if (
            (elem := self.name())
            is not None
            and
            (seq := self._loop0_17())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _tmp_18(self) -> Optional[Any]:
        # _tmp_18: '=' | '<<'
        mark = self._mark()
        if (
            (literal := self.expect('='))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('<<'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_19(self) -> Optional[Any]:
        # _tmp_19: '>>' | ':='
        mark = self._mark()
        if (
            (literal := self.expect('>>'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect(':='))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_20(self) -> Optional[Any]:
        # _tmp_20: '->' expression
        mark = self._mark()
        if (
            (literal := self.expect('->'))
            and
            (z := self.expression())
        ):
            return z
        self._reset(mark)
        return None

    @memoize
    def _tmp_21(self) -> Optional[Any]:
        # _tmp_21: '->' expression
        mark = self._mark()
        if (
            (literal := self.expect('->'))
            and
            (z := self.expression())
        ):
            return z
        self._reset(mark)
        return None

    @memoize
    def _loop1_22(self) -> Optional[Any]:
        # _loop1_22: template_item
        mark = self._mark()
        children = []
        while (
            (template_item := self.template_item())
        ):
            children.append(template_item)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_23(self) -> Optional[Any]:
        # _loop1_23: template_item
        mark = self._mark()
        children = []
        while (
            (template_item := self.template_item())
        ):
            children.append(template_item)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_25(self) -> Optional[Any]:
        # _loop0_25: ',' template_param
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.template_param())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_24(self) -> Optional[Any]:
        # _gather_24: template_param _loop0_25
        mark = self._mark()
        if (
            (elem := self.template_param())
            is not None
            and
            (seq := self._loop0_25())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _tmp_26(self) -> Optional[Any]:
        # _tmp_26: ',' '*' NAME
        mark = self._mark()
        if (
            (literal := self.expect(','))
            and
            (literal_1 := self.expect('*'))
            and
            (c := self.name())
        ):
            return c
        self._reset(mark)
        return None

    @memoize
    def _tmp_27(self) -> Optional[Any]:
        # _tmp_27: ':' template_ids
        mark = self._mark()
        if (
            (literal := self.expect(':'))
            and
            (z := self.template_ids())
        ):
            return z
        self._reset(mark)
        return None

    @memoize
    def _loop0_29(self) -> Optional[Any]:
        # _loop0_29: ',' template_argument
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.template_argument())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_28(self) -> Optional[Any]:
        # _gather_28: template_argument _loop0_29
        mark = self._mark()
        if (
            (elem := self.template_argument())
            is not None
            and
            (seq := self._loop0_29())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _tmp_30(self) -> Optional[Any]:
        # _tmp_30: ',' '*' NAME
        mark = self._mark()
        if (
            (literal := self.expect(','))
            and
            (literal_1 := self.expect('*'))
            and
            (z := self.name())
        ):
            return z
        self._reset(mark)
        return None

    @memoize
    def _loop0_32(self) -> Optional[Any]:
        # _loop0_32: ',' NAME
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.name())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_31(self) -> Optional[Any]:
        # _gather_31: NAME _loop0_32
        mark = self._mark()
        if (
            (elem := self.name())
            is not None
            and
            (seq := self._loop0_32())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _tmp_33(self) -> Optional[Any]:
        # _tmp_33: ',' '*' NAME
        mark = self._mark()
        if (
            (literal := self.expect(','))
            and
            (literal_1 := self.expect('*'))
            and
            (z := self.name())
        ):
            return z
        self._reset(mark)
        return None

    @memoize
    def _loop1_34(self) -> Optional[Any]:
        # _loop1_34: template_inst_item
        mark = self._mark()
        children = []
        while (
            (template_inst_item := self.template_inst_item())
        ):
            children.append(template_inst_item)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_36(self) -> Optional[Any]:
        # _loop0_36: ',' expression
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.expression())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_35(self) -> Optional[Any]:
        # _gather_35: expression _loop0_36
        mark = self._mark()
        if (
            (elem := self.expression())
            is not None
            and
            (seq := self._loop0_36())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_38(self) -> Optional[Any]:
        # _loop0_38: ',' expression
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.expression())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_37(self) -> Optional[Any]:
        # _gather_37: expression _loop0_38
        mark = self._mark()
        if (
            (elem := self.expression())
            is not None
            and
            (seq := self._loop0_38())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_40(self) -> Optional[Any]:
        # _loop0_40: ',' expression
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.expression())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_39(self) -> Optional[Any]:
        # _gather_39: expression _loop0_40
        mark = self._mark()
        if (
            (elem := self.expression())
            is not None
            and
            (seq := self._loop0_40())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_42(self) -> Optional[Any]:
        # _loop0_42: ',' expression
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.expression())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_41(self) -> Optional[Any]:
        # _gather_41: expression _loop0_42
        mark = self._mark()
        if (
            (elem := self.expression())
            is not None
            and
            (seq := self._loop0_42())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop1_43(self) -> Optional[Any]:
        # _loop1_43: statement
        mark = self._mark()
        children = []
        while (
            (statement := self.statement())
        ):
            children.append(statement)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_45(self) -> Optional[Any]:
        # _loop0_45: ';' simple_stmt
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(';'))
            and
            (elem := self.simple_stmt())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_44(self) -> Optional[Any]:
        # _gather_44: simple_stmt _loop0_45
        mark = self._mark()
        if (
            (elem := self.simple_stmt())
            is not None
            and
            (seq := self._loop0_45())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _tmp_46(self) -> Optional[Any]:
        # _tmp_46: 'import' | 'from'
        mark = self._mark()
        if (
            (literal := self.expect('import'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('from'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_47(self) -> Optional[Any]:
        # _tmp_47: 'def' | '@' | 'async'
        mark = self._mark()
        if (
            (literal := self.expect('def'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('@'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('async'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_48(self) -> Optional[Any]:
        # _tmp_48: 'class' | '@'
        mark = self._mark()
        if (
            (literal := self.expect('class'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('@'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_49(self) -> Optional[Any]:
        # _tmp_49: 'with' | 'async'
        mark = self._mark()
        if (
            (literal := self.expect('with'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('async'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_50(self) -> Optional[Any]:
        # _tmp_50: 'for' | 'async'
        mark = self._mark()
        if (
            (literal := self.expect('for'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('async'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_51(self) -> Optional[Any]:
        # _tmp_51: '=' annotated_rhs
        mark = self._mark()
        if (
            (literal := self.expect('='))
            and
            (d := self.annotated_rhs())
        ):
            return d
        self._reset(mark)
        return None

    @memoize
    def _tmp_52(self) -> Optional[Any]:
        # _tmp_52: '(' single_target ')' | single_subscript_attribute_target
        mark = self._mark()
        if (
            (literal := self.expect('('))
            and
            (b := self.single_target())
            and
            (literal_1 := self.expect(')'))
        ):
            return b
        self._reset(mark)
        if (
            (single_subscript_attribute_target := self.single_subscript_attribute_target())
        ):
            return single_subscript_attribute_target
        self._reset(mark)
        return None

    @memoize
    def _tmp_53(self) -> Optional[Any]:
        # _tmp_53: '=' annotated_rhs
        mark = self._mark()
        if (
            (literal := self.expect('='))
            and
            (d := self.annotated_rhs())
        ):
            return d
        self._reset(mark)
        return None

    @memoize
    def _loop1_54(self) -> Optional[Any]:
        # _loop1_54: (star_targets '=')
        mark = self._mark()
        children = []
        while (
            (_tmp_215 := self._tmp_215())
        ):
            children.append(_tmp_215)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _tmp_55(self) -> Optional[Any]:
        # _tmp_55: yield_expr | star_expressions
        mark = self._mark()
        if (
            (yield_expr := self.yield_expr())
        ):
            return yield_expr
        self._reset(mark)
        if (
            (star_expressions := self.star_expressions())
        ):
            return star_expressions
        self._reset(mark)
        return None

    @memoize
    def _tmp_56(self) -> Optional[Any]:
        # _tmp_56: yield_expr | star_expressions
        mark = self._mark()
        if (
            (yield_expr := self.yield_expr())
        ):
            return yield_expr
        self._reset(mark)
        if (
            (star_expressions := self.star_expressions())
        ):
            return star_expressions
        self._reset(mark)
        return None

    @memoize
    def _loop0_58(self) -> Optional[Any]:
        # _loop0_58: ',' NAME
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.name())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_57(self) -> Optional[Any]:
        # _gather_57: NAME _loop0_58
        mark = self._mark()
        if (
            (elem := self.name())
            is not None
            and
            (seq := self._loop0_58())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_60(self) -> Optional[Any]:
        # _loop0_60: ',' NAME
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.name())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_59(self) -> Optional[Any]:
        # _gather_59: NAME _loop0_60
        mark = self._mark()
        if (
            (elem := self.name())
            is not None
            and
            (seq := self._loop0_60())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _tmp_61(self) -> Optional[Any]:
        # _tmp_61: ',' expression
        mark = self._mark()
        if (
            (literal := self.expect(','))
            and
            (z := self.expression())
        ):
            return z
        self._reset(mark)
        return None

    @memoize
    def _tmp_62(self) -> Optional[Any]:
        # _tmp_62: ';' | NEWLINE
        mark = self._mark()
        if (
            (literal := self.expect(';'))
        ):
            return literal
        self._reset(mark)
        if (
            (_newline := self.expect('NEWLINE'))
        ):
            return _newline
        self._reset(mark)
        return None

    @memoize
    def _loop0_63(self) -> Optional[Any]:
        # _loop0_63: ('.' | '...')
        mark = self._mark()
        children = []
        while (
            (_tmp_216 := self._tmp_216())
        ):
            children.append(_tmp_216)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_64(self) -> Optional[Any]:
        # _loop1_64: ('.' | '...')
        mark = self._mark()
        children = []
        while (
            (_tmp_217 := self._tmp_217())
        ):
            children.append(_tmp_217)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_66(self) -> Optional[Any]:
        # _loop0_66: ',' import_from_as_name
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.import_from_as_name())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_65(self) -> Optional[Any]:
        # _gather_65: import_from_as_name _loop0_66
        mark = self._mark()
        if (
            (elem := self.import_from_as_name())
            is not None
            and
            (seq := self._loop0_66())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _tmp_67(self) -> Optional[Any]:
        # _tmp_67: 'as' NAME
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (z := self.name())
        ):
            return z . string
        self._reset(mark)
        return None

    @memoize
    def _loop0_69(self) -> Optional[Any]:
        # _loop0_69: ',' dotted_as_name
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.dotted_as_name())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_68(self) -> Optional[Any]:
        # _gather_68: dotted_as_name _loop0_69
        mark = self._mark()
        if (
            (elem := self.dotted_as_name())
            is not None
            and
            (seq := self._loop0_69())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _tmp_70(self) -> Optional[Any]:
        # _tmp_70: 'as' NAME
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (z := self.name())
        ):
            return z . string
        self._reset(mark)
        return None

    @memoize
    def _loop0_72(self) -> Optional[Any]:
        # _loop0_72: ',' with_item
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.with_item())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_71(self) -> Optional[Any]:
        # _gather_71: with_item _loop0_72
        mark = self._mark()
        if (
            (elem := self.with_item())
            is not None
            and
            (seq := self._loop0_72())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_74(self) -> Optional[Any]:
        # _loop0_74: ',' with_item
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.with_item())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_73(self) -> Optional[Any]:
        # _gather_73: with_item _loop0_74
        mark = self._mark()
        if (
            (elem := self.with_item())
            is not None
            and
            (seq := self._loop0_74())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_76(self) -> Optional[Any]:
        # _loop0_76: ',' with_item
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.with_item())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_75(self) -> Optional[Any]:
        # _gather_75: with_item _loop0_76
        mark = self._mark()
        if (
            (elem := self.with_item())
            is not None
            and
            (seq := self._loop0_76())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_78(self) -> Optional[Any]:
        # _loop0_78: ',' with_item
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.with_item())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_77(self) -> Optional[Any]:
        # _gather_77: with_item _loop0_78
        mark = self._mark()
        if (
            (elem := self.with_item())
            is not None
            and
            (seq := self._loop0_78())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _tmp_79(self) -> Optional[Any]:
        # _tmp_79: ',' | ')' | ':'
        mark = self._mark()
        if (
            (literal := self.expect(','))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect(')'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect(':'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _loop1_80(self) -> Optional[Any]:
        # _loop1_80: except_block
        mark = self._mark()
        children = []
        while (
            (except_block := self.except_block())
        ):
            children.append(except_block)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _tmp_81(self) -> Optional[Any]:
        # _tmp_81: 'as' NAME
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (z := self.name())
        ):
            return z . string
        self._reset(mark)
        return None

    @memoize
    def _loop1_82(self) -> Optional[Any]:
        # _loop1_82: case_block
        mark = self._mark()
        children = []
        while (
            (case_block := self.case_block())
        ):
            children.append(case_block)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_84(self) -> Optional[Any]:
        # _loop0_84: '|' closed_pattern
        mark = self._mark()
        children = []
        while (
            (literal := self.expect('|'))
            and
            (elem := self.closed_pattern())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_83(self) -> Optional[Any]:
        # _gather_83: closed_pattern _loop0_84
        mark = self._mark()
        if (
            (elem := self.closed_pattern())
            is not None
            and
            (seq := self._loop0_84())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _tmp_85(self) -> Optional[Any]:
        # _tmp_85: '+' | '-'
        mark = self._mark()
        if (
            (literal := self.expect('+'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('-'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_86(self) -> Optional[Any]:
        # _tmp_86: '+' | '-'
        mark = self._mark()
        if (
            (literal := self.expect('+'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('-'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_87(self) -> Optional[Any]:
        # _tmp_87: '.' | '(' | '='
        mark = self._mark()
        if (
            (literal := self.expect('.'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('('))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('='))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_88(self) -> Optional[Any]:
        # _tmp_88: '.' | '(' | '='
        mark = self._mark()
        if (
            (literal := self.expect('.'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('('))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('='))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _loop0_90(self) -> Optional[Any]:
        # _loop0_90: ',' maybe_star_pattern
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.maybe_star_pattern())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_89(self) -> Optional[Any]:
        # _gather_89: maybe_star_pattern _loop0_90
        mark = self._mark()
        if (
            (elem := self.maybe_star_pattern())
            is not None
            and
            (seq := self._loop0_90())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_92(self) -> Optional[Any]:
        # _loop0_92: ',' key_value_pattern
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.key_value_pattern())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_91(self) -> Optional[Any]:
        # _gather_91: key_value_pattern _loop0_92
        mark = self._mark()
        if (
            (elem := self.key_value_pattern())
            is not None
            and
            (seq := self._loop0_92())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _tmp_93(self) -> Optional[Any]:
        # _tmp_93: literal_expr | attr
        mark = self._mark()
        if (
            (literal_expr := self.literal_expr())
        ):
            return literal_expr
        self._reset(mark)
        if (
            (attr := self.attr())
        ):
            return attr
        self._reset(mark)
        return None

    @memoize
    def _loop0_95(self) -> Optional[Any]:
        # _loop0_95: ',' pattern
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.pattern())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_94(self) -> Optional[Any]:
        # _gather_94: pattern _loop0_95
        mark = self._mark()
        if (
            (elem := self.pattern())
            is not None
            and
            (seq := self._loop0_95())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_97(self) -> Optional[Any]:
        # _loop0_97: ',' keyword_pattern
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.keyword_pattern())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_96(self) -> Optional[Any]:
        # _gather_96: keyword_pattern _loop0_97
        mark = self._mark()
        if (
            (elem := self.keyword_pattern())
            is not None
            and
            (seq := self._loop0_97())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _tmp_98(self) -> Optional[Any]:
        # _tmp_98: 'from' expression
        mark = self._mark()
        if (
            (literal := self.expect('from'))
            and
            (z := self.expression())
        ):
            return z
        self._reset(mark)
        return None

    @memoize
    def _tmp_99(self) -> Optional[Any]:
        # _tmp_99: '->' expression
        mark = self._mark()
        if (
            (literal := self.expect('->'))
            and
            (z := self.expression())
        ):
            return z
        self._reset(mark)
        return None

    @memoize
    def _tmp_100(self) -> Optional[Any]:
        # _tmp_100: '->' expression
        mark = self._mark()
        if (
            (literal := self.expect('->'))
            and
            (z := self.expression())
        ):
            return z
        self._reset(mark)
        return None

    @memoize
    def _tmp_101(self) -> Optional[Any]:
        # _tmp_101: NEWLINE INDENT
        mark = self._mark()
        if (
            (_newline := self.expect('NEWLINE'))
            and
            (_indent := self.expect('INDENT'))
        ):
            return [_newline, _indent]
        self._reset(mark)
        return None

    @memoize
    def _loop0_102(self) -> Optional[Any]:
        # _loop0_102: param_no_default
        mark = self._mark()
        children = []
        while (
            (param_no_default := self.param_no_default())
        ):
            children.append(param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_103(self) -> Optional[Any]:
        # _loop0_103: param_with_default
        mark = self._mark()
        children = []
        while (
            (param_with_default := self.param_with_default())
        ):
            children.append(param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_104(self) -> Optional[Any]:
        # _loop0_104: param_with_default
        mark = self._mark()
        children = []
        while (
            (param_with_default := self.param_with_default())
        ):
            children.append(param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_105(self) -> Optional[Any]:
        # _loop1_105: param_no_default
        mark = self._mark()
        children = []
        while (
            (param_no_default := self.param_no_default())
        ):
            children.append(param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_106(self) -> Optional[Any]:
        # _loop0_106: param_with_default
        mark = self._mark()
        children = []
        while (
            (param_with_default := self.param_with_default())
        ):
            children.append(param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_107(self) -> Optional[Any]:
        # _loop1_107: param_with_default
        mark = self._mark()
        children = []
        while (
            (param_with_default := self.param_with_default())
        ):
            children.append(param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_108(self) -> Optional[Any]:
        # _loop1_108: param_no_default
        mark = self._mark()
        children = []
        while (
            (param_no_default := self.param_no_default())
        ):
            children.append(param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_109(self) -> Optional[Any]:
        # _loop1_109: param_no_default
        mark = self._mark()
        children = []
        while (
            (param_no_default := self.param_no_default())
        ):
            children.append(param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_110(self) -> Optional[Any]:
        # _loop0_110: param_no_default
        mark = self._mark()
        children = []
        while (
            (param_no_default := self.param_no_default())
        ):
            children.append(param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_111(self) -> Optional[Any]:
        # _loop1_111: param_with_default
        mark = self._mark()
        children = []
        while (
            (param_with_default := self.param_with_default())
        ):
            children.append(param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_112(self) -> Optional[Any]:
        # _loop0_112: param_no_default
        mark = self._mark()
        children = []
        while (
            (param_no_default := self.param_no_default())
        ):
            children.append(param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_113(self) -> Optional[Any]:
        # _loop1_113: param_with_default
        mark = self._mark()
        children = []
        while (
            (param_with_default := self.param_with_default())
        ):
            children.append(param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_114(self) -> Optional[Any]:
        # _loop0_114: param_maybe_default
        mark = self._mark()
        children = []
        while (
            (param_maybe_default := self.param_maybe_default())
        ):
            children.append(param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_115(self) -> Optional[Any]:
        # _loop1_115: param_maybe_default
        mark = self._mark()
        children = []
        while (
            (param_maybe_default := self.param_maybe_default())
        ):
            children.append(param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_116(self) -> Optional[Any]:
        # _loop1_116: decorator
        mark = self._mark()
        children = []
        while (
            (decorator := self.decorator())
        ):
            children.append(decorator)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _tmp_117(self) -> Optional[Any]:
        # _tmp_117: '@' dec_maybe_call NEWLINE
        mark = self._mark()
        if (
            (literal := self.expect('@'))
            and
            (f := self.dec_maybe_call())
            and
            (_newline := self.expect('NEWLINE'))
        ):
            return f
        self._reset(mark)
        return None

    @memoize
    def _tmp_118(self) -> Optional[Any]:
        # _tmp_118: '@' named_expression NEWLINE
        mark = self._mark()
        if (
            (literal := self.expect('@'))
            and
            (f := self.named_expression())
            and
            (_newline := self.expect('NEWLINE'))
        ):
            return f
        self._reset(mark)
        return None

    @memoize
    def _tmp_119(self) -> Optional[Any]:
        # _tmp_119: '(' arguments? ')'
        mark = self._mark()
        if (
            (literal := self.expect('('))
            and
            (z := self.arguments(),)
            and
            (literal_1 := self.expect(')'))
        ):
            return z
        self._reset(mark)
        return None

    @memoize
    def _loop1_120(self) -> Optional[Any]:
        # _loop1_120: (',' star_expression)
        mark = self._mark()
        children = []
        while (
            (_tmp_218 := self._tmp_218())
        ):
            children.append(_tmp_218)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_122(self) -> Optional[Any]:
        # _loop0_122: ',' star_named_expression
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.star_named_expression())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_121(self) -> Optional[Any]:
        # _gather_121: star_named_expression _loop0_122
        mark = self._mark()
        if (
            (elem := self.star_named_expression())
            is not None
            and
            (seq := self._loop0_122())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop1_123(self) -> Optional[Any]:
        # _loop1_123: (',' expression)
        mark = self._mark()
        children = []
        while (
            (_tmp_219 := self._tmp_219())
        ):
            children.append(_tmp_219)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_124(self) -> Optional[Any]:
        # _loop0_124: lambda_param_no_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_no_default := self.lambda_param_no_default())
        ):
            children.append(lambda_param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_125(self) -> Optional[Any]:
        # _loop0_125: lambda_param_with_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_with_default := self.lambda_param_with_default())
        ):
            children.append(lambda_param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_126(self) -> Optional[Any]:
        # _loop0_126: lambda_param_with_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_with_default := self.lambda_param_with_default())
        ):
            children.append(lambda_param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_127(self) -> Optional[Any]:
        # _loop1_127: lambda_param_no_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_no_default := self.lambda_param_no_default())
        ):
            children.append(lambda_param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_128(self) -> Optional[Any]:
        # _loop0_128: lambda_param_with_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_with_default := self.lambda_param_with_default())
        ):
            children.append(lambda_param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_129(self) -> Optional[Any]:
        # _loop1_129: lambda_param_with_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_with_default := self.lambda_param_with_default())
        ):
            children.append(lambda_param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_130(self) -> Optional[Any]:
        # _loop1_130: lambda_param_no_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_no_default := self.lambda_param_no_default())
        ):
            children.append(lambda_param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_131(self) -> Optional[Any]:
        # _loop1_131: lambda_param_no_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_no_default := self.lambda_param_no_default())
        ):
            children.append(lambda_param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_132(self) -> Optional[Any]:
        # _loop0_132: lambda_param_no_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_no_default := self.lambda_param_no_default())
        ):
            children.append(lambda_param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_133(self) -> Optional[Any]:
        # _loop1_133: lambda_param_with_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_with_default := self.lambda_param_with_default())
        ):
            children.append(lambda_param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_134(self) -> Optional[Any]:
        # _loop0_134: lambda_param_no_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_no_default := self.lambda_param_no_default())
        ):
            children.append(lambda_param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_135(self) -> Optional[Any]:
        # _loop1_135: lambda_param_with_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_with_default := self.lambda_param_with_default())
        ):
            children.append(lambda_param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_136(self) -> Optional[Any]:
        # _loop0_136: lambda_param_maybe_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_maybe_default := self.lambda_param_maybe_default())
        ):
            children.append(lambda_param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_137(self) -> Optional[Any]:
        # _loop1_137: lambda_param_maybe_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_maybe_default := self.lambda_param_maybe_default())
        ):
            children.append(lambda_param_maybe_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_138(self) -> Optional[Any]:
        # _loop1_138: ('or' conjunction)
        mark = self._mark()
        children = []
        while (
            (_tmp_220 := self._tmp_220())
        ):
            children.append(_tmp_220)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_139(self) -> Optional[Any]:
        # _loop1_139: ('and' inversion)
        mark = self._mark()
        children = []
        while (
            (_tmp_221 := self._tmp_221())
        ):
            children.append(_tmp_221)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_140(self) -> Optional[Any]:
        # _loop1_140: compare_op_bitwise_or_pair
        mark = self._mark()
        children = []
        while (
            (compare_op_bitwise_or_pair := self.compare_op_bitwise_or_pair())
        ):
            children.append(compare_op_bitwise_or_pair)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_142(self) -> Optional[Any]:
        # _loop0_142: ',' slice
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.slice())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_141(self) -> Optional[Any]:
        # _gather_141: slice _loop0_142
        mark = self._mark()
        if (
            (elem := self.slice())
            is not None
            and
            (seq := self._loop0_142())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _tmp_143(self) -> Optional[Any]:
        # _tmp_143: ':' expression?
        mark = self._mark()
        if (
            (literal := self.expect(':'))
            and
            (d := self.expression(),)
        ):
            return d
        self._reset(mark)
        return None

    @memoize
    def _tmp_144(self) -> Optional[Any]:
        # _tmp_144: tuple | group | genexp
        mark = self._mark()
        if (
            (tuple := self.tuple())
        ):
            return tuple
        self._reset(mark)
        if (
            (group := self.group())
        ):
            return group
        self._reset(mark)
        if (
            (genexp := self.genexp())
        ):
            return genexp
        self._reset(mark)
        return None

    @memoize
    def _tmp_145(self) -> Optional[Any]:
        # _tmp_145: list | listcomp
        mark = self._mark()
        if (
            (list := self.list())
        ):
            return list
        self._reset(mark)
        if (
            (listcomp := self.listcomp())
        ):
            return listcomp
        self._reset(mark)
        return None

    @memoize
    def _tmp_146(self) -> Optional[Any]:
        # _tmp_146: dict | set | dictcomp | setcomp
        mark = self._mark()
        if (
            (dict := self.dict())
        ):
            return dict
        self._reset(mark)
        if (
            (set := self.set())
        ):
            return set
        self._reset(mark)
        if (
            (dictcomp := self.dictcomp())
        ):
            return dictcomp
        self._reset(mark)
        if (
            (setcomp := self.setcomp())
        ):
            return setcomp
        self._reset(mark)
        return None

    @memoize
    def _loop1_147(self) -> Optional[Any]:
        # _loop1_147: STRING
        mark = self._mark()
        children = []
        while (
            (string := self.string())
        ):
            children.append(string)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _tmp_148(self) -> Optional[Any]:
        # _tmp_148: star_named_expression ',' star_named_expressions?
        mark = self._mark()
        if (
            (y := self.star_named_expression())
            and
            (literal := self.expect(','))
            and
            (z := self.star_named_expressions(),)
        ):
            return [y] + ( z or [] )
        self._reset(mark)
        return None

    @memoize
    def _tmp_149(self) -> Optional[Any]:
        # _tmp_149: yield_expr | named_expression
        mark = self._mark()
        if (
            (yield_expr := self.yield_expr())
        ):
            return yield_expr
        self._reset(mark)
        if (
            (named_expression := self.named_expression())
        ):
            return named_expression
        self._reset(mark)
        return None

    @memoize
    def _tmp_150(self) -> Optional[Any]:
        # _tmp_150: assignment_expression | expression !':='
        mark = self._mark()
        if (
            (assignment_expression := self.assignment_expression())
        ):
            return assignment_expression
        self._reset(mark)
        if (
            (expression := self.expression())
            and
            self.negative_lookahead(self.expect, ':=')
        ):
            return expression
        self._reset(mark)
        return None

    @memoize
    def _loop0_152(self) -> Optional[Any]:
        # _loop0_152: ',' double_starred_kvpair
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.double_starred_kvpair())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_151(self) -> Optional[Any]:
        # _gather_151: double_starred_kvpair _loop0_152
        mark = self._mark()
        if (
            (elem := self.double_starred_kvpair())
            is not None
            and
            (seq := self._loop0_152())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop1_153(self) -> Optional[Any]:
        # _loop1_153: for_if_clause
        mark = self._mark()
        children = []
        while (
            (for_if_clause := self.for_if_clause())
        ):
            children.append(for_if_clause)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_154(self) -> Optional[Any]:
        # _loop0_154: ('if' disjunction)
        mark = self._mark()
        children = []
        while (
            (_tmp_222 := self._tmp_222())
        ):
            children.append(_tmp_222)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_155(self) -> Optional[Any]:
        # _loop0_155: ('if' disjunction)
        mark = self._mark()
        children = []
        while (
            (_tmp_223 := self._tmp_223())
        ):
            children.append(_tmp_223)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_157(self) -> Optional[Any]:
        # _loop0_157: ',' (starred_expression | (assignment_expression | expression !':=') !'=')
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self._tmp_224())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_156(self) -> Optional[Any]:
        # _gather_156: (starred_expression | (assignment_expression | expression !':=') !'=') _loop0_157
        mark = self._mark()
        if (
            (elem := self._tmp_224())
            is not None
            and
            (seq := self._loop0_157())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _tmp_158(self) -> Optional[Any]:
        # _tmp_158: ',' kwargs
        mark = self._mark()
        if (
            (literal := self.expect(','))
            and
            (k := self.kwargs())
        ):
            return k
        self._reset(mark)
        return None

    @memoize
    def _loop0_160(self) -> Optional[Any]:
        # _loop0_160: ',' kwarg_or_starred
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.kwarg_or_starred())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_159(self) -> Optional[Any]:
        # _gather_159: kwarg_or_starred _loop0_160
        mark = self._mark()
        if (
            (elem := self.kwarg_or_starred())
            is not None
            and
            (seq := self._loop0_160())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_162(self) -> Optional[Any]:
        # _loop0_162: ',' kwarg_or_double_starred
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.kwarg_or_double_starred())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_161(self) -> Optional[Any]:
        # _gather_161: kwarg_or_double_starred _loop0_162
        mark = self._mark()
        if (
            (elem := self.kwarg_or_double_starred())
            is not None
            and
            (seq := self._loop0_162())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_164(self) -> Optional[Any]:
        # _loop0_164: ',' kwarg_or_starred
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.kwarg_or_starred())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_163(self) -> Optional[Any]:
        # _gather_163: kwarg_or_starred _loop0_164
        mark = self._mark()
        if (
            (elem := self.kwarg_or_starred())
            is not None
            and
            (seq := self._loop0_164())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_166(self) -> Optional[Any]:
        # _loop0_166: ',' kwarg_or_double_starred
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.kwarg_or_double_starred())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_165(self) -> Optional[Any]:
        # _gather_165: kwarg_or_double_starred _loop0_166
        mark = self._mark()
        if (
            (elem := self.kwarg_or_double_starred())
            is not None
            and
            (seq := self._loop0_166())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_167(self) -> Optional[Any]:
        # _loop0_167: (',' star_target)
        mark = self._mark()
        children = []
        while (
            (_tmp_225 := self._tmp_225())
        ):
            children.append(_tmp_225)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_169(self) -> Optional[Any]:
        # _loop0_169: ',' star_target
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.star_target())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_168(self) -> Optional[Any]:
        # _gather_168: star_target _loop0_169
        mark = self._mark()
        if (
            (elem := self.star_target())
            is not None
            and
            (seq := self._loop0_169())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop1_170(self) -> Optional[Any]:
        # _loop1_170: (',' star_target)
        mark = self._mark()
        children = []
        while (
            (_tmp_226 := self._tmp_226())
        ):
            children.append(_tmp_226)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _tmp_171(self) -> Optional[Any]:
        # _tmp_171: !'*' star_target
        mark = self._mark()
        if (
            self.negative_lookahead(self.expect, '*')
            and
            (star_target := self.star_target())
        ):
            return star_target
        self._reset(mark)
        return None

    @memoize
    def _loop0_173(self) -> Optional[Any]:
        # _loop0_173: ',' del_target
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.del_target())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_172(self) -> Optional[Any]:
        # _gather_172: del_target _loop0_173
        mark = self._mark()
        if (
            (elem := self.del_target())
            is not None
            and
            (seq := self._loop0_173())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _tmp_174(self) -> Optional[Any]:
        # _tmp_174: args | expression for_if_clauses
        mark = self._mark()
        if (
            (args := self.args())
        ):
            return args
        self._reset(mark)
        if (
            (expression := self.expression())
            and
            (for_if_clauses := self.for_if_clauses())
        ):
            return [expression, for_if_clauses]
        self._reset(mark)
        return None

    @memoize
    def _tmp_175(self) -> Optional[Any]:
        # _tmp_175: NAME '='
        mark = self._mark()
        if (
            (name := self.name())
            and
            (literal := self.expect('='))
        ):
            return [name, literal]
        self._reset(mark)
        return None

    @memoize
    def _tmp_176(self) -> Optional[Any]:
        # _tmp_176: NAME STRING | SOFT_KEYWORD
        mark = self._mark()
        if (
            (name := self.name())
            and
            (string := self.string())
        ):
            return [name, string]
        self._reset(mark)
        if (
            (soft_keyword := self.soft_keyword())
        ):
            return soft_keyword
        self._reset(mark)
        return None

    @memoize
    def _tmp_177(self) -> Optional[Any]:
        # _tmp_177: '=' | ':='
        mark = self._mark()
        if (
            (literal := self.expect('='))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect(':='))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_178(self) -> Optional[Any]:
        # _tmp_178: list | tuple | genexp | 'True' | 'None' | 'False'
        mark = self._mark()
        if (
            (list := self.list())
        ):
            return list
        self._reset(mark)
        if (
            (tuple := self.tuple())
        ):
            return tuple
        self._reset(mark)
        if (
            (genexp := self.genexp())
        ):
            return genexp
        self._reset(mark)
        if (
            (literal := self.expect('True'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('None'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('False'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_179(self) -> Optional[Any]:
        # _tmp_179: '=' | ':='
        mark = self._mark()
        if (
            (literal := self.expect('='))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect(':='))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _loop0_180(self) -> Optional[Any]:
        # _loop0_180: star_named_expressions
        mark = self._mark()
        children = []
        while (
            (star_named_expressions := self.star_named_expressions())
        ):
            children.append(star_named_expressions)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_181(self) -> Optional[Any]:
        # _loop0_181: (star_targets '=')
        mark = self._mark()
        children = []
        while (
            (_tmp_227 := self._tmp_227())
        ):
            children.append(_tmp_227)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_182(self) -> Optional[Any]:
        # _loop0_182: (star_targets '=')
        mark = self._mark()
        children = []
        while (
            (_tmp_228 := self._tmp_228())
        ):
            children.append(_tmp_228)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _tmp_183(self) -> Optional[Any]:
        # _tmp_183: yield_expr | star_expressions
        mark = self._mark()
        if (
            (yield_expr := self.yield_expr())
        ):
            return yield_expr
        self._reset(mark)
        if (
            (star_expressions := self.star_expressions())
        ):
            return star_expressions
        self._reset(mark)
        return None

    @memoize
    def _tmp_184(self) -> Optional[Any]:
        # _tmp_184: '[' | '(' | '{'
        mark = self._mark()
        if (
            (literal := self.expect('['))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('('))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('{'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_185(self) -> Optional[Any]:
        # _tmp_185: '[' | '{'
        mark = self._mark()
        if (
            (literal := self.expect('['))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('{'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_186(self) -> Optional[Any]:
        # _tmp_186: '[' | '{'
        mark = self._mark()
        if (
            (literal := self.expect('['))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('{'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _loop0_187(self) -> Optional[Any]:
        # _loop0_187: param_no_default
        mark = self._mark()
        children = []
        while (
            (param_no_default := self.param_no_default())
        ):
            children.append(param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_188(self) -> Optional[Any]:
        # _loop1_188: param_with_default
        mark = self._mark()
        children = []
        while (
            (param_with_default := self.param_with_default())
        ):
            children.append(param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop0_189(self) -> Optional[Any]:
        # _loop0_189: lambda_param_no_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_no_default := self.lambda_param_no_default())
        ):
            children.append(lambda_param_no_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _loop1_190(self) -> Optional[Any]:
        # _loop1_190: lambda_param_with_default
        mark = self._mark()
        children = []
        while (
            (lambda_param_with_default := self.lambda_param_with_default())
        ):
            children.append(lambda_param_with_default)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _tmp_191(self) -> Optional[Any]:
        # _tmp_191: ')' | ',' (')' | '**')
        mark = self._mark()
        if (
            (literal := self.expect(')'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect(','))
            and
            (_tmp_229 := self._tmp_229())
        ):
            return [literal, _tmp_229]
        self._reset(mark)
        return None

    @memoize
    def _tmp_192(self) -> Optional[Any]:
        # _tmp_192: ':' | ',' (':' | '**')
        mark = self._mark()
        if (
            (literal := self.expect(':'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect(','))
            and
            (_tmp_230 := self._tmp_230())
        ):
            return [literal, _tmp_230]
        self._reset(mark)
        return None

    @memoize
    def _tmp_193(self) -> Optional[Any]:
        # _tmp_193: ',' | ')' | ':'
        mark = self._mark()
        if (
            (literal := self.expect(','))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect(')'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect(':'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _loop0_195(self) -> Optional[Any]:
        # _loop0_195: ',' (expression ['as' star_target])
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self._tmp_231())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_194(self) -> Optional[Any]:
        # _gather_194: (expression ['as' star_target]) _loop0_195
        mark = self._mark()
        if (
            (elem := self._tmp_231())
            is not None
            and
            (seq := self._loop0_195())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_197(self) -> Optional[Any]:
        # _loop0_197: ',' (expressions ['as' star_target])
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self._tmp_232())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_196(self) -> Optional[Any]:
        # _gather_196: (expressions ['as' star_target]) _loop0_197
        mark = self._mark()
        if (
            (elem := self._tmp_232())
            is not None
            and
            (seq := self._loop0_197())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_199(self) -> Optional[Any]:
        # _loop0_199: ',' (expression ['as' star_target])
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self._tmp_233())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_198(self) -> Optional[Any]:
        # _gather_198: (expression ['as' star_target]) _loop0_199
        mark = self._mark()
        if (
            (elem := self._tmp_233())
            is not None
            and
            (seq := self._loop0_199())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_201(self) -> Optional[Any]:
        # _loop0_201: ',' (expressions ['as' star_target])
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self._tmp_234())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_200(self) -> Optional[Any]:
        # _gather_200: (expressions ['as' star_target]) _loop0_201
        mark = self._mark()
        if (
            (elem := self._tmp_234())
            is not None
            and
            (seq := self._loop0_201())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _tmp_202(self) -> Optional[Any]:
        # _tmp_202: 'except' | 'finally'
        mark = self._mark()
        if (
            (literal := self.expect('except'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('finally'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_203(self) -> Optional[Any]:
        # _tmp_203: 'as' NAME
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (name := self.name())
        ):
            return [literal, name]
        self._reset(mark)
        return None

    @memoize
    def _tmp_204(self) -> Optional[Any]:
        # _tmp_204: 'as' NAME
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (name := self.name())
        ):
            return [literal, name]
        self._reset(mark)
        return None

    @memoize
    def _tmp_205(self) -> Optional[Any]:
        # _tmp_205: 'as' NAME
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (name := self.name())
        ):
            return [literal, name]
        self._reset(mark)
        return None

    @memoize
    def _tmp_206(self) -> Optional[Any]:
        # _tmp_206: '->' expression
        mark = self._mark()
        if (
            (literal := self.expect('->'))
            and
            (expression := self.expression())
        ):
            return [literal, expression]
        self._reset(mark)
        return None

    @memoize
    def _tmp_207(self) -> Optional[Any]:
        # _tmp_207: '(' arguments? ')'
        mark = self._mark()
        if (
            (literal := self.expect('('))
            and
            (opt := self.arguments(),)
            and
            (literal_1 := self.expect(')'))
        ):
            return [literal, opt, literal_1]
        self._reset(mark)
        return None

    @memoize
    def _loop0_209(self) -> Optional[Any]:
        # _loop0_209: ',' double_starred_kvpair
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.double_starred_kvpair())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_208(self) -> Optional[Any]:
        # _gather_208: double_starred_kvpair _loop0_209
        mark = self._mark()
        if (
            (elem := self.double_starred_kvpair())
            is not None
            and
            (seq := self._loop0_209())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _tmp_210(self) -> Optional[Any]:
        # _tmp_210: '}' | ','
        mark = self._mark()
        if (
            (literal := self.expect('}'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect(','))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _loop0_212(self) -> Optional[Any]:
        # _loop0_212: ',' pragma_arg
        mark = self._mark()
        children = []
        while (
            (literal := self.expect(','))
            and
            (elem := self.pragma_arg())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_211(self) -> Optional[Any]:
        # _gather_211: pragma_arg _loop0_212
        mark = self._mark()
        if (
            (elem := self.pragma_arg())
            is not None
            and
            (seq := self._loop0_212())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _loop0_214(self) -> Optional[Any]:
        # _loop0_214: '.' NAME
        mark = self._mark()
        children = []
        while (
            (literal := self.expect('.'))
            and
            (elem := self.name())
        ):
            children.append(elem)
            mark = self._mark()
        self._reset(mark)
        return children

    @memoize
    def _gather_213(self) -> Optional[Any]:
        # _gather_213: NAME _loop0_214
        mark = self._mark()
        if (
            (elem := self.name())
            is not None
            and
            (seq := self._loop0_214())
            is not None
        ):
            return [elem] + seq
        self._reset(mark)
        return None

    @memoize
    def _tmp_215(self) -> Optional[Any]:
        # _tmp_215: star_targets '='
        mark = self._mark()
        if (
            (z := self.star_targets())
            and
            (literal := self.expect('='))
        ):
            return z
        self._reset(mark)
        return None

    @memoize
    def _tmp_216(self) -> Optional[Any]:
        # _tmp_216: '.' | '...'
        mark = self._mark()
        if (
            (literal := self.expect('.'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('...'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_217(self) -> Optional[Any]:
        # _tmp_217: '.' | '...'
        mark = self._mark()
        if (
            (literal := self.expect('.'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('...'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_218(self) -> Optional[Any]:
        # _tmp_218: ',' star_expression
        mark = self._mark()
        if (
            (literal := self.expect(','))
            and
            (c := self.star_expression())
        ):
            return c
        self._reset(mark)
        return None

    @memoize
    def _tmp_219(self) -> Optional[Any]:
        # _tmp_219: ',' expression
        mark = self._mark()
        if (
            (literal := self.expect(','))
            and
            (c := self.expression())
        ):
            return c
        self._reset(mark)
        return None

    @memoize
    def _tmp_220(self) -> Optional[Any]:
        # _tmp_220: 'or' conjunction
        mark = self._mark()
        if (
            (literal := self.expect('or'))
            and
            (c := self.conjunction())
        ):
            return c
        self._reset(mark)
        return None

    @memoize
    def _tmp_221(self) -> Optional[Any]:
        # _tmp_221: 'and' inversion
        mark = self._mark()
        if (
            (literal := self.expect('and'))
            and
            (c := self.inversion())
        ):
            return c
        self._reset(mark)
        return None

    @memoize
    def _tmp_222(self) -> Optional[Any]:
        # _tmp_222: 'if' disjunction
        mark = self._mark()
        if (
            (literal := self.expect('if'))
            and
            (z := self.disjunction())
        ):
            return z
        self._reset(mark)
        return None

    @memoize
    def _tmp_223(self) -> Optional[Any]:
        # _tmp_223: 'if' disjunction
        mark = self._mark()
        if (
            (literal := self.expect('if'))
            and
            (z := self.disjunction())
        ):
            return z
        self._reset(mark)
        return None

    @memoize
    def _tmp_224(self) -> Optional[Any]:
        # _tmp_224: starred_expression | (assignment_expression | expression !':=') !'='
        mark = self._mark()
        if (
            (starred_expression := self.starred_expression())
        ):
            return starred_expression
        self._reset(mark)
        if (
            (_tmp_235 := self._tmp_235())
            and
            self.negative_lookahead(self.expect, '=')
        ):
            return _tmp_235
        self._reset(mark)
        return None

    @memoize
    def _tmp_225(self) -> Optional[Any]:
        # _tmp_225: ',' star_target
        mark = self._mark()
        if (
            (literal := self.expect(','))
            and
            (c := self.star_target())
        ):
            return c
        self._reset(mark)
        return None

    @memoize
    def _tmp_226(self) -> Optional[Any]:
        # _tmp_226: ',' star_target
        mark = self._mark()
        if (
            (literal := self.expect(','))
            and
            (c := self.star_target())
        ):
            return c
        self._reset(mark)
        return None

    @memoize
    def _tmp_227(self) -> Optional[Any]:
        # _tmp_227: star_targets '='
        mark = self._mark()
        if (
            (star_targets := self.star_targets())
            and
            (literal := self.expect('='))
        ):
            return [star_targets, literal]
        self._reset(mark)
        return None

    @memoize
    def _tmp_228(self) -> Optional[Any]:
        # _tmp_228: star_targets '='
        mark = self._mark()
        if (
            (star_targets := self.star_targets())
            and
            (literal := self.expect('='))
        ):
            return [star_targets, literal]
        self._reset(mark)
        return None

    @memoize
    def _tmp_229(self) -> Optional[Any]:
        # _tmp_229: ')' | '**'
        mark = self._mark()
        if (
            (literal := self.expect(')'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('**'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_230(self) -> Optional[Any]:
        # _tmp_230: ':' | '**'
        mark = self._mark()
        if (
            (literal := self.expect(':'))
        ):
            return literal
        self._reset(mark)
        if (
            (literal := self.expect('**'))
        ):
            return literal
        self._reset(mark)
        return None

    @memoize
    def _tmp_231(self) -> Optional[Any]:
        # _tmp_231: expression ['as' star_target]
        mark = self._mark()
        if (
            (expression := self.expression())
            and
            (opt := self._tmp_236(),)
        ):
            return [expression, opt]
        self._reset(mark)
        return None

    @memoize
    def _tmp_232(self) -> Optional[Any]:
        # _tmp_232: expressions ['as' star_target]
        mark = self._mark()
        if (
            (expressions := self.expressions())
            and
            (opt := self._tmp_237(),)
        ):
            return [expressions, opt]
        self._reset(mark)
        return None

    @memoize
    def _tmp_233(self) -> Optional[Any]:
        # _tmp_233: expression ['as' star_target]
        mark = self._mark()
        if (
            (expression := self.expression())
            and
            (opt := self._tmp_238(),)
        ):
            return [expression, opt]
        self._reset(mark)
        return None

    @memoize
    def _tmp_234(self) -> Optional[Any]:
        # _tmp_234: expressions ['as' star_target]
        mark = self._mark()
        if (
            (expressions := self.expressions())
            and
            (opt := self._tmp_239(),)
        ):
            return [expressions, opt]
        self._reset(mark)
        return None

    @memoize
    def _tmp_235(self) -> Optional[Any]:
        # _tmp_235: assignment_expression | expression !':='
        mark = self._mark()
        if (
            (assignment_expression := self.assignment_expression())
        ):
            return assignment_expression
        self._reset(mark)
        if (
            (expression := self.expression())
            and
            self.negative_lookahead(self.expect, ':=')
        ):
            return expression
        self._reset(mark)
        return None

    @memoize
    def _tmp_236(self) -> Optional[Any]:
        # _tmp_236: 'as' star_target
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (star_target := self.star_target())
        ):
            return [literal, star_target]
        self._reset(mark)
        return None

    @memoize
    def _tmp_237(self) -> Optional[Any]:
        # _tmp_237: 'as' star_target
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (star_target := self.star_target())
        ):
            return [literal, star_target]
        self._reset(mark)
        return None

    @memoize
    def _tmp_238(self) -> Optional[Any]:
        # _tmp_238: 'as' star_target
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (star_target := self.star_target())
        ):
            return [literal, star_target]
        self._reset(mark)
        return None

    @memoize
    def _tmp_239(self) -> Optional[Any]:
        # _tmp_239: 'as' star_target
        mark = self._mark()
        if (
            (literal := self.expect('as'))
            and
            (star_target := self.star_target())
        ):
            return [literal, star_target]
        self._reset(mark)
        return None

    KEYWORDS = ('as', 'lambda', 'continue', 'def', 'and', 'finally', 'global', 'async', 'try', 'for', 'if', 'or', 'return', 'del', 'elif', 'else', 'assert', 'except', 'import', 'yield', 'break', 'await', 'True', 'from', 'pass', 'in', 'while', 'with', 'not', 'raise', 'False', 'None', 'nonlocal', 'is', 'class')
    SOFT_KEYWORDS = ('enamldef', 'template', 'const', 'func', 'attr', 'pragma', 'alias', 'case', '_', 'event', 'match')


if __name__ == '__main__':
    from pegen.parser import simple_parser_main
    simple_parser_main(EnamlParser)
